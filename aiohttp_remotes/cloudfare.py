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
        num_proxies=1,
        upstreams=tuple(),
        whitelist=tuple(),
    ):
        self.header = header
        self.url = url
        self.whitelist = set(whitelist)

        if num_proxies:
            self.proxy = ProxyMiddleware(
                num_proxies=num_proxies,
                upstreams=upstreams,
            )
        else:
            self.proxy = None

        self._masks = set()

    async def setup(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                text = await response.text()

        for mask in text.split('\n'):
            try:
                mask = ip_network(mask)
            except (ValueError, TypeError):
                continue

            self._masks.add(mask)

        assert self._masks

    def is_cloudflare(self, remote_addr):
        remote_addr = ip_address(remote_addr)

        return any(map(lambda mask: remote_addr in mask, self.__masks))

    async def middleware_factory(self, app, handler):
        async def middleware_handler(request):
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

        return middleware_handler

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
