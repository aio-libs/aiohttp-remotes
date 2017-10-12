from ipaddress import ip_address, ip_network

from aiohttp import hdrs, web

from .exceptions import TooManyHeaders
from .log import logger


class ForwardedRelaxed:

    async def raise_error(self):
        raise web.HTTPBadRequest()

    async def middleware_handler(self, request, handler):
        overrides = {}

        for elem in request.forwarded:
            pass
        forwarded_for = self.get_forwarded_for()
        if forwarded_for:
            overrides['remote'] = str(forwarded_for[0])

        proto = self.get_forwarded_proto()
        if proto is not None:
            overrides['scheme'] = proto

        host = self.get_forwarded_host()
        if host is not None:
            overrides['host'] = host

        request = request.clone(**overrides)

        return await handler(request)

    async def __call__(self, app, handler):
        async def middleware_handler(request):
            try:
                return await self.middleware_handler(request, handler)
            except TooManyHeaders as exc:
                msg = 'Too many headers for %(header)s'
                context = {'header': exc.header}
                logger.error(msg, context, extra={'request': request,
                                                  'header': exc.header})
                self.raise_error()
        return middleware_handler


class ForwardedStrict(ForwardedRelaxed):

    def __init__(self, num_proxies=1, upstreams=(), *, white_paths=()):
        self._num_proxies = num_proxies
        self._upstreams = set(ip_network(i) for i in upstreams)
        self._white_paths = set(white_paths)

    def get_remote_addr(self, request):
        forwarded_for = self._get_forwarded_for(request.headers)

        trusted_header = len(forwarded_for) >= self._num_proxies

        real_remote_addr, _ = request.transport.get_extra_info('peername')

        if trusted_header:
            trusted = False
            _real_remote_addr = ip_address(real_remote_addr)

            for upstream in self.upstreams:
                if _real_remote_addr in upstream:
                    trusted = True
                    break

            if trusted:
                remote_addr = forwarded_for[-self.num_proxies]
            else:
                remote_addr = real_remote_addr
        else:
            remote_addr = real_remote_addr
            trusted = False

        return remote_addr, trusted

    async def middleware_handler(self, request, handler):
        if request.path not in self.white_paths:
            overrides = {}
            remote_addr, trusted = self._get_remote_addr(request)

            if not trusted:
                msg = 'Reverse proxy not found: %(remote_addr)s'
                context = {'remote_addr': remote_addr}
                logger.error(msg, context, extra={'request': request})

                self.raise_error()
            overrides['remote'] = str(remote_addr)

            proto = self._get_forwarded_proto()
            if proto is not None:
                overrides['scheme'] = proto

            host = self._get_forwarded_host()
            if host is not None:
                overrides['host'] = host

            request = request.clone(**overrides)

        return await handler(request)
