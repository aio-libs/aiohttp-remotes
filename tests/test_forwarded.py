from aiohttp import web
from aiohttp_remotes import ForwardedRelaxed, ForwardedStrict
from aiohttp_remotes import setup as _setup


async def test_forwarded_relaxed_ok(test_client):
    async def handler(request):
        assert request.host == 'example.com'
        assert request.scheme == 'https'
        assert request.secure
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedRelaxed())
    cl = await test_client(app)
    hdr_val = '; '.join(['for=10.10.10.10',
                         'proto=https',
                         'host=example.com'])
    resp = await cl.get('/', headers={'Forwarded': hdr_val})
    assert resp.status == 200


async def test_forwarded_relaxed_no_for(test_client):
    async def handler(request):
        assert request.host == 'example.com'
        assert request.scheme == 'https'
        assert request.secure
        assert request.remote == '127.0.0.1'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedRelaxed())
    cl = await test_client(app)
    hdr_val = '; '.join(['proto=https',
                        'host=example.com'])
    resp = await cl.get('/', headers={'Forwarded': hdr_val})
    assert resp.status == 200


async def test_forwarded_relaxed_no_proto(test_client):
    async def handler(request):
        assert request.host == 'example.com'
        assert request.scheme == 'http'
        assert not request.secure
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedRelaxed())
    cl = await test_client(app)
    hdr_val = '; '.join(['for=10.10.10.10',
                        'host=example.com'])
    resp = await cl.get('/', headers={'Forwarded': hdr_val})
    assert resp.status == 200


async def test_forwarded_relaxed_no_host(test_client):
    async def handler(request):
        url = cl.make_url('/')
        host = url.host + ':' + str(url.port)
        assert request.host == host
        assert request.scheme == 'https'
        assert request.secure
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedRelaxed())
    cl = await test_client(app)
    hdr_val = '; '.join(['for=10.10.10.10',
                        'proto=https'])
    resp = await cl.get('/', headers={'Forwarded': hdr_val})
    assert resp.status == 200


async def test_forwarded_relaxed_many_hosts(test_client):
    async def handler(request):
        assert request.host == 'example.com'
        assert request.scheme == 'https'
        assert request.secure
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedRelaxed())
    cl = await test_client(app)
    hdr_val1 = '; '.join(['for=20.20.20.20',
                          'proto=http',
                          'host=example.org'])
    hdr_val2 = '; '.join(['for=10.10.10.10',
                          'proto=https',
                          'host=example.com'])
    hdr_val = ', '.join([hdr_val1, hdr_val2])
    resp = await cl.get('/', headers={'Forwarded': hdr_val})
    assert resp.status == 200


async def test_forwarded_strict_ok(test_client):
    async def handler(request):
        assert request.host == 'example.com'
        assert request.scheme == 'https'
        assert request.secure
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    hdr_val = '; '.join(['for=10.10.10.10',
                         'proto=https',
                         'host=example.com'])
    resp = await cl.get('/', headers={'Forwarded': hdr_val})
    assert resp.status == 200


async def test_forwarded_strict_no_proto(test_client):
    async def handler(request):
        assert request.host == 'example.com'
        assert request.scheme == 'http'
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    hdr_val = '; '.join(['for=10.10.10.10',
                         'host=example.com'])
    resp = await cl.get('/', headers={'Forwarded': hdr_val})
    assert resp.status == 200


async def test_forwarded_strict_no_host(test_client):
    async def handler(request):
        assert request.host.startswith('127.0.0.1:')
        assert request.scheme == 'https'
        assert request.remote == '10.10.10.10'

        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    hdr_val = '; '.join(['for=10.10.10.10',
                         'proto=https'])
    resp = await cl.get('/', headers={'Forwarded': hdr_val})
    assert resp.status == 200


async def test_forwarded_strict_too_many_protos(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    hdr1_val = '; '.join(['for=10.10.10.10',
                          'proto=https'])
    hdr2_val = '; '.join(['for=20.20.20.20',
                          'proto=http'])
    hdr_val = ', '.join([hdr1_val, hdr2_val])
    resp = await cl.get('/', headers={'Forwarded': hdr_val})
    assert resp.status == 400


async def test_forwarded_strict_too_many_for(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedStrict([['127.0.0.1']]))
    cl = await test_client(app)
    resp = await cl.get('/',
                        headers={'Forwarded':
                                 'for=10.10.10.10, for=11.11.11.11'})
    assert resp.status == 400


async def test_forwarded_strict_untrusted_ip(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedStrict([['20.20.20.20']]))
    cl = await test_client(app)
    resp = await cl.get('/',
                        headers={'Forwarded': 'for=10.10.10.10'})
    assert resp.status == 400


async def test_forwarded_strict_whitelist(test_client):
    async def handler(request):
        assert request.remote == '127.0.0.1'
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedStrict([['20.20.20.20']], white_paths=['/']))
    cl = await test_client(app)
    resp = await cl.get('/',
                        headers={'Forwarded': 'for=10.10.10.10'})
    assert resp.status == 200


async def test_forwarded_strict_no_for(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, ForwardedStrict([['127.0.0.1'], ['10.10.10.10']]))
    cl = await test_client(app)
    hdr_val = ', '.join(['for=10.10.10.10',
                         'proto=https'])
    resp = await cl.get('/', headers={'Forwarded': hdr_val})
    assert resp.status == 400
