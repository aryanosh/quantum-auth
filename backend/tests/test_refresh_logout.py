import pytest


@pytest.mark.xfail(reason="Backend does not implement /api/refresh yet")
def test_refresh_token_endpoint_exists(client):
    resp = client.post("/api/refresh")
    assert resp.status_code in (200, 401)


@pytest.mark.xfail(reason="Backend does not implement /api/logout yet (stateless JWT)")
def test_logout_endpoint_exists(client):
    resp = client.post("/api/logout")
    assert resp.status_code in (200, 401)

