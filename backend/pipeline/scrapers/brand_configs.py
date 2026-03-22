# Per-brand Shopify scraper configuration.
# domain: storefront domain (without https://)
# brand:  human-readable brand name (must match what goes in the DB)

SHOPIFY_BRANDS: dict[str, dict] = {
    "frankies-bikinis": {
        "brand": "Frankies Bikinis",
        "domain": "www.frankiesbikinis.com",
    },
    "monday-swimwear": {
        "brand": "Monday Swimwear",
        "domain": "www.mondayswimwear.com",
    },
    "kulani-kinis": {
        "brand": "Kulani Kinis",
        "domain": "www.kulanikinis.com",
    },
    "hunza-g": {
        "brand": "Hunza G",
        "domain": "www.hunzag.com",
    },
    # MIKOH uses WordPress (not Shopify) — /products.json returns HTML
    # Maaji returns 404 for /products.json — not a standard Shopify storefront
    # Both brands pending custom scraper implementation
}
