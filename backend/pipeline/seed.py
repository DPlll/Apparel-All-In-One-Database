"""
Seed script: runs the full scraper pipeline and writes results to the DB.

Usage:
    python -m pipeline.seed [--dry-run] [--brand SLUG]

Options:
    --dry-run   Scrape and print counts but do not write to DB
    --brand     Only scrape a single brand by slug (e.g. frankies-bikinis)
"""
import argparse
import os
import sys
from dotenv import load_dotenv

from pipeline.brands import BRANDS
from pipeline.database import get_connection, upsert_product
from pipeline.scrapers import scrape_brand


def seed(db_path: str, dry_run: bool = False, brand_slug: str | None = None) -> dict:
    brands = BRANDS
    if brand_slug:
        brands = [b for b in BRANDS if b["brand_slug"] == brand_slug]
        if not brands:
            print(f"[ERROR] Unknown brand slug: {brand_slug}")
            sys.exit(1)

    conn = None if dry_run else get_connection(db_path)
    summary = {"brands_processed": 0, "products_scraped": 0, "errors": []}

    try:
        for brand_cfg in brands:
            slug = brand_cfg["brand_slug"]
            name = brand_cfg["brand"]

            if not brand_cfg.get("scrape_via"):
                print(f"[SKIP] {name} -- no scrape_via configured")
                continue

            print(f"[SCRAPE] {name} ({slug}) ...", flush=True)
            try:
                products = scrape_brand(slug)
                summary["brands_processed"] += 1
                summary["products_scraped"] += len(products)
                print(f"  -> {len(products)} products")

                if not dry_run and conn is not None:
                    for p in products:
                        upsert_product(conn, p)
            except Exception as e:
                summary["errors"].append({"brand": name, "error": str(e)})
                print(f"[ERR] {name} — {e}")
    finally:
        if conn is not None:
            conn.close()

    return summary


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Seed the product catalog DB")
    parser.add_argument("--dry-run", action="store_true", help="Scrape but do not write to DB")
    parser.add_argument("--brand", metavar="SLUG", help="Only scrape this brand slug")
    args = parser.parse_args()

    db_path = os.getenv("DB_PATH", "./data/products.db")
    db_dir = os.path.dirname(db_path)
    if db_dir and not args.dry_run:
        os.makedirs(db_dir, exist_ok=True)

    mode = "DRY RUN" if args.dry_run else f"-> {db_path}"
    print(f"Seeding catalog [{mode}]\n")

    result = seed(db_path=db_path, dry_run=args.dry_run, brand_slug=args.brand)

    print(f"\nDone: {result['brands_processed']} brands, "
          f"{result['products_scraped']} products scraped"
          + (f", {len(result['errors'])} errors" if result["errors"] else ""))

    if result["errors"]:
        for e in result["errors"]:
            print(f"  ERROR: {e['brand']}: {e['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
