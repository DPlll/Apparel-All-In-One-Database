import time
import requests
from pipeline.models import Product

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BikiniCatalogBot/1.0; +https://swimco.com)",
    "Accept": "application/json",
}


def _infer_style(product_type: str, title: str, tags: list[str]) -> str:
    combined = " ".join([product_type, title, *tags]).lower()
    if any(w in combined for w in ["one-piece", "one piece", "onepiece", "swimsuit", "maillot"]):
        return "one-piece"
    if any(w in combined for w in ["bottom", "brief", "cheeky", "bikini bottom", "pant"]):
        return "bottom"
    if any(w in combined for w in ["top", "bikini top", "bandeau", "triangle", "bralette", "halter"]):
        return "top"
    return "set"


def _get_option_values(product: dict, option_name: str) -> list[str]:
    """Return deduplicated values for a named option (Color, Size) across all variants."""
    for i, opt in enumerate(product.get("options", []), 1):
        if opt.get("name", "").lower() == option_name.lower():
            key = f"option{i}"
            seen: set[str] = set()
            result: list[str] = []
            for v in product.get("variants", []):
                val = (v.get(key) or "").strip()
                if val and val not in seen:
                    seen.add(val)
                    result.append(val)
            return result
    return []


def scrape_shopify(
    domain: str,
    brand: str,
    brand_slug: str,
    delay: float = 1.5,
) -> list[Product]:
    """
    Scrape all products from a Shopify store via /products.json.

    Args:
        domain:     Shopify storefront domain, e.g. "www.frankiesbikinis.com"
        brand:      Human-readable brand name, e.g. "Frankies Bikinis"
        brand_slug: URL-safe slug, e.g. "frankies-bikinis"
        delay:      Seconds to wait between paginated requests (be polite)

    Returns:
        List of Product objects ready for upsert_product().
    """
    products: list[Product] = []
    page = 1

    while True:
        url = f"https://{domain}/products.json?limit=250&page={page}"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            break

        items = resp.json().get("products", [])
        if not items:
            break

        for item in items:
            variants = item.get("variants", [])
            if not variants:
                continue

            # Price: Shopify stores sale as price < compare_at_price
            price_str = variants[0].get("price") or "0"
            compare_str = variants[0].get("compare_at_price")
            price = float(price_str)
            sale_price = None
            if compare_str:
                compare = float(compare_str)
                if compare > price:
                    # product is on sale: compare_at is original, price is sale
                    sale_price = price
                    price = compare

            # Image: first image in list
            images = item.get("images", [])
            image_url = images[0]["src"] if images else ""

            # Options
            colors = _get_option_values(item, "Color")
            sizes = _get_option_values(item, "Size")

            # Style from product_type + title + tags
            tags_raw = item.get("tags", [])
            tags = tags_raw if isinstance(tags_raw, list) else [t.strip() for t in tags_raw.split(",")]
            style = _infer_style(
                item.get("product_type", ""),
                item.get("title", ""),
                tags,
            )

            # Direct product URL (no affiliate tracking for beta)
            handle = item.get("handle", "")
            product_url = f"https://{domain}/products/{handle}"

            # SKU: use first variant SKU, fall back to product ID
            sku = (variants[0].get("sku") or "").strip() or str(item["id"])

            # In stock if any variant is available
            in_stock = any(v.get("available", True) for v in variants)

            products.append(Product(
                id=f"{brand_slug}_{sku}",
                brand=brand,
                brand_slug=brand_slug,
                name=item.get("title", ""),
                price=price,
                sale_price=sale_price,
                image_url=image_url,
                affiliate_url=product_url,
                style=style,
                colors=colors,
                sizes=sizes,
                in_stock=in_stock,
            ))

        # Shopify returns < 250 on last page
        if len(items) < 250:
            break

        page += 1
        if delay > 0:
            time.sleep(delay)

    return products
