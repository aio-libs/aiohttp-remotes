from ipaddress import ip_address, ip_network

import aiohttp
from aiohttp import web

from .abc import ABC
from .log import logger


class Cloudflare(ABC):

    def __init__(self, client=None):
        self._ip_networks = set()
        self._client = client

    def _parse_mask(self, text):
        ret = set()
        for mask in text.splitlines():
            try:
                mask = ip_network(mask)
            except (ValueError, TypeError):
                continue

            ret.add(mask)
        return ret

    async def setup(self, app):
        if self._client is not None:  # pragma: no branch
            client = self._client
        else:
            client = aiohttp.ClientSession()  # pragma: no cover
        try:
            async with client.get(
                    'https://www.cloudflare.com/ips-v4') as response:
                self._ip_networks |= self._parse_mask(await response.text())
            async with client.get(
                    'https://www.cloudflare.com/ips-v6') as response:
                self._ip_networks |= self._parse_mask(await response.text())
        finally:
            if self._client is None:  # pragma: no cover
                await client.close()

        if not self._ip_networks:
            raise RuntimeError("No networks are available")
        app.middlewares.append(self.middleware)

    @web.middleware
    async def middleware(self, request, handler):
        remote_ip = ip_address(request.remote)

        for network in self._ip_networks:
            if remote_ip in network:
                request = request.clone(
                    remote=request.headers['CF-CONNECTING-IP'])
                return await handler(request)

        msg = "Not cloudflare: %(remote_ip)s"
        context = {'remote_ip': remote_ip}
        logger.error(msg, context)

        await self.raise_error(request)
