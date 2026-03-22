from pipeline.scrapers.shopify import scrape_shopify
from pipeline.models import Product


def scrape_brand(brand_slug: str) -> list[Product]:
    """Scrape products for a brand by slug. Returns empty list if slug not configured.

    NOTE: brand_configs is imported lazily here to avoid a circular/missing-module
    error if __init__.py is imported before brand_configs.py exists.
    """
    # Lazy import so Task 1 tests work before brand_configs.py is created in Task 2
    from pipeline.scrapers.brand_configs import SHOPIFY_BRANDS
    cfg = SHOPIFY_BRANDS.get(brand_slug)
    if not cfg:
        return []
    return scrape_shopify(
        domain=cfg["domain"],
        brand=cfg["brand"],
        brand_slug=brand_slug,
    )
