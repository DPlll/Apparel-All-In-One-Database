import csv
import re
from pipeline.models import Product

def normalize_brand_slug(brand: str) -> str:
    slug = brand.lower()
    # Replace non-alphanumeric/space/hyphen with spaces
    slug = re.sub(r"[^a-z0-9\s-]", " ", slug)
    # Collapse multiple spaces to single space, then convert to hyphens
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug

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
            sale_str   = row.get(column_map.get("sale_price", ""), "").strip()
            image_url  = row.get(column_map["image_url"], "").strip()
            buy_url    = row.get(column_map["buy_url"], "").strip()
            category   = row.get(column_map.get("category", ""), "").strip()
            colors_raw = row.get(column_map.get("colors", ""), "").strip()
            sizes_raw  = row.get(column_map.get("sizes", ""), "").strip()

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
                in_stock=True,
            ))

    return products
