def test_list_products(client):
    r = client.get("/products")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert len(data["items"]) == 1


def test_list_products_filter_brand(client):
    r = client.get("/products?brand=frankies-bikinis")
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1


def test_list_products_filter_no_match(client):
    r = client.get("/products?brand=triangl")
    assert r.status_code == 200
    assert len(r.json()["items"]) == 0


def test_list_products_filter_price(client):
    r = client.get("/products?min_price=50&max_price=200")
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1


def test_get_product_by_id(client):
    r = client.get("/products/frankies_sku001")
    assert r.status_code == 200
    assert r.json()["id"] == "frankies_sku001"


def test_get_product_not_found(client):
    r = client.get("/products/does_not_exist")
    assert r.status_code == 404
