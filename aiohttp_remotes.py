import base64
import binascii
import logging

from aiohttp import ClientSession, web
from netaddr import AddrFormatError, IPAddress, IPNetwork

logger = logging.getLogger(__name__)


class BasicAuthMiddleware:

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username')
        self.password = kwargs.pop('password')
        self.realm = kwargs.pop('realm')
        self.whitelist = set(kwargs.pop('whitelist'))

        super().__init__(*args, **kwargs)

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
            if request.rel_url.raw_path not in self.whitelist:
                auth_header = request.headers.get('Authorization')

                if auth_header is None or not auth_header.startswith('Basic '):
                    return self.request_basic_auth(request)

                try:
                    secret = auth_header[6:].encode('utf-8')

                    auth_decoded = base64.decodestring(secret).decode('utf-8')
                except (UnicodeDecodeError, UnicodeEncodeError, binascii.Error):  # noqa
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


class CloudflareMiddleware:

    def __init__(
        self,
        header='CF-CONNECTING-IP',
        url='https://www.cloudflare.com/ips-v4',
        num_proxies=1,
        upstreams=tuple(),
        whitelist=tuple(),
    ):
        self.header = header
        self.url = url
        self.proxy = bool(num_proxies)
        self.whitelist = set(whitelist)

        if self.proxy:
            self.proxy = ProxyMiddleware(
                num_proxies=num_proxies,
                upstreams=upstreams,
            )

        self.__masks = set()

    async def setup(self):
        async with ClientSession() as session:
            async with session.get(self.url) as response:
                text = await response.text()

        for mask in text.split('\n'):
            try:
                mask = IPNetwork(mask)
            except (ValueError, TypeError, AddrFormatError):
                continue

            self.__masks.add(mask)

        assert self.__masks

    def is_cloudflare(self, remote_addr):
        remote_addr = IPAddress(remote_addr)

        return any(map(lambda mask: remote_addr in mask, self.__masks))

    async def middleware_factory(self, app, handler):
        async def middleware_handler(request):
            if request.rel_url.raw_path not in self.whitelist:
                remote_addr, trusted = self.get_remote_addr(
                    request.headers, request.transport,
                )

                if not trusted:
                    msg = 'Not cloudflare: %(remote_addr)s'
                    context = {'remote_addr': remote_addr}
                    logger.error(msg, context)

                    raise web.HTTPNotAcceptable

            return await handler(request)

        return middleware_handler

    def get_remote_addr(self, headers, transport):
        trusted = False

        if self.proxy:
            remote_addr, trusted = self.proxy.get_remote_addr(
                headers, transport,
            )

            if not trusted:
                return remote_addr, trusted
        else:
            remote_addr, _ = transport.get_extra_info('peername')

        if self.is_cloudflare(remote_addr):
            remote_addr = headers[self.header]

            trusted = True

        return remote_addr, trusted

    def remote_addr_callback(self, headers, transport):
        remote_addr, _ = self.get_remote_addr(headers, transport)

        return remote_addr


class ProxyMiddleware:

    def __init__(
        self,
        header='X-FORWARDED-FOR',
        num_proxies=1,
        upstreams=tuple(),
        whitelist=tuple(),
    ):
        self.header = header
        self.num_proxies = num_proxies
        self.upstreams = set(map(IPNetwork, upstreams))
        self.whitelist = set(whitelist)

    def get_forwarded_for(self, headers):
        forwarded_for = headers.get(self.header, '').split(',')
        forwarded_for = [
            addr for addr in [addr.strip() for addr in forwarded_for] if addr
        ]

        return forwarded_for

    def get_remote_addr(self, headers, transport):
        forwarded_for = self.get_forwarded_for(headers)

        trusted_header = len(forwarded_for) >= self.num_proxies

        real_remote_addr, _ = transport.get_extra_info('peername')

        if trusted_header:
            trusted = False
            _real_remote_addr = IPAddress(real_remote_addr)

            for upstream in self.upstreams:
                if _real_remote_addr in upstream:
                    trusted = True
                    break

            if trusted:
                remote_addr = forwarded_for[-1 * self.num_proxies]
            else:
                remote_addr = real_remote_addr
        else:
            remote_addr = real_remote_addr
            trusted = False

        return remote_addr, trusted

    async def middleware_factory(self, app, handler):
        async def middleware_handler(request):
            if request.rel_url.raw_path not in self.whitelist:
                remote_addr, trusted = self.get_remote_addr(
                    request.headers, request.transport,
                )

                if not trusted:
                    msg = 'Not proxy: %(remote_addr)s'
                    context = {'remote_addr': remote_addr}
                    logger.error(msg, context)

                    raise web.HTTPNotAcceptable

            return await handler(request)

        return middleware_handler

    def remote_addr_callback(self, headers, transport):
        remote_addr, _ = self.get_remote_addr(headers, transport)

        return remote_addr


class SecureMiddleware:

    scheme = 'https'
    sts_seconds = 31536000

    def __init__(self, redirect=True, whitelist=tuple()):
        self.redirect = redirect
        self.whitelist = set(whitelist)

    async def middleware_factory(self, app, handler):
        async def middleware_handler(request):
            whitelisted = request.rel_url.raw_path not in self.whitelist
            if whitelisted:
                if request.url.scheme != self.scheme:
                    if self.redirect:
                        url = request.url.with_scheme(self.scheme)

                        raise web.HTTPFound(url)
                    else:
                        msg = 'Not https'
                        logger.error(msg)

                        raise web.HTTPNotAcceptable

            response = await handler(request)

            if whitelisted or request.scheme != self.scheme:
                return response

            if 'x-frame-options' not in response.headers:
                response.headers['x-frame-options'] = 'DENY'

            if 'strict-transport-security' not in response.headers:
                sts_header = 'max-age={seconds}; includeSubDomains'
                sts_header = sts_header.format(
                    seconds=self.sts_seconds,
                )
                response.headers['strict-transport-security'] = sts_header

            if 'x-content-type-options' not in response.headers:
                response.headers['x-content-type-options'] = 'nosniff'

            if 'x-xss-protection' not in response.headers:
                response.headers['x-xss-protection'] = '1; mode=block'

            return response

        return middleware_handler


class HostMiddleware:

    def __init__(self, allowed_hosts=None, whitelist=tuple()):
        if allowed_hosts is None:
            allowed_hosts = ['*']

        allowed_hosts = set(allowed_hosts)

        if '*' in allowed_hosts:
            class ANY:

                def __contains__(self, item):
                    return True

            allowed_hosts = ANY()

        self.allowed_hosts = allowed_hosts
        self.whitelist = set(whitelist)

    async def middleware_factory(self, app, handler):
        async def middleware_handler(request):
            if (
                request.rel_url.raw_path not in self.whitelist and
                request.url.host not in self.allowed_hosts
            ):
                raise web.HTTPNotAcceptable

            return await handler(request)

        return middleware_handler
