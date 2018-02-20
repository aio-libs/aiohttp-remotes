from aiohttp import web
from aiohttp_remotes import XForwardedRelaxed, XForwardedStrict
from aiohttp_remotes import setup as _setup


async def test_x_forwarded_relaxed_ok(test_client):
    async def handler(request):
        assert request.host == 'example.com'
        assert request.scheme == 'https'
        assert request.secure
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedRelaxed())
    cl = await test_client(app)
    resp = await cl.get('/', headers={'X-Forwarded-For': '10.10.10.10',
                                      'X-Forwarded-Proto': 'https',
                                      'X-Forwarded-Host': 'example.com'})
    assert resp.status == 200


async def test_x_forwarded_relaxed_no_forwards(test_client):
    async def handler(request):
        url = cl.make_url('/')
        host = url.host + ':' + str(url.port)
        assert request.host == host
        assert request.scheme == 'http'
        assert not request.secure
        assert request.remote == '127.0.0.1'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedRelaxed())
    cl = await test_client(app)
    resp = await cl.get('/')
    assert resp.status == 200


async def test_x_forwarded_relaxed_multiple_for(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedRelaxed())
    cl = await test_client(app)
    resp = await cl.get('/', headers=[('X-Forwarded-For', '10.10.10.10'),
                                      ('X-Forwarded-For', '20.20.20.20'),
                                      ('X-Forwarded-Proto', 'https'),
                                      ('X-Forwarded-Host', 'example.com')])
    assert resp.status == 400


async def test_x_forwarded_relaxed_multiple_proto(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedRelaxed())
    cl = await test_client(app)
    resp = await cl.get('/', headers=[('X-Forwarded-For', '10.10.10.10'),
                                      ('X-Forwarded-Proto', 'http'),
                                      ('X-Forwarded-Proto', 'https'),
                                      ('X-Forwarded-Host', 'example.com')])
    assert resp.status == 400


async def test_x_forwarded_relaxed_multiple_host(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedRelaxed())
    cl = await test_client(app)
    resp = await cl.get('/', headers=[('X-Forwarded-For', '10.10.10.10'),
                                      ('X-Forwarded-Proto', 'http'),
                                      ('X-Forwarded-Host', 'example.org'),
                                      ('X-Forwarded-Host', 'example.com')])
    assert resp.status == 400


async def test_x_forwarded_strict_ok(test_client):
    async def handler(request):
        assert request.host == 'example.com'
        assert request.scheme == 'https'
        assert request.secure
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    resp = await cl.get('/', headers={'X-Forwarded-For': '10.10.10.10',
                                      'X-Forwarded-Proto': 'https',
                                      'X-Forwarded-Host': 'example.com'})
    assert resp.status == 200


async def test_x_forwarded_strict_no_proto(test_client):
    async def handler(request):
        assert request.host == 'example.com'
        assert request.scheme == 'http'
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    resp = await cl.get('/', headers={'X-Forwarded-For': '10.10.10.10',
                                      'X-Forwarded-Host': 'example.com'})
    assert resp.status == 200


async def test_x_forwarded_strict_no_host(test_client):
    async def handler(request):
        assert request.host.startswith('127.0.0.1:')
        assert request.scheme == 'https'
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    resp = await cl.get('/', headers={'X-Forwarded-For': '10.10.10.10',
                                      'X-Forwarded-Proto': 'https'})
    assert resp.status == 200


async def test_x_forwarded_strict_too_many_headers(test_client):
    async def handler(request):
        assert request.host == 'example.com'
        assert request.scheme == 'https'
        assert request.secure
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    resp = await cl.get('/', headers=[('X-Forwarded-For', '10.10.10.10'),
                                      ('X-Forwarded-Proto', 'https'),
                                      ('X-Forwarded-Proto', 'http'),
                                      ('X-Forwarded-Host', 'example.com')])
    assert resp.status == 400


async def test_x_forwarded_strict_too_many_protos(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    resp = await cl.get('/',
                        headers={'X-Forwarded-For': '10.10.10.10',
                                 'X-Forwarded-Proto': 'https, http, https'})
    assert resp.status == 400


async def test_x_forwarded_strict_too_many_for(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    resp = await cl.get('/',
                        headers={'X-Forwarded-For':
                                 '10.10.10.10, 11.11.11.11'})
    assert resp.status == 400


async def test_x_forwarded_strict_untrusted_ip(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedStrict([['20.20.20.20']]))
    cl = await test_client(app)
    resp = await cl.get('/',
                        headers={'X-Forwarded-For': '10.10.10.10'})
    assert resp.status == 400


async def test_x_forwarded_strict_whitelist(test_client):
    async def handler(request):
        assert request.remote == '127.0.0.1'
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, XForwardedStrict([['20.20.20.20']], white_paths=['/']))
    cl = await test_client(app)
    resp = await cl.get('/',
                        headers={'X-Forwarded-For': '10.10.10.10'})
    assert resp.status == 200
