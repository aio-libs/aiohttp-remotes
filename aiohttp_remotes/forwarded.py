from ipaddress import ip_address, ip_network

from aiohttp import web

from .abc import ABC
from .exceptions import RemoteError, IncorrectForwardedCount
from .utils import parse_trusted_list


class ForwardedRelaxed(ABC):

    def __init__(self, num=1):
        self._num = num

    def setup(self, app):
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

    def setup(self, app):
        app.middlewares.append(self.middleware)

    @web.middleware
    async def middleware(self, request, handler):
        try:
            overrides = {}

            forwarded = request.forwarded
            if len(self._trusted) != len(forwarded):
                raise IncorrectForwardedCount(len(trusted), len(forwared))

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
        except RemoteError as exc:
            exc.log(request)
            await self.raise_error(request)
