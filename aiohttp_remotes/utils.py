from collections.abc import Sequence, Container

from ipaddress import (ip_address, ip_network, IPv4Address,
                       IPv6Address, IPv4Network, IPv6Network)


from .exceptions import IncorrectIPsCount, UntrustedIP


MSG = ('Trusted list should be a sequence of sets '
       'with either addresses or networks.')

IP_CLASSES = (IPv4Address, IPv6Address, IPv4Network, IPv6Network)


def parse_trusted_list(lst):
    if isinstance(lst, str) or not isinstance(lst, Sequence):
        raise TypeError(MSG)
    out = []
    for elem in lst:
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
                        '{!r} is not IPv4 or IPv6 address or network'
                        .format(item))
        out.append(new_elem)
    return out


def remote_ip(trusted, ips):
    if len(trusted) + 1 != len(ips):
        raise IncorrectIPsCount(len(trusted) + 1, ips)
    for i in range(len(trusted)):
        ip = ips[i]
        for elem in trusted[i]:
            if isinstance(elem, (IPv4Address, IPv6Address)):
                if elem == ip:
                    break
            else:
                if ip in elem:
                    break
        else:
            raise UntrustedIP(ip, trusted[i])
    return ips[-1]
