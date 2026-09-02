import httpx

from infrawatch.checks import check_dns, check_http


def test_http_ok(httpx_mock):
    httpx_mock.add_response(status_code=200)
    r = check_http({"name": "x", "url": "https://x.com"})
    assert r.ok
    assert "200" in r.detail


def test_http_status_inesperado(httpx_mock):
    httpx_mock.add_response(status_code=500)
    r = check_http({"name": "x", "url": "https://x.com", "expect_status": 200})
    assert not r.ok


def test_http_sem_resposta(httpx_mock):
    httpx_mock.add_exception(httpx.ConnectError("recusou"))
    r = check_http({"name": "x", "url": "https://x.com"})
    assert not r.ok
    assert "não respondeu" in r.detail


def test_dns_resolve():
    assert check_dns({"name": "local", "host": "localhost"}).ok


def test_dns_nao_resolve():
    assert not check_dns({"name": "x", "host": "nao-existe-mesmo.invalid"}).ok