import pathlib
import ssl

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from aiohttp_remotes import Secure
from aiohttp_remotes import setup as _setup
from yarl import URL


@pytest.fixture
def here():
    return pathlib.Path(__file__).parent


@pytest.fixture
def ssl_ctx(here):
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ssl_ctx.load_cert_chain(
        str(here / 'sample.crt'),
        str(here / 'sample.key')
    )
    return ssl_ctx


async def test_secure_ok(test_client, test_server, ssl_ctx):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, Secure())
    srv = await test_server(app, ssl=ssl_ctx)
    conn = aiohttp.TCPConnector(verify_ssl=False)
    cl = await test_client(srv, connector=conn)
    resp = await cl.get('/')
    print(resp.request_info.url)
    assert resp.status == 200
    assert resp.headers['X-Frame-Options'] == 'DENY'
    expected = 'max-age=31536000; includeSubDomains'
    assert resp.headers['Strict-Transport-Security'] == expected
    assert resp.headers['X-Content-Type-Options'] == 'nosniff'
    assert resp.headers['X-XSS-Protection'] == '1; mode=block'


async def test_secure_redirect(test_client, test_server, ssl_ctx):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    secure = Secure()
    await _setup(app, secure)
    http_srv = await test_server(app)
    https_srv = await test_server(app, ssl=ssl_ctx)
    secure._redirect_url = https_srv.make_url('/')
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(connector=conn) as cl:
        url = http_srv.make_url('/')
        resp = await cl.get(url)
        assert resp.status == 200
        assert resp.request_info.url.scheme == 'https'


async def test_secure_no_redirection(test_client):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, Secure(redirect=False))
    cl = await test_client(app)
    resp = await cl.get('/')
    assert resp.status == 400
    assert resp.request_info.url.scheme == 'http'


async def test_no_x_frame(test_client, test_server, ssl_ctx):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, Secure(x_frame=None))
    srv = await test_server(app, ssl=ssl_ctx)
    conn = aiohttp.TCPConnector(verify_ssl=False)
    cl = await test_client(srv, connector=conn)
    resp = await cl.get('/')
    print(resp.request_info.url)
    assert resp.status == 200
    assert 'X-Frame-Options' not in resp.headers
    expected = 'max-age=31536000; includeSubDomains'
    assert resp.headers['Strict-Transport-Security'] == expected
    assert resp.headers['X-Content-Type-Options'] == 'nosniff'
    assert resp.headers['X-XSS-Protection'] == '1; mode=block'


async def test_no_sts(test_client, test_server, ssl_ctx):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, Secure(sts=None))
    srv = await test_server(app, ssl=ssl_ctx)
    conn = aiohttp.TCPConnector(verify_ssl=False)
    cl = await test_client(srv, connector=conn)
    resp = await cl.get('/')
    print(resp.request_info.url)
    assert resp.status == 200
    assert resp.headers['X-Frame-Options'] == 'DENY'
    assert 'Strict-Transport-Security' not in resp.headers
    assert resp.headers['X-Content-Type-Options'] == 'nosniff'
    assert resp.headers['X-XSS-Protection'] == '1; mode=block'


async def test_no_cto(test_client, test_server, ssl_ctx):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, Secure(cto=None))
    srv = await test_server(app, ssl=ssl_ctx)
    conn = aiohttp.TCPConnector(verify_ssl=False)
    cl = await test_client(srv, connector=conn)
    resp = await cl.get('/')
    print(resp.request_info.url)
    assert resp.status == 200
    assert resp.headers['X-Frame-Options'] == 'DENY'
    expected = 'max-age=31536000; includeSubDomains'
    assert resp.headers['Strict-Transport-Security'] == expected
    assert 'X-Content-Type-Options' not in resp.headers
    assert resp.headers['X-XSS-Protection'] == '1; mode=block'


async def test_no_xss(test_client, test_server, ssl_ctx):
    async def handler(request):
        return web.Response()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, Secure(xss=None))
    srv = await test_server(app, ssl=ssl_ctx)
    conn = aiohttp.TCPConnector(verify_ssl=False)
    cl = await test_client(srv, connector=conn)
    resp = await cl.get('/')
    print(resp.request_info.url)
    assert resp.status == 200
    assert resp.headers['X-Frame-Options'] == 'DENY'
    expected = 'max-age=31536000; includeSubDomains'
    assert resp.headers['Strict-Transport-Security'] == expected
    assert resp.headers['X-Content-Type-Options'] == 'nosniff'
    assert 'X-XSS-Protection' not in resp.headers


async def test_default_redirect():
    s = Secure()

    async def handler(request):
        pass

    req = make_mocked_request('GET', '/path',
                              headers={'Host': 'example.com'})
    with pytest.raises(web.HTTPPermanentRedirect) as ctx:
        await s.middleware(req, handler)
    assert ctx.value.location == URL('https://example.com/path')


def test_non_https_redirect_url():
    with pytest.raises(ValueError):
        Secure(redirect_url='http://example.com')


def test_redirect_url_with_path():
    with pytest.raises(ValueError):
        Secure(redirect_url='https://example.com/path/to')


def test_redirect_url_ok():
    Secure(redirect_url='https://example.com')
