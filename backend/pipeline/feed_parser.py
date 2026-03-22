import csv
import re
from typing import Optional
from pipeline.models import Product

def normalize_brand_slug(brand: str) -> str:
    slug = brand.lower()
    # Replace non-alphanumeric/space/hyphen with space (preserves word boundaries)
    slug = re.sub(r"[^a-z0-9\s-]", " ", slug)
    # Collapse multiple spaces/hyphens to single space, then convert to hyphens
    slug = re.sub(r"\s+", "-", slug.strip())
    # Clean up any double hyphens that may result from adjacent spaces/hyphens in original
    slug = re.sub(r"-+", "-", slug)
    return slug

def _get_col(row: dict, col: Optional[str]) -> str:
    """Safely retrieve an optional column value from a row.

    Returns empty string if col is None (column not in mapping).
    Avoids reading blank-header columns which can cause data leaks.
    """
    if not col:
        return ""
    return row.get(col, "").strip()

def _parse_list(value: str) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

def _map_style(category: str) -> str:
    cat = category.lower()
    if "top"       in cat: return "top"
    if "bottom"    in cat: return "bottom"
    if "one-piece" in cat or "onepiece" in cat: return "one-piece"
    return "set"

def parse_csv_feed(
    filepath: str,
    brand: str,
    affiliate_prefix: str,
    column_map: dict,
) -> list[Product]:
    slug = normalize_brand_slug(brand)
    products = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sku        = row.get(column_map["sku"], "").strip()
            name       = row.get(column_map["name"], "").strip()
            price_str  = row.get(column_map["price"], "0").strip()
            image_url  = row.get(column_map["image_url"], "").strip()
            buy_url    = row.get(column_map["buy_url"], "").strip()

            # Optional columns: use sentinel pattern to avoid reading blank-header columns
            sale_str   = _get_col(row, column_map.get("sale_price"))
            category   = _get_col(row, column_map.get("category"))
            colors_raw = _get_col(row, column_map.get("colors"))
            sizes_raw  = _get_col(row, column_map.get("sizes"))

            if not sku or not name or not buy_url:
                continue

            try:
                price = float(price_str)
            except ValueError:
                continue

            sale_price = None
            if sale_str:
                try:
                    sale_price = float(sale_str)
                except ValueError:
                    pass

            products.append(Product(
                id=f"{slug}_{sku}",
                brand=brand,
                brand_slug=slug,
                name=name,
                price=price,
                sale_price=sale_price,
                image_url=image_url,
                affiliate_url=affiliate_prefix + buy_url,
                style=_map_style(category),
                colors=_parse_list(colors_raw),
                sizes=_parse_list(sizes_raw),
                # Affiliate feeds don't include stock status; default to True
                in_stock=True,
            ))

    return products
