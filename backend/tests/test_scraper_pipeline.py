from unittest.mock import patch
from pipeline.run import run_pipeline
from pipeline.models import Product
from pipeline.database import get_connection

FAKE_PRODUCT = Product(
    id="frankies-bikinis_ABC123",
    brand="Frankies Bikinis",
    brand_slug="frankies-bikinis",
    name="Test Top",
    price=98.0,
    image_url="https://example.com/img.jpg",
    affiliate_url="https://www.frankiesbikinis.com/products/test-top",
    style="top",
    colors=["Black"],
    sizes=["XS", "S"],
    in_stock=True,
)


def test_run_pipeline_uses_scraper_when_no_feed_url(tmp_path):
    db_path = str(tmp_path / "test.db")
    with patch("pipeline.run.scrape_brand") as mock_scrape:
        mock_scrape.return_value = [FAKE_PRODUCT]
        summary = run_pipeline(db_path)

    # All 6 brands have no feed_url, so scraper should be called 6 times
    assert mock_scrape.call_count == 6
    assert summary["products_upserted"] == 6


def test_run_pipeline_skips_scraper_when_feed_url_present(tmp_path):
    db_path = str(tmp_path / "test.db")
    fake_brands = [{
        "brand": "Test Brand",
        "brand_slug": "test-brand",
        "scrape_via": "shopify",
        "feed_url": "https://example.com/feed.csv",
        "affiliate_prefix": "https://aff.example.com/?url=",
        "column_map": {
            "sku": "SKU", "name": "Name", "price": "Price",
            "image_url": "Image", "buy_url": "URL",
        },
    }]

    with patch("pipeline.run.BRANDS", fake_brands), \
         patch("pipeline.run.download_feed") as mock_dl, \
         patch("pipeline.run.parse_csv_feed") as mock_parse, \
         patch("pipeline.run.scrape_brand") as mock_scrape:
        mock_dl.return_value = "/tmp/fake.csv"
        mock_parse.return_value = []
        run_pipeline(db_path)
    mock_scrape.assert_not_called()


def test_run_pipeline_products_land_in_db(tmp_path):
    db_path = str(tmp_path / "test.db")
    with patch("pipeline.run.scrape_brand") as mock_scrape:
        mock_scrape.return_value = [FAKE_PRODUCT]
        run_pipeline(db_path)

    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM products WHERE brand_slug = 'frankies-bikinis'").fetchall()
    assert len(rows) == 1
    assert rows[0]["name"] == "Test Top"
    conn.close()
