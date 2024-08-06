import pytest
from _pytest.capture import CaptureFixture

from rblchecker import CLI
from rblchecker.utilities import (
    get_ip_addresses_in_ip_network,
    get_ip_addresses_in_range,
)
from tests.conftest import SNDSListings

# SNDS


def test_cli_snds_listed(
    capsys: CaptureFixture,
    snds_mock_listed: SNDSListings,
) -> None:
    with pytest.raises(SystemExit) as e:
        CLI.main()

    assert e.value.code == 1

    output = capsys.readouterr().out.splitlines()

    for listing in snds_mock_listed:
        start_range, end_range, blocked, reason = listing

        for ip_address in get_ip_addresses_in_range(
            str(start_range), str(end_range)
        ):
            assert (
                f"(SNDS) IP address {ip_address} is listed on SNDS (reason: '{reason}')"
                in output
            )


def test_cli_snds_unlisted(
    capsys: CaptureFixture,
    snds_mock_unlisted: None,
) -> None:
    with pytest.raises(SystemExit):
        CLI.main()

    assert not any(
        line.startswith("SNDS")
        for line in capsys.readouterr().out.splitlines()
    )


# DNS


def test_cli_dns_listed(
    capsys: CaptureFixture,
    dns_mock_listed: None,
    config_mock: dict,
    snds_mock_unlisted: None,
) -> None:
    with pytest.raises(SystemExit) as e:
        CLI.main()

    assert e.value.code == 1

    output = capsys.readouterr().out.splitlines()

    ip_addresses = []

    for ip_network in config_mock["ip_networks"]:
        ip_addresses.extend(get_ip_addresses_in_ip_network(ip_network))

    assert len(output) >= len(ip_addresses)

    for ip_address in ip_addresses:
        for host in config_mock["checkers"]["dns"]["hosts"]:
            assert (
                f"(DNS) IP address {ip_address} is listed on {host}" in output
            )


def test_cli_dns_unlisted(
    capsys: CaptureFixture, dns_mock_unlisted: None, snds_mock_unlisted: None
) -> None:
    with pytest.raises(SystemExit):
        CLI.main()

    assert not any(
        line.startswith("DNS") for line in capsys.readouterr().out.splitlines()
    )
