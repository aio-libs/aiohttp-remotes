"""Control remote side information.

Properly sets up host, scheme and remote properties of
aiohttp.web.Request if the server is deployed behind reverse proxy.

"""


__version__ = '0.1.2'


from .allowed_hosts import AllowedHosts
from .basic_auth import BasicAuth
from .cloudflare import Cloudflare
from .forwarded import ForwardedRelaxed, ForwardedStrict
from .secure import Secure
from .x_forwarded import XForwardedRelaxed, XForwardedStrict


async def setup(app, *tools):
    for tool in tools:
        await tool.setup(app)


__all__ = ('AllowedHosts', 'BasicAuth',
           'Cloudflare',
           'ForwardedRelaxed', 'ForwardedStrict',
           'Secure',
           'XForwardedRelaxed', 'XForwardedStrict',
           'setup')
