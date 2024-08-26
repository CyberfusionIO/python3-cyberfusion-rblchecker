from typing import Generator

import pytest
from _pytest.capture import CaptureFixture
from pytest_mock import MockerFixture

from cyberfusion.RBLChecker import checkers
from cyberfusion.RBLChecker import CLI
from cyberfusion.RBLChecker.utilities import (
    get_ip_addresses_in_ip_network,
    get_ip_addresses_in_range,
)
from tests.conftest import SNDSListings


def test_cli_get_args(mocker: MockerFixture):
    mocker.resetall()

    with pytest.raises(SystemExit):
        CLI.get_args()


# SNDS


def test_cli_snds_listed(
    capsys: CaptureFixture, snds_mock_listed: SNDSListings, cli_config: None
) -> None:
    with pytest.raises(SystemExit) as e:
        CLI.main()

    assert e.value.code == 1

    output = capsys.readouterr().out.splitlines()

    for listing in snds_mock_listed:
        start_range, end_range, blocked, reason = listing

        for ip_address in get_ip_addresses_in_range(str(start_range), str(end_range)):
            assert (
                f"(SNDS) IP address {ip_address} is listed on SNDS (reason: '{reason}')"
                in output
            )


def test_cli_snds_unlisted(
    capsys: CaptureFixture, snds_mock_unlisted: None, cli_config: None
) -> None:
    with pytest.raises(SystemExit):
        CLI.main()

    assert not any(
        line.startswith("SNDS") for line in capsys.readouterr().out.splitlines()
    )


# DNS


def test_cli_dns_listed(
    capsys: CaptureFixture,
    dns_mock_listed: None,
    config_mock: Generator[dict, None, None],
    snds_mock_unlisted: None,
    cli_config: None,
) -> None:
    with pytest.raises(SystemExit) as e:
        CLI.main()

    assert e.value.code == 1

    output = capsys.readouterr().out.splitlines()

    # Get IP addresses

    ip_addresses = []

    for ip_network in config_mock["ip_networks"]:
        ip_addresses.extend(get_ip_addresses_in_ip_network(ip_network))

    # Test output

    assert len(output) >= len(ip_addresses)

    for ip_address in ip_addresses:
        for host in config_mock["checkers"]["dns"]["hosts"]:
            _, query_name, query_result = checkers.DNSChecker(ip_address, host).check()

            assert (
                f"(DNS) IP address {ip_address} is listed on {host} ({query_name} -> {query_result})"
                in output
            )


def test_cli_dns_unlisted(
    capsys: CaptureFixture,
    dns_mock_unlisted_nxdomain: None,
    snds_mock_unlisted: None,
    cli_config: None,
) -> None:
    with pytest.raises(SystemExit):
        CLI.main()

    assert not any(
        line.startswith("DNS") for line in capsys.readouterr().out.splitlines()
    )


def test_cli_dns_servfail(
    capsys: CaptureFixture,
    dns_mock_servfail: None,
    snds_mock_unlisted: None,
    cli_config: None,
) -> None:
    with pytest.raises(SystemExit):
        CLI.main()

    assert not any(
        line.startswith("DNS") for line in capsys.readouterr().out.splitlines()
    )


def test_cli_dns_timeout(
    capsys: CaptureFixture,
    dns_mock_timeout: None,
    snds_mock_unlisted: None,
    cli_config: None,
) -> None:
    with pytest.raises(SystemExit):
        CLI.main()

    assert not any(
        line.startswith("DNS") for line in capsys.readouterr().out.splitlines()
    )


def test_cli_dns_noanswer(
    capsys: CaptureFixture,
    dns_mock_noanswer: None,
    snds_mock_unlisted: None,
    cli_config: None,
) -> None:
    with pytest.raises(SystemExit):
        CLI.main()

    assert not any(
        line.startswith("DNS") for line in capsys.readouterr().out.splitlines()
    )
