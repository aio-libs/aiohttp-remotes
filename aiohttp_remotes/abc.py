import abc

from typing_extensions import NoReturn, deprecated

from aiohttp import web


class AbstractRemote(abc.ABC):
    @abc.abstractmethod
    async def setup(self, app: web.Application) -> None:
        pass  # pragma: no cover

    async def raise_error(self, request: web.Request) -> NoReturn:
        raise web.HTTPBadRequest()

@deprecated("Renamed to AbstractRemote for readability purposes")
class ABC(AbstractRemote):
    pass

