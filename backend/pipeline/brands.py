# Brand configurations for the pipeline.
#
# For brands with affiliate network feeds (CSV/XML):
#   - set feed_url and affiliate_prefix from the network dashboard
#   - set column_map to map normalized fields → CSV column headers
#
# For brands without a feed (scraper fallback):
#   - leave feed_url as ""
#   - set scrape_via: "shopify" (or other scraper key)
#   - brand_slug must match a key in pipeline.scrapers.brand_configs.SHOPIFY_BRANDS

BRANDS = [
    {
        "brand": "Frankies Bikinis",
        "brand_slug": "frankies-bikinis",
        "scrape_via": "shopify",
        "affiliate_prefix": "",  # fill in when ShareASale approved
        "feed_url": "",
        "column_map": {},
    },
    {
        "brand": "Monday Swimwear",
        "brand_slug": "monday-swimwear",
        "scrape_via": "shopify",
        "affiliate_prefix": "",
        "feed_url": "",
        "column_map": {},
    },
    {
        "brand": "MIKOH",
        "brand_slug": "mikoh",
        "scrape_via": "shopify",
        "affiliate_prefix": "",
        "feed_url": "",
        "column_map": {},
    },
    {
        "brand": "Maaji",
        "brand_slug": "maaji",
        "scrape_via": "shopify",
        "affiliate_prefix": "",
        "feed_url": "",
        "column_map": {},
    },
    {
        "brand": "Kulani Kinis",
        "brand_slug": "kulani-kinis",
        "scrape_via": "shopify",
        "affiliate_prefix": "",
        "feed_url": "",
        "column_map": {},
    },
    {
        "brand": "Hunza G",
        "brand_slug": "hunza-g",
        "scrape_via": "shopify",
        "affiliate_prefix": "",
        "feed_url": "",
        "column_map": {},
    },
]
