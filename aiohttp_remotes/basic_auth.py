import base64
import binascii

from aiohttp import hdrs, web


class BasicAuth:

    def __init__(self, username, password, realm, *, white_paths=()):
        self._username = username
        self._password = password
        self._realm = realm
        self._white_paths = set(white_paths)

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def realm(self):
        return self._realm

    @property
    def white_paths(self):
        return self._white_paths

    async def request_basic_auth(self, request):
        return web.HTTPUnauthorized(
            headers={
                hdrs.WWW_AUTHENTICATE: 'Basic realm={}'.format(self._realm)
            },
        )

    async def __call__(self, app, handler):
        async def middleware_handler(request):
            if request.path not in self._white_paths:
                auth_header = request.headers.get(hdrs.AUTHORIZATION)

                if auth_header is None or not auth_header.startswith('Basic '):
                    return await self.request_basic_auth(request)

                try:
                    secret = auth_header[6:].encode('utf-8')

                    auth_decoded = base64.decodestring(secret).decode('utf-8')
                except (UnicodeDecodeError, UnicodeEncodeError,
                        binascii.Error):
                    return await self.request_basic_auth(request)

                credentials = auth_decoded.split(':')

                if len(credentials) != 2:
                    return await self.request_basic_auth(request)

                username, password = credentials

                if (
                    username != self._username or
                    password != self._password
                ):
                    return await self.request_basic_auth(request)

            return await handler(request)

        return middleware_handler
