from collections.abc import Container, Sequence
from ipaddress import (IPv4Address, IPv4Network, IPv6Address, IPv6Network,
                       ip_address, ip_network)

from .exceptions import IncorrectIPCount, UntrustedIP

MSG = ("Trusted list should be a sequence of sets "
       "with either addresses or networks.")

IP_CLASSES = (IPv4Address, IPv6Address, IPv4Network, IPv6Network)


def parse_trusted_list(lst):
    if isinstance(lst, str) or not isinstance(lst, Sequence):
        raise TypeError(MSG)
    out = []
    has_ellipsis = False
    for elem in lst:
        if elem is ...:
            has_ellipsis = True
            new_elem = ...
        else:
            if has_ellipsis:
                raise ValueError(
                    "Ellipsis is allowed only at the end of list")
            if isinstance(elem, str) or not isinstance(elem, Container):
                raise TypeError(MSG)
            new_elem = []
            for item in elem:
                if isinstance(item, IP_CLASSES):
                    new_elem.append(item)
                    continue
                try:
                    new_elem.append(ip_address(item))
                except ValueError:
                    try:
                        new_elem.append(ip_network(item))
                    except ValueError:
                        raise ValueError(
                            "{!r} is not IPv4 or IPv6 address or network"
                            .format(item))
        out.append(new_elem)
    return out


def remote_ip(trusted, ips):
    if len(trusted) + 1 != len(ips):
        raise IncorrectIPCount(len(trusted) + 1, ips)
    for i in range(len(trusted)):
        ip = ips[i]
        tr = trusted[i]
        if tr is ...:
            return ip
        check_ip(tr, ip)
    return ips[-1]


def check_ip(trusted, ip):
    for elem in trusted:
        if isinstance(elem, (IPv4Address, IPv6Address)):
            if elem == ip:
                break
        else:
            if ip in elem:
                break
    else:
        raise UntrustedIP(ip, trusted)
