import aiohttp
from aiohttp import web

from aiohttp_remotes import XForwardedRelaxed


async def xtest_x_forwarded_ok(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    app.middlewares.append(XForwardedRelaxed())
    cl = await test_client(app)
    resp = await cl.get('/')
    assert resp.status == 200

