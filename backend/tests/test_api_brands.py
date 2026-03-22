def test_get_brands(client):
    r = client.get("/brands")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert data[0]["brand_slug"] == "frankies-bikinis"
    assert data[0]["product_count"] == 1
