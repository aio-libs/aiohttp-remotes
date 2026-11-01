import abc
import sys
from typing import NoReturn

if sys.version_info < (3, 13):
    from typing_extensions import deprecated
else:
    from warnings import deprecated

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
