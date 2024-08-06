import csv
import io
import ipaddress
import os
import uuid
from collections import namedtuple
from typing import Generator, List, NewType

import dns
import docopt
import pytest
import yaml
from pytest_mock import MockerFixture
from requests_mock.mocker import Mocker

from rblchecker import CLI
from rblchecker.checkers import BASE_URL_SNDS

SNDSListing = namedtuple(
    "SNDSListing", ["start_range", "end_range", "blocked", "reason"]
)
SNDSListings = NewType("SNDSListings", List[SNDSListing])


def get_tmp_file() -> str:
    return os.path.join(os.path.sep, "tmp", str(uuid.uuid4()))


@pytest.fixture
def config_path() -> str:
    return get_tmp_file()


@pytest.fixture(autouse=True)
def config_mock(config_path: str) -> Generator[dict, None, None]:
    config = {
        "ip_networks": [
            # IPv6 address
            "2001:0db8::/128",
            # IPv6 range (discouraged, but should still be tested)
            "2001:0db8::/127",
            # IPv4 address
            "198.51.100.100/32",
            # IPv4 range
            "198.51.100.0/27",
        ],
        "checkers": {
            "snds": {"key": str(uuid.uuid4())},
            "dns": {"hosts": ["dnsbl.example.com"]},
        },
    }

    with open(config_path, "w") as fh:
        fh.write(yaml.dump(config))

    yield config

    os.unlink(config_path)


@pytest.fixture
def snds_mock_listed(
    requests_mock: Mocker, config_mock: Generator[dict, None, None]
) -> SNDSListings:
    ip_range = ipaddress.ip_network(config_mock["ip_networks"][3])

    listings = SNDSListings(
        [
            SNDSListing(
                ip_range[1],  # Random
                ip_range[25],  # Random
                "Yes",
                "Blocked due to user complaints or other evidence of spamming",
            ),
            SNDSListing(
                ip_range[26],  # Random
                ip_range[27],  # Random
                "No",
                "Junked due to user complaints or other evidence of spamming",
            ),
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
def snds_mock_unlisted(
    requests_mock: Mocker, config_mock: Generator[dict, None, None]
) -> None:
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


@pytest.fixture
def cli_config(mocker: MockerFixture, config_path: str) -> None:
    mocker.patch(
        "rblchecker.CLI.get_args",
        return_value=docopt.docopt(
            CLI.__doc__,
            ["--config-path", config_path],
        ),
    )
