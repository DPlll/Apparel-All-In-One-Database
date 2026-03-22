import sqlite3
import pytest
from pipeline.database import init_db, upsert_product, get_products, get_product_by_id, get_brands, log_click, search_products
from pipeline.models import Product

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    yield conn
    conn.close()

def make_product(brand_slug="frankies", sku="001", style="top", color="black", size="S", price=90.0):
    return Product(
        id=f"{brand_slug}_{sku}",
        brand="Test Brand",
        brand_slug=brand_slug,
        name="Test Top",
        price=price,
        image_url="https://img.com/1.jpg",
        affiliate_url="https://brand.com/buy",
        style=style,
        colors=[color],
        sizes=[size],
        in_stock=True,
    )

def test_init_db_creates_table(db):
    cur = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
    assert cur.fetchone() is not None

def test_upsert_and_retrieve(db):
    p = make_product()
    upsert_product(db, p)
    results = get_products(db)
    assert len(results) == 1
    assert results[0]["id"] == p.id

def test_upsert_updates_existing(db):
    p = make_product(price=90.0)
    upsert_product(db, p)
    p2 = make_product(price=75.0)
    upsert_product(db, p2)
    results = get_products(db)
    assert len(results) == 1
    assert results[0]["price"] == 75.0

def test_get_product_by_id(db):
    p = make_product()
    upsert_product(db, p)
    result = get_product_by_id(db, p.id)
    assert result is not None
    assert result["id"] == p.id

def test_filter_by_brand(db):
    upsert_product(db, make_product(brand_slug="frankies", sku="1"))
    upsert_product(db, make_product(brand_slug="triangl", sku="2"))
    results = get_products(db, brand="frankies")
    assert len(results) == 1

def test_filter_by_price_range(db):
    upsert_product(db, make_product(sku="1", price=50.0))
    upsert_product(db, make_product(sku="2", price=150.0))
    results = get_products(db, min_price=40.0, max_price=100.0)
    assert len(results) == 1
    assert results[0]["price"] == 50.0

def test_get_brands(db):
    upsert_product(db, make_product(brand_slug="frankies", sku="1"))
    upsert_product(db, make_product(brand_slug="triangl", sku="2"))
    brands = get_brands(db)
    slugs = [b["brand_slug"] for b in brands]
    assert "frankies" in slugs
    assert "triangl" in slugs

def test_search_finds_product(db):
    p = make_product(brand_slug="triangl", sku="99")
    p.name = "Crete Triangle Set"
    upsert_product(db, p)
    results = search_products(db, "Crete")
    assert len(results) == 1
    assert results[0]["name"] == "Crete Triangle Set"

def test_log_click(db):
    p = make_product()
    upsert_product(db, p)
    log_click(db, p.id)
    row = db.execute("SELECT product_id FROM clicks WHERE product_id = ?", (p.id,)).fetchone()
    assert row is not None

def test_fts_updates_after_upsert(db):
    p = make_product(brand_slug="triangl", sku="88")
    p.name = "Original Name"
    upsert_product(db, p)
    # Update the product with a new name
    p.name = "Updated Name"
    upsert_product(db, p)
    # FTS should return the updated name, not the original
    results = search_products(db, "Updated")
    assert len(results) == 1
    assert results[0]["name"] == "Updated Name"
    # Old name should not appear
    old = search_products(db, "Original")
    assert len(old) == 0
