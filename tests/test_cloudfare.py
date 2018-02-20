import asyncio
import pathlib
import socket
import ssl

import aiohttp
import pytest
from aiohttp import web
from aiohttp.abc import AbstractResolver
from aiohttp.resolver import DefaultResolver
from aiohttp.test_utils import unused_port
from aiohttp_remotes import Cloudflare
from aiohttp_remotes import setup as _setup


class FakeResolver(AbstractResolver):
    _LOCAL_HOST = {0: '127.0.0.1',
                   socket.AF_INET: '127.0.0.1',
                   socket.AF_INET6: '::1'}

    def __init__(self, fakes, *, loop):
        """fakes -- dns -> port dict"""
        self._fakes = fakes
        self._resolver = DefaultResolver(loop=loop)

    async def resolve(self, host, port=0, family=socket.AF_INET):
        fake_port = self._fakes.get(host)
        if fake_port is not None:
            return [{'hostname': host,
                     'host': self._LOCAL_HOST[family], 'port': fake_port,
                     'family': family, 'proto': 0,
                     'flags': socket.AI_NUMERICHOST}]
        else:
            return await self._resolver.resolve(host, port, family)

    async def close(self):
        await self._resolver.close()


class FakeCloudfare:
    def __init__(self, *, ipv4=['127.0.0.0/16'], ipv6=['::/16']):
        self._ipv4 = ipv4
        self._ipv6 = ipv6
        self.loop = asyncio.get_event_loop()
        self.app = web.Application()
        self.app.router.add_get('/ips-v4', self.ipv4)
        self.app.router.add_get('/ips-v6', self.ipv6)

        self.handler = None
        self.server = None
        here = pathlib.Path(__file__)
        ssl_cert = here.parent / 'sample.crt'
        ssl_key = here.parent / 'sample.key'
        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.load_cert_chain(str(ssl_cert), str(ssl_key))

    async def start(self):
        port = unused_port()
        self.handler = self.app.make_handler()
        self.server = await self.loop.create_server(self.handler,
                                                    '127.0.0.1', port,
                                                    ssl=self.ssl_context)
        return {'www.cloudflare.com': port}

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()
        await self.app.shutdown()
        await self.handler.shutdown()
        await self.app.cleanup()

    async def ipv4(self, request):
        return web.Response(text='\n'.join(self._ipv4))

    async def ipv6(self, request):
        return web.Response(text='\n'.join(self._ipv6))


@pytest.fixture
def cloudfare_session(loop):
    sessions = []

    async def go(**kwargs):
        fake = FakeCloudfare(**kwargs)
        info = await fake.start()
        resolver = FakeResolver(info, loop=asyncio.get_event_loop())
        connector = aiohttp.TCPConnector(resolver=resolver,
                                         verify_ssl=False)

        session = aiohttp.ClientSession(connector=connector)
        sessions.append(session)
        return session

    yield go

    for s in sessions:
        loop.run_until_complete(s.close())


async def test_cloudfare_ok(test_client, cloudfare_session):
    async def handler(request):
        assert request.remote == '10.10.10.10'

        return web.Response()

    cf_client = await cloudfare_session()

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, Cloudflare(cf_client))
    cl = await test_client(app)
    resp = await cl.get('/', headers={'CF-CONNECTING-IP': '10.10.10.10'})
    assert resp.status == 200


async def test_cloudfare_no_networks(test_client, cloudfare_session):
    cf_client = await cloudfare_session(ipv4=[], ipv6=[])

    app = web.Application()
    with pytest.raises(RuntimeError):
        await _setup(app, Cloudflare(cf_client))


async def test_cloudfare_not_cloudfare(test_client, cloudfare_session):
    async def handler(request):
        return web.Response()

    cf_client = await cloudfare_session(ipv4=['10.0.0.0'], ipv6=['10::'])

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, Cloudflare(cf_client))
    cl = await test_client(app)
    resp = await cl.get('/', headers={'CF-CONNECTING-IP': '10.10.10.10'})
    assert resp.status == 400


async def test_cloudfare_garbage_config(test_client, cloudfare_session):
    async def handler(request):
        assert request.remote == '10.10.10.10'

        return web.Response()

    cf_client = await cloudfare_session(ipv4=['127.0.0.0/16', 'garbage'])

    app = web.Application()
    app.router.add_get('/', handler)
    await _setup(app, Cloudflare(cf_client))
    cl = await test_client(app)
    resp = await cl.get('/', headers={'CF-CONNECTING-IP': '10.10.10.10'})
    assert resp.status == 200
