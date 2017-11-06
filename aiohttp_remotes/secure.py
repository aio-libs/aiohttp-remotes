from aiohttp import web
from yarl import URL

from .abc import ABC
from .log import logger


@web.middleware
class Secure(ABC):
    def __init__(self, *, redirect=True,
                 redirect_url=None,
                 x_frame='DENY',
                 sts='max-age=31536000; includeSubDomains',
                 cto='nosniff',
                 xss='1; mode=block',
                 white_paths=()):
        self._redirect = redirect
        if redirect_url is not None:
            redirect_url = URL(redirect_url)
            if redirect_url.scheme != 'https':
                raise ValueError("Redirection url {} should have "
                                 "HTTPS scheme".format(redirect_url))
            if redirect_url.origin() != redirect_url:
                raise ValueError("Redirection url {} should have no "
                                 "path, query and fragment parts".format(
                                     redirect_url))
        self._redirect_url = redirect_url
        self._x_frame = x_frame
        self._sts = sts
        self._cto = cto
        self._xss = xss
        self._white_paths = set(white_paths)

    async def setup(self, app):
        app.on_response_prepare.append(self.on_response_prepare)
        app.middlewares.append(self.middleware)

    async def on_response_prepare(self, request, response):
        x_frame = self._x_frame
        if x_frame is not None:
            response.headers.setdefault('X-Frame-Options', x_frame)
        sts = self._sts
        if sts is not None:
            response.headers.setdefault('Strict-Transport-Security', sts)
        cto = self._cto
        if cto is not None:
            response.headers.setdefault('X-Content-Type-Options', cto)
        xss = self._xss
        if xss is not None:
            response.headers.setdefault('X-XSS-Protection', xss)

    @web.middleware
    async def middleware(self, request, handler):
        whitepath = request.path in self._white_paths
        if not whitepath and not request.secure:
            if self._redirect:
                if self._redirect_url:
                    url = self._redirect_url.join(request.url.relative())
                else:
                    url = request.url.with_scheme('https').with_port(None)
                raise web.HTTPPermanentRedirect(url)
            else:
                msg = "Not secure URL %(url)s"
                logger.error(msg, {'url': request.url})
                await self.raise_error(request)

        return await handler(request)
