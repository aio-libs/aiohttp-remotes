import abc
from aiohttp import web


class ABC(abc.ABC):
    @abc.abstractmethod
    def setup(self, app):
        pass

    async def raise_error(self, request):
        raise web.HTTPBadRequest()
