class TooManyHeaders(Exception):
    @property
    def header(self):
        return self.args[0]



class IncorrectIPCount(Exception):
    @property
    def expected(self):
        return self.args[0]
    @property
    def actual(self):
        return self.args[1]


class IncorrectProtoCount(Exception):
    @property
    def expected(self):
        return self.args[0]
    @property
    def actual(self):
        return self.args[1]


class UntrustedIP(Exception):
    @property
    def ip(self):
        return self.args[0]
    @property
    def trusted(self):
        return self.args[1]
