import pytest
from pathlib import Path
from pipeline.feed_parser import parse_csv_feed, normalize_brand_slug

FIXTURE = Path(__file__).parent / "fixtures" / "sample_feed.csv"

def test_normalize_brand_slug():
    assert normalize_brand_slug("Frankies Bikinis") == "frankies-bikinis"
    assert normalize_brand_slug("L*Space") == "l-space"
    assert normalize_brand_slug("Monday Swimwear") == "monday-swimwear"
    # Test adjacent-hyphen edge cases (Fix 4)
    assert normalize_brand_slug("Brand - Summer") == "brand-summer"
    assert normalize_brand_slug("L * Space") == "l-space"

def test_parse_csv_returns_products():
    products = parse_csv_feed(
        filepath=str(FIXTURE),
        brand="Test Brand",
        affiliate_prefix="https://track.com/?url=",
        column_map={
            "sku": "sku", "name": "name", "price": "price",
            "sale_price": "sale_price", "image_url": "image_url",
            "buy_url": "buy_url", "category": "category",
            "colors": "colors", "sizes": "sizes",
        }
    )
    assert len(products) == 2

def test_parse_csv_product_fields():
    products = parse_csv_feed(
        filepath=str(FIXTURE),
        brand="Test Brand",
        affiliate_prefix="https://track.com/?url=",
        column_map={
            "sku": "sku", "name": "name", "price": "price",
            "sale_price": "sale_price", "image_url": "image_url",
            "buy_url": "buy_url", "category": "category",
            "colors": "colors", "sizes": "sizes",
        }
    )
    p = products[0]
    assert p.name == "Malibu Triangle Top"
    assert p.price == 98.0
    assert p.sale_price is None
    assert "black" in p.colors
    assert "XS" in p.sizes
    assert p.affiliate_url.startswith("https://track.com/")

def test_parse_csv_sale_price():
    products = parse_csv_feed(
        filepath=str(FIXTURE),
        brand="Test Brand",
        affiliate_prefix="https://track.com/?url=",
        column_map={
            "sku": "sku", "name": "name", "price": "price",
            "sale_price": "sale_price", "image_url": "image_url",
            "buy_url": "buy_url", "category": "category",
            "colors": "colors", "sizes": "sizes",
        }
    )
    p = products[1]
    assert p.sale_price == 60.0
