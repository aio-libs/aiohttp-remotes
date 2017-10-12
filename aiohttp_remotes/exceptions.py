class TooManyHeaders(Exception):
    @property
    def header(self):
        return self.args[0]
