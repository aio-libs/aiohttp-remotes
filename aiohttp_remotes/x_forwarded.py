from ipaddress import ip_address, ip_network

from aiohttp import web


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
        self.upstreams = set(ip_network(i) for i in upstreams)
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
            _real_remote_addr = ip_address(real_remote_addr)

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
