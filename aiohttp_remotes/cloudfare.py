from ipaddress import ip_address, ip_network

import aiohttp
from aiohttp import web

from .log import logger

ProxyMiddleware = 1


class CloudflareMiddleware:

    def __init__(
        self,
        header='CF-CONNECTING-IP',
        url='https://www.cloudflare.com/ips-v4',
        whitelist=tuple(),
    ):
        self._header = header
        self._url = url
        self.whitelist = set(whitelist)

        self._masks = set()

    async def setup(self, app):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                text = await response.text()

        for mask in text.split('\n'):
            try:
                mask = ip_network(mask)
            except (ValueError, TypeError):
                continue

            self._masks.add(mask)

        if not self._masks:
            raise RuntimeError("No masks are available")
        app.middlewares.append(self.middleware)

    def is_cloudflare(self, remote_addr):
        remote_addr = ip_address(remote_addr)

        return any(map(lambda mask: remote_addr in mask, self.__masks))

    @web.middleware
    async def middleware(self, request, handler):
        if request.rel_url.raw_path not in self.whitelist:
            remote_addr, trusted = self.get_remote_addr(
                request.headers, request.transport,
            )

            if not trusted:
                msg = 'Not cloudflare: %(remote_addr)s'
                context = {'remote_addr': remote_addr}
                logger.error(msg, context)

                raise web.HTTPNotAcceptable

        return await handler(request)

    def get_remote_addr(self, headers, transport):
        trusted = False

        if self.proxy:
            remote_addr, trusted = self.proxy.get_remote_addr(
                headers, transport,
            )

            if not trusted:
                return remote_addr, trusted
        else:
            remote_addr, _ = transport.get_extra_info('peername')

        if self.is_cloudflare(remote_addr):
            remote_addr = headers[self.header]

            trusted = True

        return remote_addr, trusted

    def remote_addr_callback(self, headers, transport):
        remote_addr, _ = self.get_remote_addr(headers, transport)

        return remote_addr
