# Brand configurations for the pipeline.
# affiliate_prefix: your tracked affiliate URL prefix from the network
# feed_url: CSV/XML feed URL from the affiliate network dashboard
# column_map: maps normalized field names to this brand's CSV column headers

BRANDS = [
    {
        "brand": "Frankies Bikinis",
        "affiliate_prefix": "https://www.shareasale.com/r.cfm?u=YOURID&b=BRANDID&m=MERCHANTID&afftrack=&urllink=",
        "feed_url": "",  # fill in from ShareASale dashboard
        "column_map": {
            "sku": "SKU", "name": "Name", "price": "Price",
            "sale_price": "SalePrice", "image_url": "ImageURL",
            "buy_url": "BuyURL", "category": "Category",
            "colors": "Color", "sizes": "Size",
        },
    },
    # Add more brands here following the same pattern
]
