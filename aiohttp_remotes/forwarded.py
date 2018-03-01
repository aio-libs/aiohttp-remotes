from ipaddress import ip_address

from aiohttp import web

from .abc import ABC
from .exceptions import IncorrectForwardedCount, RemoteError
from .utils import parse_trusted_list, remote_ip


class ForwardedRelaxed(ABC):

    def __init__(self, num=1):
        self._num = num

    async def setup(self, app):
        app.middlewares.append(self.middleware)

    @web.middleware
    async def middleware(self, request, handler):
        overrides = {}

        for elem in reversed(request.forwarded[-self._num:]):
            for_ = elem.get('for')
            if for_:
                overrides['remote'] = for_
            proto = elem.get('proto')
            if proto is not None:
                overrides['scheme'] = proto
            host = elem.get('host')
            if host is not None:
                overrides['host'] = host

        request = request.clone(**overrides)
        return await handler(request)


class ForwardedStrict(ABC):

    def __init__(self, trusted, *, white_paths=()):
        self._trusted = parse_trusted_list(trusted)
        self._white_paths = set(white_paths)

    async def setup(self, app):
        app.middlewares.append(self.middleware)

    @web.middleware
    async def middleware(self, request, handler):
        if request.path in self._white_paths:
            return await handler(request)
        try:
            overrides = {}

            forwarded = request.forwarded
            if len(self._trusted) != len(forwarded):
                raise IncorrectForwardedCount(len(self._trusted),
                                              len(forwarded))

            peer_ip, *_ = request.transport.get_extra_info('peername')
            ips = [ip_address(peer_ip)]

            for elem in reversed(request.forwarded):
                for_ = elem.get('for')
                if for_:
                    ips.append(ip_address(for_))
                proto = elem.get('proto')
                if proto is not None:
                    overrides['scheme'] = proto
                host = elem.get('host')
                if host is not None:
                    overrides['host'] = host

                overrides['remote'] = str(remote_ip(self._trusted, ips))

            request = request.clone(**overrides)
            return await handler(request)
        except RemoteError as exc:
            exc.log(request)
            await self.raise_error(request)
