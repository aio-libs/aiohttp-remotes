import pytest
from typing_extensions import NoReturn

from aiohttp import web
from aiohttp.pytest_plugin import AiohttpClient
from aiohttp_remotes import ForwardedRelaxed, ForwardedStrict, setup as _setup
from aiohttp_remotes.forwarded import _parse_forwarded_for


async def test_forwarded_relaxed_ok(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.host == "example.com"
        assert request.scheme == "https"
        assert request.secure
        assert request.remote == "10.10.10.10"

        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedRelaxed())
    cl = await aiohttp_client(app)
    hdr_val = "; ".join(["for=10.10.10.10", "proto=https", "host=example.com"])
    async with cl.get("/", headers={"Forwarded": hdr_val}) as resp:
        assert resp.status == 200


async def test_forwarded_relaxed_no_for(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.host == "example.com"
        assert request.scheme == "https"
        assert request.secure
        assert request.remote == "127.0.0.1"

        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedRelaxed())
    cl = await aiohttp_client(app)
    hdr_val = "; ".join(["proto=https", "host=example.com"])
    async with cl.get("/", headers={"Forwarded": hdr_val}) as resp:
        assert resp.status == 200


async def test_forwarded_relaxed_no_proto(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.host == "example.com"
        assert request.scheme == "http"
        assert not request.secure
        assert request.remote == "10.10.10.10"

        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedRelaxed())
    cl = await aiohttp_client(app)
    hdr_val = "; ".join(["for=10.10.10.10", "host=example.com"])
    resp = await cl.get("/", headers={"Forwarded": hdr_val})
    assert resp.status == 200


async def test_forwarded_relaxed_no_host(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        url = cl.make_url("/")
        assert url.host is not None
        host = url.host + ":" + str(url.port)
        assert request.host == host
        assert request.scheme == "https"
        assert request.secure
        assert request.remote == "10.10.10.10"

        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedRelaxed())
    cl = await aiohttp_client(app)
    hdr_val = "; ".join(["for=10.10.10.10", "proto=https"])
    async with cl.get("/", headers={"Forwarded": hdr_val}) as resp:
        assert resp.status == 200


async def test_forwarded_relaxed_many_hosts(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.host == "example.com"
        assert request.scheme == "https"
        assert request.secure
        assert request.remote == "10.10.10.10"

        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedRelaxed())
    cl = await aiohttp_client(app)
    hdr_val1 = "; ".join(["for=20.20.20.20", "proto=http", "host=example.org"])
    hdr_val2 = "; ".join(["for=10.10.10.10", "proto=https", "host=example.com"])
    hdr_val = ", ".join([hdr_val1, hdr_val2])
    async with cl.get("/", headers={"Forwarded": hdr_val}) as resp:
        assert resp.status == 200


async def test_forwarded_strict_ok(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.host == "example.com"
        assert request.scheme == "https"
        assert request.secure
        assert request.remote == "10.10.10.10"

        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["127.0.0.1"]]))
    cl = await aiohttp_client(app)
    hdr_val = "; ".join(["for=10.10.10.10", "proto=https", "host=example.com"])
    async with cl.get("/", headers={"Forwarded": hdr_val}) as resp:
        assert resp.status == 200


@pytest.mark.parametrize(
    "node,remote",
    [
        ("192.0.2.43", "192.0.2.43"),
        ("2001:db8::1", "2001:db8::1"),
        ("2001:db8::1:443", "2001:db8::1:443"),
        ("fe80::1%eth0", "fe80::1%eth0"),
        ("[2001:db8::1]", "2001:db8::1"),
        ("[2001:DB8:0:0:0:0:0:1]:443", "2001:db8::1"),
        ("[::ffff:192.0.2.1]:443", "::ffff:c000:201"),
        ("192.0.2.43:443", "192.0.2.43"),
        ("[2001:db8::1]:0", "2001:db8::1"),
        ("192.0.2.43:99999", "192.0.2.43"),
        ("[2001:db8::1]:_port.1_-", "2001:db8::1"),
        ("192.0.2.43:_port.1_-", "192.0.2.43"),
    ],
)
async def test_forwarded_strict_ip_node(
    aiohttp_client: AiohttpClient, node: str, remote: str
) -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.remote == remote
        assert request.scheme == "https"
        assert request.host == "example.com"
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["127.0.0.1"]]))
    client = await aiohttp_client(app)
    async with client.get(
        "/", headers={"Forwarded": f'for="{node}";proto=https;host=example.com'}
    ) as response:
        assert response.status == 200


@pytest.mark.parametrize(
    "node",
    [
        "unknown",
        "_hidden",
        "[192.0.2.43]",
        "[]",
        "[invalid]",
        "[2001:db8::1",
        "2001:db8::1]",
        "[2001:db8::1]junk",
        "[2001:db8::1]:",
        "192.0.2.43:",
        "[2001:db8::1]:123456",
        "192.0.2.43:123456",
        "192.0.2.43:443trailer",
        "192.0.2.43:443:extra",
        "[2001:db8::1]:-1",
        "[2001:db8::1]:_",
        "[2001:db8::1]:_bad+port",
        "[2001:db8::1]:\u0664\u0664\u0663",
        "[fe80::1%eth0]",
    ],
)
async def test_forwarded_strict_invalid_node(
    aiohttp_client: AiohttpClient, node: str
) -> None:
    async def handler(request: web.Request) -> web.Response:
        pytest.fail("Invalid Forwarded node reached the handler")

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["127.0.0.1"]]))
    client = await aiohttp_client(app)
    async with client.get("/", headers={"Forwarded": f'for="{node}"'}) as response:
        assert response.status == 400


@pytest.mark.parametrize(
    "node", ["[2001:db8::1]", "[2001:db8::1]:443", "192.0.2.43:443"]
)
async def test_forwarded_strict_ip_node_untrusted(
    aiohttp_client: AiohttpClient, node: str
) -> None:
    async def handler(request: web.Request) -> web.Response:
        pytest.fail("Untrusted proxy reached the handler")

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["192.0.2.10"]]))
    client = await aiohttp_client(app)
    async with client.get("/", headers={"Forwarded": f'for="{node}"'}) as response:
        assert response.status == 400


@pytest.mark.parametrize(
    "node", ["192.0.2.43:\u0664\u0664\u0663", "[2001:db8::1]:\u0664\u0664\u0663"]
)
def test_forwarded_strict_ip_node_non_ascii_port(node: str) -> None:
    # aiohttp rejects these before middleware; check the parsed-node boundary too.
    with pytest.raises(ValueError):
        _parse_forwarded_for(node)


async def test_forwarded_strict_error_hook(aiohttp_client: AiohttpClient) -> None:
    class CustomError(ForwardedStrict):
        async def raise_error(self, request: web.Request) -> NoReturn:
            raise web.HTTPUnprocessableEntity()

    async def handler(request: web.Request) -> web.Response:
        pytest.fail("Invalid Forwarded node reached the handler")

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, CustomError([["127.0.0.1"]]))
    client = await aiohttp_client(app)
    async with client.get("/", headers={"Forwarded": 'for="[invalid]"'}) as response:
        assert response.status == 422


async def test_forwarded_strict_node_whitelist(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.remote == "127.0.0.1"
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["192.0.2.10"]], white_paths=["/"]))
    client = await aiohttp_client(app)
    async with client.get("/", headers={"Forwarded": 'for="[invalid]"'}) as response:
        assert response.status == 200


async def test_forwarded_strict_no_proto(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.host == "example.com"
        assert request.scheme == "http"
        assert request.remote == "10.10.10.10"

        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["127.0.0.1"]]))
    cl = await aiohttp_client(app)
    hdr_val = "; ".join(["for=10.10.10.10", "host=example.com"])
    async with cl.get("/", headers={"Forwarded": hdr_val}) as resp:
        assert resp.status == 200


async def test_forwarded_strict_no_host(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.host.startswith("127.0.0.1:")
        assert request.scheme == "https"
        assert request.remote == "10.10.10.10"

        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["127.0.0.1"]]))
    cl = await aiohttp_client(app)
    hdr_val = "; ".join(["for=10.10.10.10", "proto=https"])
    async with cl.get("/", headers={"Forwarded": hdr_val}) as resp:
        assert resp.status == 200


async def test_forwarded_strict_too_many_protos(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["127.0.0.1"]]))
    cl = await aiohttp_client(app)
    hdr1_val = "; ".join(["for=10.10.10.10", "proto=https"])
    hdr2_val = "; ".join(["for=20.20.20.20", "proto=http"])
    hdr_val = ", ".join([hdr1_val, hdr2_val])
    async with cl.get("/", headers={"Forwarded": hdr_val}) as resp:
        assert resp.status == 400


async def test_forwarded_strict_too_many_for(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["127.0.0.1"]]))
    cl = await aiohttp_client(app)
    resp = await cl.get("/", headers={"Forwarded": "for=10.10.10.10, for=11.11.11.11"})
    assert resp.status == 400


async def test_forwarded_strict_untrusted_ip(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["20.20.20.20"]]))
    cl = await aiohttp_client(app)
    async with cl.get("/", headers={"Forwarded": "for=10.10.10.10"}) as resp:
        assert resp.status == 400


async def test_forwarded_strict_whitelist(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.remote == "127.0.0.1"
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["20.20.20.20"]], white_paths=["/"]))
    cl = await aiohttp_client(app)
    async with cl.get("/", headers={"Forwarded": "for=10.10.10.10"}) as resp:
        assert resp.status == 200


async def test_forwarded_strict_no_for(aiohttp_client: AiohttpClient) -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = web.Application()
    app.router.add_get("/", handler)
    await _setup(app, ForwardedStrict([["127.0.0.1"], ["10.10.10.10"]]))
    cl = await aiohttp_client(app)
    hdr_val = ", ".join(["for=10.10.10.10", "proto=https"])
    resp = await cl.get("/", headers={"Forwarded": hdr_val})
    assert resp.status == 400
