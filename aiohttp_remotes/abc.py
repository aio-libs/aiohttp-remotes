import abc

from aiohttp import web


class ABC(abc.ABC):
    @abc.abstractmethod
    async def setup(self, app):
        pass  # pragma: no cover

    async def raise_error(self, request):
        raise web.HTTPBadRequest()
