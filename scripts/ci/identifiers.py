"""Identifier rules shared by source enumeration and privacy checks."""

import ipaddress
import re

PERSONAL_HOME = re.compile(r"(?:/(?:home|Users)/[A-Za-z0-9_.-]+|[A-Za-z]:[\\/]Users[\\/][A-Za-z0-9_.-]+)")
TAILNET = re.compile(r"\b(?:[a-z0-9-]+\.)*tail[a-z0-9]+\.ts\.net\b", re.I)
EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
NOREPLY = re.compile(r"(?:[A-Za-z0-9+_.\[\]-]+@users\.noreply\.github\.com|noreply@github\.com)\Z")
IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?!\d|\.\d)")
PRIVATE_NETWORKS = tuple(ipaddress.ip_network((address, prefix)) for address, prefix in
                         ((0x0A000000, 8), (0xAC100000, 12), (0xC0A80000, 16),
                          (0x64400000, 10), (0xA9FE0000, 16)))


def has_private_identifier(text: str) -> bool:
    if PERSONAL_HOME.search(text) or TAILNET.search(text):
        return True
    if any(not NOREPLY.fullmatch(value) for value in EMAIL.findall(text)):
        return True
    for value in IPV4.findall(text):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            continue
        if any(address in network for network in PRIVATE_NETWORKS):
            return True
    return False
