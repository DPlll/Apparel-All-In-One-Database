import os
import tempfile
import requests
from pipeline.brands import BRANDS
from pipeline.feed_parser import parse_csv_feed
from pipeline.scraper import scrape_brand
from pipeline.database import get_connection, upsert_product


def download_feed(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb")
    tmp.write(resp.content)
    tmp.close()
    return tmp.name


def run_pipeline(db_path: str) -> dict:
    conn = get_connection(db_path)
    summary = {"brands_processed": 0, "products_upserted": 0, "errors": []}

    try:
        for brand_cfg in BRANDS:
            brand = brand_cfg["brand"]
            brand_slug = brand_cfg.get("brand_slug", "")

            try:
                feed_url = brand_cfg.get("feed_url", "")

                if feed_url:
                    # Affiliate feed path
                    print(f"[FETCH] {brand} — feed")
                    filepath = download_feed(feed_url)
                    try:
                        products = parse_csv_feed(
                            filepath=filepath,
                            brand=brand,
                            affiliate_prefix=brand_cfg["affiliate_prefix"],
                            column_map=brand_cfg["column_map"],
                        )
                    finally:
                        os.unlink(filepath)

                elif brand_cfg.get("scrape_via"):
                    # Scraper fallback
                    print(f"[SCRAPE] {brand} — {brand_cfg['scrape_via']}")
                    products = scrape_brand(brand_slug)

                else:
                    print(f"[SKIP] {brand} — no feed_url and no scrape_via configured")
                    continue

                for p in products:
                    upsert_product(conn, p)

                summary["brands_processed"] += 1
                summary["products_upserted"] += len(products)
                print(f"[OK] {brand} — {len(products)} products")

            except Exception as e:
                summary["errors"].append({"brand": brand, "error": str(e)})
                print(f"[ERR] {brand} — {e}")
    finally:
        conn.close()

    return summary


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    db_path = os.getenv("DB_PATH", "./data/products.db")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    result = run_pipeline(db_path)
    print(f"\nDone: {result}")
