import base64
import binascii

from aiohttp import hdrs, web

from .abc import ABC


class BasicAuth(ABC):

    def __init__(self, username, password, realm, *, white_paths=()):
        self._username = username
        self._password = password
        self._realm = realm
        self._white_paths = set(white_paths)

    async def setup(self, app):
        app.middlewares.append(self.middleware)

    async def raise_error(self, request):
        raise web.HTTPUnauthorized(
            headers={
                hdrs.WWW_AUTHENTICATE: 'Basic realm={}'.format(self._realm)
            },
        )

    @web.middleware
    async def middleware(self, request, handler):
        if request.path not in self._white_paths:
            auth_header = request.headers.get(hdrs.AUTHORIZATION)

            if auth_header is None or not auth_header.startswith('Basic '):
                return await self.raise_error(request)

            try:
                secret = auth_header[6:].encode('utf-8')

                auth_decoded = base64.decodestring(secret).decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError,
                    binascii.Error):
                await self.raise_error(request)

            credentials = auth_decoded.split(':')

            if len(credentials) != 2:
                await self.raise_error(request)

            username, password = credentials

            if username != self._username or password != self._password:
                await self.raise_error(request)

        return await handler(request)
