import aiohttp
from aiohttp import web
from aiohttp.pytest_plugin import AiohttpClient
from aiohttp_remotes import BasicAuth, setup as _setup


async def test_basic_auth_ok(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, BasicAuth("user", "pass", "realm"))
    cl = await aiohttp_client(app)
    resp = await cl.get("/", auth=aiohttp.BasicAuth("user", "pass"))
    assert resp.status == 200


async def test_basic_auth_request_auth(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, BasicAuth("user", "pass", "realm"))
    cl = await aiohttp_client(app)
    resp = await cl.get("/")
    assert resp.status == 401
    assert resp.headers["WWW-Authenticate"] == "Basic realm=realm"


async def test_basic_auth_wrong_creds(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, BasicAuth("user", "pass", "realm"))
    cl = await aiohttp_client(app)
    resp = await cl.get("/", auth=aiohttp.BasicAuth("user", "badpass"))
    assert resp.status == 401
    assert resp.headers["WWW-Authenticate"] == "Basic realm=realm"


async def test_basic_auth_malformed_req(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, BasicAuth("user", "pass", "realm"))
    cl = await aiohttp_client(app)
    resp = await cl.get("/", headers={"Authorization": "Basic nonbase64"})
    assert resp.status == 401
    assert resp.headers["WWW-Authenticate"] == "Basic realm=realm"


async def test_basic_auth_malformed_req2(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, BasicAuth("user", "pass", "realm"))
    cl = await aiohttp_client(app)
    resp = await cl.get("/", headers={"Authorization": "Basic nonbase64"})
    assert resp.status == 401
    assert resp.headers["WWW-Authenticate"] == "Basic realm=realm"


async def test_basic_auth_white_path(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, BasicAuth("user", "pass", "realm", white_paths=["/"]))
    cl = await aiohttp_client(app)
    resp = await cl.get("/")
    assert resp.status == 200
