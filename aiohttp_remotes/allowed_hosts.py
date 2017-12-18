from aiohttp import web

from .abc import ABC


class ANY:
    def __contains__(self, item):
        return True


class AllowedHosts(ABC):

    def __init__(self, allowed_hosts=('*',), *, white_paths=()):
        allowed_hosts = set(allowed_hosts)

        if '*' in allowed_hosts:
            allowed_hosts = ANY()

        self._allowed_hosts = allowed_hosts
        self._white_paths = set(white_paths)

    async def setup(self, app):
        app.middlewares.append(self.middleware)

    @web.middleware
    async def middleware(self, request, handler):
        if (
            request.path not in self._white_paths and
            request.host not in self._allowed_hosts
        ):
            await self.raise_error(request)

        return await handler(request)
