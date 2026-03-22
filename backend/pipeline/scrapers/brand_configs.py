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
    "mikoh": {
        "brand": "MIKOH",
        "domain": "www.mikoh.com",
    },
    "maaji": {
        "brand": "Maaji",
        "domain": "www.maaji.com",
    },
    "kulani-kinis": {
        "brand": "Kulani Kinis",
        "domain": "www.kulanikinis.com",
    },
    "hunza-g": {
        "brand": "Hunza G",
        "domain": "www.hunzag.com",
    },
}
