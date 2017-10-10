from aiohttp import web


class ANY:
    def __contains__(self, item):
        return True


class AllowedHosts:

    def __init__(self, allowed_hosts=None, whitelist=tuple()):
        if allowed_hosts is None:
            allowed_hosts = ['*']

        allowed_hosts = set(allowed_hosts)

        if '*' in allowed_hosts:
            allowed_hosts = ANY()

        self.allowed_hosts = allowed_hosts
        self.whitelist = set(whitelist)

    async def middleware_factory(self, app, handler):
        async def middleware_handler(request):
            if (
                request.raw_path not in self.whitelist and
                request.host not in self.allowed_hosts
            ):
                raise web.HTTPNotAcceptable

            return await handler(request)

        return middleware_handler
