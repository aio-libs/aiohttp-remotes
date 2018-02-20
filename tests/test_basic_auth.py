import base64

import aiohttp
from aiohttp import web
from aiohttp_remotes import BasicAuth
from aiohttp_remotes import setup as _setup


async def test_basic_auth_ok(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, BasicAuth('user', 'pass', 'realm'))
    cl = await test_client(app)
    resp = await cl.get('/', auth=aiohttp.BasicAuth('user', 'pass'))
    assert resp.status == 200


async def test_basic_auth_request_auth(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, BasicAuth('user', 'pass', 'realm'))
    cl = await test_client(app)
    resp = await cl.get('/')
    assert resp.status == 401
    assert resp.headers['WWW-Authenticate'] == 'Basic realm=realm'


async def test_basic_auth_wrong_creds(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, BasicAuth('user', 'pass', 'realm'))
    cl = await test_client(app)
    resp = await cl.get('/', auth=aiohttp.BasicAuth('user', 'badpass'))
    assert resp.status == 401
    assert resp.headers['WWW-Authenticate'] == 'Basic realm=realm'


async def test_basic_auth_malformed_req(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, BasicAuth('user', 'pass', 'realm'))
    cl = await test_client(app)
    resp = await cl.get('/', headers={'Authorization': 'Basic nonbase64'})
    assert resp.status == 401
    assert resp.headers['WWW-Authenticate'] == 'Basic realm=realm'


async def test_basic_auth_malformed_req2(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, BasicAuth('user', 'pass', 'realm'))
    cl = await test_client(app)
    resp = await cl.get('/', headers={'Authorization': 'Basic nonbase64'})
    assert resp.status == 401
    assert resp.headers['WWW-Authenticate'] == 'Basic realm=realm'


async def test_basic_auth_malformed_req3(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, BasicAuth('user', 'pass', 'realm'))
    cl = await test_client(app)
    creds = base64.encodestring(b'a:b:c').decode('utf-8')
    resp = await cl.get('/', headers={'Authorization': 'Basic '+creds})
    assert resp.status == 401
    assert resp.headers['WWW-Authenticate'] == 'Basic realm=realm'


async def test_basic_auth_white_path(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, BasicAuth('user', 'pass', 'realm', white_paths=['/']))
    cl = await test_client(app)
    resp = await cl.get('/')
    assert resp.status == 200
