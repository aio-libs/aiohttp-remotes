from .log import logger


class RemoteError(Exception):
    def log(self, request):
        raise NotImplementedError  # pragma: no cover


class TooManyHeaders(RemoteError):
    @property
    def header(self):
        return self.args[0]

    def log(self, request):
        msg = "Too many headers for %(header)s"
        context = {'header': self.header}
        extra = context.copy()
        extra['request'] = request
        logger.error(msg, context, extra=extra)


class IncorrectIPCount(RemoteError):
    @property
    def expected(self):
        return self.args[0]

    @property
    def actual(self):
        return self.args[1]

    def log(self, request):
        msg = ("Too many X-Forwarded-For values: %(actual)s, "
               "expected %(expected)s")
        context = {'actual': self.actual,
                   'expected': self.expected}
        extra = context.copy()
        extra['request'] = request
        logger.error(msg, context, extra=extra)


class IncorrectForwardedCount(RemoteError):
    @property
    def expected(self):
        return self.args[0]

    @property
    def actual(self):
        return self.args[1]

    def log(self, request):
        msg = ("Too many Forwarded values: %(actual)s, "
               "expected %(expected)s")
        context = {'actual': self.actual,
                   'expected': self.expected}
        extra = context.copy()
        extra['request'] = request
        logger.error(msg, context, extra=extra)


class IncorrectProtoCount(RemoteError):
    @property
    def expected(self):
        return self.args[0]

    @property
    def actual(self):
        return self.args[1]

    def log(self, request):
        msg = ("Too many X-Forwarded-Proto values: %(actual)s, "
               "expected %(expected)s")
        context = {'actual': self.actual,
                   'expected': self.expected}
        extra = context.copy()
        extra['request'] = request
        logger.error(msg, context, extra=extra)


class UntrustedIP(RemoteError):
    @property
    def ip(self):
        return self.args[0]

    @property
    def trusted(self):
        return self.args[1]

    def log(self, request):
        msg = "Untrusted IP: %(ip)s, trusted: %(expected)s"
        context = {'ip': self.ip,
                   'trusted': self.trusted}
        extra = context.copy()
        extra['request'] = request
        logger.error(msg, context, extra=extra)
        logger.error(msg, context, extra=extra)
