"""Control remote side information.

Properly sets up host, scheme and remote properties of
aiohttp.web.Request if the server is deployed behind reverse proxy.

"""


__version__ = '0.0.1'


from .basic_auth import BasicAuth
from .x_forwarded import XForwardedRelaxed, XForwardedStrict


__all__ = ('BasicAuth', 'XForwardedRelaxed', 'XForwardedStrict')
