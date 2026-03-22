from pipeline.models import Product

def test_product_has_required_fields():
    p = Product(
        id="frankies-bikinis_sku123",
        brand="Frankies Bikinis",
        brand_slug="frankies-bikinis",
        name="Malibu Triangle Top",
        price=98.0,
        image_url="https://example.com/img.jpg",
        affiliate_url="https://example.com/buy",
        style="top",
        colors=["black"],
        sizes=["XS", "S", "M"],
        in_stock=True,
    )
    assert p.id == "frankies-bikinis_sku123"
    assert p.sale_price is None

def test_product_to_dict_is_serializable():
    p = Product(
        id="test_1", brand="Brand", brand_slug="brand",
        name="Top", price=50.0, image_url="http://img",
        affiliate_url="http://link", style="top",
        colors=["white"], sizes=["S"], in_stock=True,
    )
    d = p.to_dict()
    assert d["id"] == "test_1"
    assert d["colors"] == ["white"]
    assert "updated_at" in d
