"""Control remote side information.

Properly sets up host, scheme and remote properties of
aiohttp.web.Request if the server is deployed behind reverse proxy.

"""


__version__ = '0.0.1'


from .allowed_hosts import AllowedHosts
from .basic_auth import BasicAuth
from .forwarded import ForwardedRelaxed, ForwardedStrict
from .secure import Secure
from .x_forwarded import XForwardedRelaxed, XForwardedStrict


def setup(app, *args):
    for arg in args:
        arg.setup(app)


__all__ = ('AllowedHosts', 'BasicAuth',
           'ForwardedRelaxed', 'ForwardedStrict',
           'Secure',
           'XForwardedRelaxed', 'XForwardedStrict',
           'setup')
