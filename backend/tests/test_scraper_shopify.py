import json
from unittest.mock import patch, MagicMock
from pipeline.scrapers.shopify import scrape_shopify

FAKE_PRODUCT = {
    "id": 123456,
    "title": "Malibu Triangle Top",
    "handle": "malibu-triangle-top",
    "product_type": "Bikini Top",
    "tags": ["swim", "top"],
    "images": [{"src": "https://cdn.shopify.com/img.jpg"}],
    "options": [
        {"name": "Color", "position": 1},
        {"name": "Size", "position": 2},
    ],
    "variants": [
        {
            "sku": "MAL-BLK-XS",
            "price": "98.00",
            "compare_at_price": None,
            "option1": "Black",
            "option2": "XS",
            "available": True,
        },
        {
            "sku": "MAL-BLK-S",
            "price": "98.00",
            "compare_at_price": None,
            "option1": "Black",
            "option2": "S",
            "available": True,
        },
        {
            "sku": "MAL-WHT-XS",
            "price": "98.00",
            "compare_at_price": None,
            "option1": "White",
            "option2": "XS",
            "available": False,
        },
    ],
}

FAKE_SALE_PRODUCT = {
    "id": 789,
    "title": "Rio Set",
    "handle": "rio-set",
    "product_type": "Bikini Set",
    "tags": [],
    "images": [{"src": "https://cdn.shopify.com/rio.jpg"}],
    "options": [{"name": "Size", "position": 1}],
    "variants": [
        {
            "sku": "RIO-S",
            "price": "60.00",
            "compare_at_price": "120.00",
            "option1": "S",
            "available": True,
        }
    ],
}


def _mock_response(products, status=200):
    mock = MagicMock()
    mock.status_code = status
    mock.json.return_value = {"products": products}
    return mock


def test_scrape_returns_products():
    with patch("pipeline.scrapers.shopify.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response([FAKE_PRODUCT]),
            _mock_response([]),
        ]
        results = scrape_shopify("www.frankiesbikinis.com", "Frankies Bikinis", "frankies-bikinis", delay=0)

    assert len(results) == 1
    p = results[0]
    assert p.id == "frankies-bikinis_MAL-BLK-XS"
    assert p.brand == "Frankies Bikinis"
    assert p.brand_slug == "frankies-bikinis"
    assert p.name == "Malibu Triangle Top"
    assert p.price == 98.0
    assert p.sale_price is None
    assert p.image_url == "https://cdn.shopify.com/img.jpg"
    assert p.affiliate_url == "https://www.frankiesbikinis.com/products/malibu-triangle-top"
    assert p.style == "top"
    assert "Black" in p.colors
    assert "White" in p.colors
    assert "XS" in p.sizes
    assert "S" in p.sizes
    assert p.in_stock is True


def test_scrape_detects_sale_price():
    with patch("pipeline.scrapers.shopify.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response([FAKE_SALE_PRODUCT]),
            _mock_response([]),
        ]
        results = scrape_shopify("www.example.com", "Brand", "brand", delay=0)

    p = results[0]
    assert p.price == 120.0
    assert p.sale_price == 60.0
    assert p.style == "set"


def test_scrape_stops_on_non_200():
    with patch("pipeline.scrapers.shopify.requests.get") as mock_get:
        mock_get.return_value = _mock_response([], status=403)
        results = scrape_shopify("www.example.com", "Brand", "brand", delay=0)
    assert results == []


def test_scrape_deduplicates_colors():
    with patch("pipeline.scrapers.shopify.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response([FAKE_PRODUCT]),
            _mock_response([]),
        ]
        results = scrape_shopify("www.example.com", "Brand", "brand", delay=0)
    colors = results[0].colors
    assert colors.count("Black") == 1


def test_scrape_paginates():
    product_a = {**FAKE_PRODUCT, "id": 1, "variants": [{**FAKE_PRODUCT["variants"][0], "sku": "A"}]}
    product_b = {**FAKE_PRODUCT, "id": 2, "handle": "other", "variants": [{**FAKE_PRODUCT["variants"][0], "sku": "B"}]}
    with patch("pipeline.scrapers.shopify.requests.get") as mock_get:
        # Page 1: full (250 items) → scraper continues to page 2
        # Page 2: partial (1 item) → scraper breaks (len < 250), no page 3 fetched
        mock_get.side_effect = [
            _mock_response([product_a] * 250),
            _mock_response([product_b]),
        ]
        results = scrape_shopify("www.example.com", "Brand", "brand", delay=0)
    assert len(results) == 251
