from aiohttp import web


class ANY:
    def __contains__(self, item):
        return True


class AllowedHosts:

    def __init__(self, allowed_hosts=None, *, white_paths=()):
        if allowed_hosts is None:
            allowed_hosts = {'*'}
        else:
            allowed_hosts = set(allowed_hosts)

        if '*' in allowed_hosts:
            allowed_hosts = ANY()

        self._allowed_hosts = allowed_hosts
        self._white_paths = set(white_paths)

    async def raise_error(self):
        raise web.HTTPBadRequest()

    async def __call__(self, app, handler):
        async def middleware_handler(request):
            if (
                request.path not in self._white_paths and
                request.host not in self._allowed_hosts
            ):
                await self.raise_error()

            return await handler(request)

        return middleware_handler
