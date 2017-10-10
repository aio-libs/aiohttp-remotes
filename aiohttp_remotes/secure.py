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
