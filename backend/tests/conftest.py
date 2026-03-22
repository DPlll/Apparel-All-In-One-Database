import sqlite3
import pytest
from fastapi.testclient import TestClient
from pipeline.database import init_db, upsert_product
from pipeline.models import Product
from api.main import app
from api.deps import get_db


@pytest.fixture
def mem_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def sample_product():
    return Product(
        id="frankies_sku001",
        brand="Frankies Bikinis",
        brand_slug="frankies-bikinis",
        name="Malibu Top",
        price=98.0,
        image_url="https://img.com/1.jpg",
        affiliate_url="https://frankies.com/buy",
        style="top",
        colors=["black", "white"],
        sizes=["XS", "S", "M"],
        in_stock=True,
    )


@pytest.fixture
def client(mem_db, sample_product):
    upsert_product(mem_db, sample_product)
    app.dependency_overrides[get_db] = lambda: mem_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
