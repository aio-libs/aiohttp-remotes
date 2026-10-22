from collections.abc import Sequence
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from types import EllipsisType
from typing import Any, cast

from aiohttp import web

from .log import logger

IPAddress = IPv4Address | IPv6Address
IPNetwork = IPv4Network | IPv6Network
IPRule = IPAddress | IPNetwork
Trusted = Sequence[EllipsisType | Sequence[IPRule]]


class RemoteError(Exception):
    def log(self, request: web.Request) -> None:
        raise NotImplementedError  # pragma: no cover


class TooManyHeaders(RemoteError):
    @property
    def header(self) -> str:
        return cast(str, self.args[0])

    def log(self, request: web.Request) -> None:
        msg = "Too many headers for %(header)s"
        context: dict[str, Any] = {"header": self.header}
        extra = context.copy()
        extra["request"] = request
        logger.error(msg, context, extra=extra)


class IncorrectIPCount(RemoteError):
    @property
    def expected(self) -> int:
        return cast(int, self.args[0])

    @property
    def actual(self) -> Sequence[IPAddress]:
        return cast(Sequence[IPAddress], self.args[1])

    def log(self, request: web.Request) -> None:
        msg = "Too many X-Forwarded-For values: %(actual)s, expected %(expected)s"
        context: dict[str, Any] = {"actual": self.actual, "expected": self.expected}
        extra = context.copy()
        extra["request"] = request
        logger.error(msg, context, extra=extra)


class IncorrectForwardedCount(RemoteError):
    @property
    def expected(self) -> int:
        return cast(int, self.args[0])

    @property
    def actual(self) -> int:
        return cast(int, self.args[1])

    def log(self, request: web.Request) -> None:
        msg = "Too many Forwarded values: %(actual)s, " "expected %(expected)s"
        context: dict[str, Any] = {"actual": self.actual, "expected": self.expected}
        extra = context.copy()
        extra["request"] = request
        logger.error(msg, context, extra=extra)


class IncorrectProtoCount(RemoteError):
    @property
    def expected(self) -> int:
        return cast(int, self.args[0])

    @property
    def actual(self) -> Sequence[str]:
        return cast(Sequence[str], self.args[1])

    def log(self, request: web.Request) -> None:
        msg = "Too many X-Forwarded-Proto values: %(actual)s, " "expected %(expected)s"
        context: dict[str, Any] = {"actual": self.actual, "expected": self.expected}
        extra = context.copy()
        extra["request"] = request
        logger.error(msg, context, extra=extra)


class IncorrectHostCount(RemoteError):
    @property
    def expected(self) -> int:
        return cast(int, self.args[0])

    @property
    def actual(self) -> Sequence[str]:
        return cast(Sequence[str], self.args[1])

    def log(self, request: web.Request) -> None:
        msg = "Too many X-Forwarded-Host values: %(actual)s, " "expected %(expected)s"
        context: dict[str, Any] = {"actual": self.actual, "expected": self.expected}
        extra = context.copy()
        extra["request"] = request
        logger.error(msg, context, extra=extra)


class UntrustedIP(RemoteError):
    @property
    def ip(self) -> IPAddress:
        return cast(IPAddress, self.args[0])

    @property
    def trusted(self) -> Sequence[IPAddress]:
        return cast(Sequence[IPAddress], self.args[1])

    def log(self, request: web.Request) -> None:
        msg = "Untrusted IP: %(ip)s, trusted: %(trusted)s"
        context: dict[str, Any] = {"ip": self.ip, "trusted": self.trusted}
        extra = context.copy()
        extra["request"] = request
        logger.error(msg, context, extra=extra)
        logger.error(msg, context, extra=extra)
