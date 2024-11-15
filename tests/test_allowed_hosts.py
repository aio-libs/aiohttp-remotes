from aiohttp import web
from aiohttp.pytest_plugin import AiohttpClient
from aiohttp_remotes import AllowedHosts, setup as _setup


async def test_allowed_hosts_ok(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, AllowedHosts({"example.com"}))
    cl = await aiohttp_client(app)
    resp = await cl.get("/", headers={"Host": "example.com"})
    assert resp.status == 200


async def test_allowed_hosts_forbidden(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, AllowedHosts({"example.com"}))
    cl = await aiohttp_client(app)
    resp = await cl.get("/", headers={"Host": "not-allowed.com"})
    assert resp.status == 400


async def test_allowed_hosts_star(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, AllowedHosts({"*"}))
    cl = await aiohttp_client(app)
    resp = await cl.get("/", headers={"Host": "example.com"})
    assert resp.status == 200


async def test_allowed_hosts_default(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, AllowedHosts())
    cl = await aiohttp_client(app)
    resp = await cl.get("/", headers={"Host": "example.com"})
    assert resp.status == 200
