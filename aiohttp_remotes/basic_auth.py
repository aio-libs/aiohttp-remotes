import base64
import binascii

from aiohttp import web


class BasicAuthMiddleware:

    def __init__(self, username, password, realm, *, whitelist=()):
        self.username = username
        self.password = password
        self.realm = realm
        self.whitelist = set(whitelist)

    def request_basic_auth(self, request):
        status = web.HTTPUnauthorized.status_code

        return web.json_response(
            {
                'status': status,
                'error': 'Unauthorized',
            },
            status=status,
            headers={
                'WWW-Authenticate': 'Basic realm={realm}'.format(
                    realm=self.realm,
                ),
            },
        )

    async def middleware_factory(self, app, handler):
        async def middleware_handler(request):
            if request.raw_path not in self.whitelist:
                auth_header = request.headers.get('Authorization')

                if auth_header is None or not auth_header.startswith('Basic '):
                    return self.request_basic_auth(request)

                try:
                    secret = auth_header[6:].encode('utf-8')

                    auth_decoded = base64.decodestring(secret).decode('utf-8')
                except (UnicodeDecodeError, UnicodeEncodeError,
                        binascii.Error):
                    return self.request_basic_auth(request)

                credentials = auth_decoded.split(':')

                if len(credentials) != 2:
                    return self.request_basic_auth(request)

                username, password = credentials

                if (
                    username != self.username or
                    password != self.password
                ):
                    return self.request_basic_auth(request)

            return await handler(request)

        return middleware_handler
