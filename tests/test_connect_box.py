import base64
import os
import pytest

from aiohttp import web, ClientResponseError
from pathlib import Path

from arris_tg2492lg.connect_box import ConnectBox
from arris_tg2492lg.exception import InvalidCredentialError


async def test_async_login_ok(aiohttp_client, loop):
    app = web.Application(loop=loop)
    app.router.add_get("/login", _get_credential)
    client = await aiohttp_client(app)

    connect_box = ConnectBox(client.session, f"http://{client.host}:{client.port}", "secret")
    token = await connect_box.async_login()

    assert token == "eyJuYW1lIjogImFkbWluIn0="  # base64 representation of: {"name": "admin"}


async def test_async_login_nok_wrong_password(aiohttp_client, loop):
    """Test when an invalid password is provided.

    The router responds with an Internal Server Error when a wrong password is provided.
    """

    def internal_server_error(request):
        return web.Response(status=500)

    app = web.Application(loop=loop)
    app.router.add_get("/login", internal_server_error)
    client = await aiohttp_client(app)

    connect_box = ConnectBox(client.session, f"http://{client.host}:{client.port}", "wrong")

    with pytest.raises(ClientResponseError):
        await connect_box.async_login()


async def test_async_login_nok_html_response(aiohttp_client, loop):
    """Test when an invalid endpoint is used.

    An unsupported browser could respond with html.
    """

    def get_html_response(request):
        html_response = "<!DOCTYPE html><html><body>hello</body></html>"
        return web.Response(text=html_response)

    app = web.Application(loop=loop)
    app.router.add_get("/login", get_html_response)
    client = await aiohttp_client(app)

    connect_box = ConnectBox(client.session, f"http://{client.host}:{client.port}", "secret")

    with pytest.raises(InvalidCredentialError):
        await connect_box.async_login()


async def test_get_connected_devices(aiohttp_client, loop):
    app = web.Application(loop=loop)
    app.router.add_get("/login", _get_credential)
    app.router.add_get("/getConnDevices", _get_mock_data)
    client = await aiohttp_client(app)

    connect_box = ConnectBox(client.session, f"http://{client.host}:{client.port}", "secret")
    connected_devices = await connect_box.async_get_connected_devices()

    assert len(connected_devices) == 4


async def test_get_connected_devices_throws_401_once(aiohttp_client, loop):
    def login_result(request):
        login_result.call_count += 1
        return _get_credential(request)

    def conn_devices_result(request):
        conn_devices_result.call_count += 1
        if conn_devices_result.call_count == 1:
            return web.Response(status=401)
        else:
            return _get_mock_data(request)

    login_result.call_count = 0
    conn_devices_result.call_count = 0

    app = web.Application(loop=loop)
    app.router.add_get("/login", login_result)
    app.router.add_get("/getConnDevices", conn_devices_result)
    client = await aiohttp_client(app)

    connect_box = ConnectBox(client.session, f"http://{client.host}:{client.port}", "secret")
    connected_devices = await connect_box.async_get_connected_devices()

    assert len(connected_devices) == 4

    assert login_result.call_count == 2
    assert conn_devices_result.call_count == 2


async def test_get_connected_devices_throws_401_twice(aiohttp_client, loop):
    def login_result(request):
        login_result.call_count += 1
        return _get_credential(request)

    def conn_devices_result(request):
        conn_devices_result.call_count += 1
        return web.Response(status=401)

    login_result.call_count = 0
    conn_devices_result.call_count = 0

    app = web.Application(loop=loop)
    app.router.add_get("/login", login_result)
    app.router.add_get("/getConnDevices", conn_devices_result)
    client = await aiohttp_client(app)

    connect_box = ConnectBox(client.session, f"http://{client.host}:{client.port}", "secret")

    with pytest.raises(ClientResponseError):
        await connect_box.async_get_connected_devices()

    assert login_result.call_count == 2
    assert conn_devices_result.call_count == 2


async def test_logout_accepts_http_status_500(aiohttp_client, loop):
    def get_logout_success(request):
        get_logout_success.call_count += 1
        return web.Response(status=500)

    get_logout_success.call_count = 0

    app = web.Application(loop=loop)
    app.router.add_get("/login", _get_credential)
    app.router.add_get("/logout", get_logout_success)
    client = await aiohttp_client(app)

    connect_box = ConnectBox(client.session, f"http://{client.host}:{client.port}", "secret")
    await connect_box.async_logout()

    assert get_logout_success.call_count == 1


async def test_logout_throws_for_401_unauthorized(aiohttp_client, loop):
    async def get_logout_failure(request):
        get_logout_failure.call_count += 1
        return web.Response(status=401)

    get_logout_failure.call_count = 0

    app = web.Application(loop=loop)
    app.router.add_get("/login", _get_credential)
    app.router.add_get("/logout", get_logout_failure)
    client = await aiohttp_client(app)

    connect_box = ConnectBox(client.session, f"http://{client.host}:{client.port}", "secret")

    with pytest.raises(ClientResponseError):
        await connect_box.async_logout()

    assert get_logout_failure.call_count == 1


async def test_get_router_information(aiohttp_client, loop):
    app = web.Application(loop=loop)
    app.router.add_get("/login", _get_credential)
    app.router.add_get("/snmpGet", _get_mock_router_information)
    client = await aiohttp_client(app)

    connect_box = ConnectBox(client.session, f"http://{client.host}:{client.port}", "secret")
    router_information = await connect_box.async_get_router_information()

    assert router_information.mac_address == "12:34:56:78:90:ab"
    assert router_information.hardware_version == "10"
    assert router_information.software_version == "9.1.2103.102"
    assert router_information.serial_number == "ABCD12345678"


def _get_credential(request):
    dummy_token = base64.b64encode('{"name": "admin"}'.encode("utf-8")).decode("ascii")

    return web.Response(text=dummy_token)


def _get_mock_data(request):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    test_data_path = current_path / "getConnDevices-response.json"

    return web.Response(text=test_data_path.read_text())


def _get_mock_router_information(request):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    test_data_path = current_path / "snmpGet-response.json"

    return web.Response(text=test_data_path.read_text())
