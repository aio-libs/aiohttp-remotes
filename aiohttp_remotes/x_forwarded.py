from ipaddress import ip_address, ip_network

from aiohttp import hdrs, web

from .abc import ABC
from .exceptions import TooManyHeaders
from .log import logger
from .utils import parse_trusted_list


class XForwardedRelaxed(ABC):

    def setup(self, app):
        app.middlewares.append(self.middleware)

    def get_forwarded_for(self, headers):
        forwarded_for = headers.getall(hdrs.X_FORWARDED_FOR, [])
        if not forwarded_for:
            return []
        if len(forwarded_for) > 1:
            raise TooManyHeaders(hdrs.X_FORWARDED_FOR)
        forwarded_for = forwarded_for[0].split(',')
        forwarded_for = [
            ip_address(addr) for addr in
            (a.strip() for a in forwarded_for)
            if addr
        ]

        return forwarded_for

    def get_forwarded_proto(self, headers):
        forwarded_proto = headers.getall(hdrs.X_FORWARDED_PROTO, [])
        if not forwarded_proto:
            return []
        if len(forwarded_proto) > 1:
            raise TooManyHeaders(hdrs.X_FORWARDED_PROTO)
        forwarded_proto = forwarded_proto[0].split(',')
        forwarded_proto = [p.strip() for p in forwarded_proto]

        return forwarded_proto

    def get_forwarded_host(self, headers):
        forwarded_host = headers.getall(hdrs.X_FORWARDED_HOST, [])
        if len(forwarded_host) > 1:
            raise TooManyHeaders(hdrs.X_FORWARDED_HOST)
        return forwarded_host[0] if forwarded_host else None

    @web.middleware
    async def middleware(self, request, handler):
        try:
            overrides = {}

            headers = request.headers
            forwarded_for = self.get_forwarded_for(headers)
            if forwarded_for:
                overrides['remote'] = str(forwarded_for[0])

            proto = self.get_forwarded_proto(headers)
            if proto:
                overrides['scheme'] = proto[0]

            host = self.get_forwarded_host(headers)
            if host is not None:
                overrides['host'] = host

            request = request.clone(**overrides)

            return await handler(request)
        except TooManyHeaders as exc:
            msg = 'Too many headers for %(header)s'
            context = {'header': exc.header}
            logger.error(msg, context, extra={'request': request,
                                              'header': exc.header})
            await self.raise_error(request)


class XForwardedStrict(XForwardedRelaxed):

    def __init__(self, trusted, *, white_paths=()):
        self._trusted = parse_trusted_list(trusted)
        self._white_paths = set(white_paths)

    @web.middleware
    async def middleware(self, request, handler):
        if request.path in self._white_paths:
            return await handler(request)
        try:
            overrides = {}

            forwarded_for = self.get_forwarded_for()
            peer_ip, _ = request.transport.get_extra_info('peername')
            ips = [peer_ip] + list(reversed(forwarded_for))
            remote_ip = remote_ip(self._trusted, ips)
            overrides['remote'] = str(remote_ip)

            proto = self.get_forwarded_proto()
            if proto:
                overrides['scheme'] = proto[0]

            host = self.get_forwarded_host()
            if host is not None:
                overrides['host'] = host

            request = request.clone(**overrides)

            return await handler(request)
        except TooManyHeaders as exc:
            msg = 'Too many headers for %(header)s'
            context = {'header': exc.header}
            logger.error(msg, context, extra={'request': request,
                                              'header': exc.header})
            await self.raise_error(request)
