def test_click_returns_affiliate_url(client):
    r = client.post("/click/frankies_sku001")
    assert r.status_code == 200
    assert "affiliate_url" in r.json()

def test_click_not_found(client):
    r = client.post("/click/does_not_exist")
    assert r.status_code == 404
