import csv
import io
import ipaddress
import uuid
from collections import namedtuple
from typing import List, NewType, Tuple

import dns
import docopt
import pytest
from pytest_mock import MockerFixture
from requests_mock.mocker import Mocker

from rblchecker import CLI
from rblchecker.checkers import BASE_URL_SNDS

SNDSListing = namedtuple(
    "SNDSListing", ["start_range", "end_range", "blocked", "reason"]
)
SNDSListings = NewType("SNDSListings", List[SNDSListing])


@pytest.fixture(autouse=True)
def config_mock(mocker: MockerFixture) -> dict:
    config = {
        "ip_networks": ["198.51.100.0/27"],
        "checkers": {
            "snds": {"key": uuid.uuid4()},
            "dns": {"hosts": ["dnsbl.example.com"]},
        },
    }

    mocker.patch("rblchecker.CLI.get_config", return_value=config)

    return config


@pytest.fixture
def snds_mock_listed(requests_mock: Mocker, config_mock: dict) -> SNDSListings:
    ip_range = ipaddress.ip_network(config_mock["ip_networks"][0])

    listings = SNDSListings(
        [
            SNDSListing(
                ip_range[1],  # Random
                ip_range[25],  # Random
                "Yes",
                "Blocked due to user complaints or other evidence of spamming",
            )
        ]
    )

    file_ = io.StringIO()

    writer = csv.writer(file_, delimiter=",")

    for listing in listings:
        start_range, end_range, blocked, reason = listing

        writer.writerow([start_range, end_range, blocked, reason])

    requests_mock.get(BASE_URL_SNDS, text=file_.getvalue())

    return listings


@pytest.fixture
def snds_mock_unlisted(requests_mock: Mocker, config_mock: dict) -> None:
    requests_mock.get(BASE_URL_SNDS, text="")


@pytest.fixture
def dns_mock_listed(mocker: MockerFixture) -> None:
    answer = dns.resolver.resolve("example.com", "A")

    mocker.patch(
        "dns.resolver.resolve",
        return_value=answer,
    )


@pytest.fixture
def dns_mock_unlisted(mocker: MockerFixture) -> None:
    try:
        dns.resolver.resolve("doesntexist.example.com", "A")
    except dns.resolver.NXDOMAIN as e:
        e_ = e

    mocker.patch(
        "dns.resolver.resolve",
        side_effect=e_,
    )


@pytest.fixture(autouse=True)
def _cli_config(mocker: MockerFixture) -> None:
    mocker.patch(
        "rblchecker.CLI.get_args",
        return_value=docopt.docopt(
            CLI.__doc__,
            ["--config-path", "config.yml"],
        ),
    )
