def test_search_finds_product(client):
    r = client.get("/search?q=Malibu")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Malibu Top"

def test_search_no_results(client):
    r = client.get("/search?q=doesnotexist99")
    assert r.status_code == 200
    assert r.json()["items"] == []

def test_search_missing_query(client):
    r = client.get("/search")
    assert r.status_code == 422
