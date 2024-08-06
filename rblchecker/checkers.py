"""Checkers."""

import csv
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Tuple, Union

import dns.resolver
import requests

from rblchecker.utilities import get_ip_addresses_in_range, reverse_ip_address

BASE_URL_SNDS = (
    "https://sendersupport.olc.protection.outlook.com/snds/ipStatus.aspx"
)


class Checker:
    """Interface for checkers."""

    pass


class DNSChecker(Checker):
    """Checker for DNSBLs."""

    def __init__(
        self, ip_address: Union[IPv6Address, IPv4Address], host: str
    ) -> None:
        """Set attributes."""
        self.ip_address = ip_address
        self.host = host

    @staticmethod
    def _get_query_name(
        ip_address: Union[IPv6Address, IPv4Address], host: str
    ) -> str:
        """Get name for DNS query."""
        return reverse_ip_address(ip_address) + "." + host

    def check(
        self,
    ) -> bool:
        """Check whether IP address is listed in RBL."""
        query_name = self._get_query_name(self.ip_address, self.host)

        try:
            dns.resolver.resolve(query_name, "A")
        except dns.resolver.NXDOMAIN:
            return False

        return True


class SNDSChecker(Checker):
    """Checker for Microsoft SNDS."""

    def __init__(
        self, ip_address: Union[IPv6Address, IPv4Address], key: str
    ) -> None:
        """Set attributes."""
        self.ip_address = ip_address
        self.key = key

    def check(
        self,
    ) -> Tuple[bool, Optional[str]]:
        """Check whether IP address is listed in RBL."""
        request = requests.get(BASE_URL_SNDS, params={"key": self.key})
        request.raise_for_status()

        response = request.text.splitlines()

        reader = csv.DictReader(
            response,
            fieldnames=["first_ip", "last_ip", "blocked", "details"],
            delimiter=",",
        )

        for row in reader:
            ip_addresses_in_range = get_ip_addresses_in_range(
                row["first_ip"], row["last_ip"]
            )

            if str(self.ip_address) not in ip_addresses_in_range:
                continue

            if row["blocked"] != "Yes":
                continue

            return True, row["details"]

        return False, None
