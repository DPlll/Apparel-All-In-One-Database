# Bikini Catalog — Backend & Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python data pipeline that pulls bikini products from affiliate feeds + scraping into SQLite, and a FastAPI backend that serves them via REST API.

**Architecture:** Pipeline normalizes products into a single SQLite schema. FastAPI reads from that DB and exposes filtered/paginated endpoints. Frontend (Plan 2) calls this API. Pipeline runs manually or on a cron schedule.

**Tech Stack:** Python 3.11, FastAPI, uvicorn, SQLite (via sqlite3), requests, BeautifulSoup4, feedparser, pytest

> **Pagination note:** This plan uses offset-based pagination (`page` param) for simplicity. The spec mentions cursor-based — upgrade to keyset pagination post-launch if catalog grows beyond ~5k products. At MVP scale (10-15 brands, ~100 products each), offset is correct.
>
> **Scraper note:** `backend/pipeline/scraper.py` is listed in the file structure but not implemented in this plan — it's a post-MVP fallback for brands not on affiliate networks. Add a stub `# TODO: web scraper fallback` file in Task 1.

---

## File Structure

```
backend/
├── pipeline/
│   ├── __init__.py
│   ├── models.py          # Product dataclass — single source of truth for schema
│   ├── database.py        # SQLite setup, upsert, query helpers
│   ├── feed_parser.py     # Affiliate feed ingestion (CSV/XML)
│   ├── scraper.py         # Web scraping fallback
│   └── run.py             # CLI entry point — runs full pipeline
├── api/
│   ├── __init__.py
│   ├── main.py            # FastAPI app, router mounts, CORS
│   ├── deps.py            # DB connection dependency
│   └── routes/
│       ├── products.py    # GET /products, GET /products/{id}
│       ├── brands.py      # GET /brands
│       ├── search.py      # GET /search
│       └── clicks.py      # POST /click/{id}
├── tests/
│   ├── conftest.py        # Shared fixtures (in-memory DB, test client)
│   ├── test_models.py
│   ├── test_database.py
│   ├── test_feed_parser.py
│   ├── test_api_products.py
│   ├── test_api_brands.py
│   ├── test_api_search.py
│   └── test_api_clicks.py
├── requirements.txt
├── .env.example
└── pytest.ini
```

---

### Task 1: Project scaffold + Product model

**Files:**
- Create: `backend/pipeline/__init__.py`
- Create: `backend/api/__init__.py`
- Create: `backend/api/routes/__init__.py`
- Create: `backend/pipeline/models.py`
- Create: `backend/tests/test_models.py`
- Create: `backend/requirements.txt`
- Create: `backend/pytest.ini`
- Create: `backend/.env.example`

- [ ] **Step 1: Create directory structure**

```bash
cd /path/to/Apparel-All-In-One-Database
mkdir -p backend/pipeline backend/api/routes backend/tests backend/tests/fixtures
touch backend/pipeline/__init__.py backend/api/__init__.py backend/api/routes/__init__.py
echo "# TODO: web scraper fallback for brands not on affiliate networks" > backend/pipeline/scraper.py
```

- [ ] **Step 2: Write requirements.txt**

```
fastapi==0.115.0
uvicorn==0.30.0
requests==2.32.0
beautifulsoup4==4.12.0
feedparser==6.0.11
python-dotenv==1.0.0
pytest==8.3.0
httpx==0.27.0
```

- [ ] **Step 3: Write pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
```

- [ ] **Step 4: Write .env.example**

```
DB_PATH=./data/products.db
```

- [ ] **Step 5: Write failing test for Product model**

`backend/tests/test_models.py`:
```python
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
```

- [ ] **Step 6: Run test — expect FAIL**

```bash
cd backend && pip install -r requirements.txt
pytest tests/test_models.py -v
```
Expected: `ModuleNotFoundError` or `ImportError`

- [ ] **Step 7: Implement Product model**

`backend/pipeline/models.py`:
```python
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timezone

@dataclass
class Product:
    id: str
    brand: str
    brand_slug: str
    name: str
    price: float
    image_url: str
    affiliate_url: str
    style: str          # top / bottom / set / one-piece
    colors: list
    sizes: list
    in_stock: bool
    sale_price: Optional[float] = None
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        d = asdict(self)
        d["colors"] = self.colors
        d["sizes"] = self.sizes
        return d
```

- [ ] **Step 8: Run test — expect PASS**

```bash
pytest tests/test_models.py -v
```
Expected: 2 passed

- [ ] **Step 9: Commit**

```bash
git add backend/
git commit -m "feat: product model + project scaffold"
```

---

### Task 2: SQLite database layer

**Files:**
- Create: `backend/pipeline/database.py`
- Create: `backend/tests/test_database.py`

- [ ] **Step 1: Write failing tests**

`backend/tests/test_database.py`:
```python
import sqlite3
import pytest
from pipeline.database import init_db, upsert_product, get_products, get_product_by_id, get_brands
from pipeline.models import Product

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    yield conn
    conn.close()

def make_product(brand_slug="frankies", sku="001", style="top", color="black", size="S", price=90.0):
    return Product(
        id=f"{brand_slug}_{sku}",
        brand="Test Brand",
        brand_slug=brand_slug,
        name="Test Top",
        price=price,
        image_url="https://img.com/1.jpg",
        affiliate_url="https://brand.com/buy",
        style=style,
        colors=[color],
        sizes=[size],
        in_stock=True,
    )

def test_init_db_creates_table(db):
    cur = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
    assert cur.fetchone() is not None

def test_upsert_and_retrieve(db):
    p = make_product()
    upsert_product(db, p)
    results = get_products(db)
    assert len(results) == 1
    assert results[0]["id"] == p.id

def test_upsert_updates_existing(db):
    p = make_product(price=90.0)
    upsert_product(db, p)
    p2 = make_product(price=75.0)
    upsert_product(db, p2)
    results = get_products(db)
    assert len(results) == 1
    assert results[0]["price"] == 75.0

def test_get_product_by_id(db):
    p = make_product()
    upsert_product(db, p)
    result = get_product_by_id(db, p.id)
    assert result is not None
    assert result["id"] == p.id

def test_filter_by_brand(db):
    upsert_product(db, make_product(brand_slug="frankies", sku="1"))
    upsert_product(db, make_product(brand_slug="triangl", sku="2"))
    results = get_products(db, brand="frankies")
    assert len(results) == 1

def test_filter_by_price_range(db):
    upsert_product(db, make_product(sku="1", price=50.0))
    upsert_product(db, make_product(sku="2", price=150.0))
    results = get_products(db, min_price=40.0, max_price=100.0)
    assert len(results) == 1
    assert results[0]["price"] == 50.0

def test_get_brands(db):
    upsert_product(db, make_product(brand_slug="frankies", sku="1"))
    upsert_product(db, make_product(brand_slug="triangl", sku="2"))
    brands = get_brands(db)
    slugs = [b["brand_slug"] for b in brands]
    assert "frankies" in slugs
    assert "triangl" in slugs

def test_search_finds_product(db):
    from pipeline.database import search_products
    p = make_product(brand_slug="triangl", sku="99")
    p.name = "Crete Triangle Set"
    upsert_product(db, p)
    results = search_products(db, "Crete")
    assert len(results) == 1
    assert results[0]["name"] == "Crete Triangle Set"
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/test_database.py -v
```

- [ ] **Step 3: Implement database.py**

`backend/pipeline/database.py`:
```python
import sqlite3
import json
from pipeline.models import Product

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id           TEXT PRIMARY KEY,
    brand        TEXT NOT NULL,
    brand_slug   TEXT NOT NULL,
    name         TEXT NOT NULL,
    price        REAL NOT NULL,
    sale_price   REAL,
    image_url    TEXT NOT NULL,
    affiliate_url TEXT NOT NULL,
    style        TEXT NOT NULL,
    colors       TEXT NOT NULL,  -- JSON array
    sizes        TEXT NOT NULL,  -- JSON array
    in_stock     INTEGER NOT NULL DEFAULT 1,
    updated_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_brand_slug ON products(brand_slug);
CREATE INDEX IF NOT EXISTS idx_style     ON products(style);
CREATE INDEX IF NOT EXISTS idx_in_stock  ON products(in_stock);
CREATE VIRTUAL TABLE IF NOT EXISTS products_fts USING fts5(
    id UNINDEXED, name, brand, colors
);
CREATE TRIGGER IF NOT EXISTS products_fts_ai AFTER INSERT ON products BEGIN
  INSERT INTO products_fts(rowid, id, name, brand, colors)
  VALUES (new.rowid, new.id, new.name, new.brand, new.colors);
END;
CREATE TRIGGER IF NOT EXISTS products_fts_ad AFTER DELETE ON products BEGIN
  INSERT INTO products_fts(products_fts, rowid, id, name, brand, colors)
  VALUES ('delete', old.rowid, old.id, old.name, old.brand, old.colors);
END;
CREATE TRIGGER IF NOT EXISTS products_fts_au AFTER UPDATE ON products BEGIN
  INSERT INTO products_fts(products_fts, rowid, id, name, brand, colors)
  VALUES ('delete', old.rowid, old.id, old.name, old.brand, old.colors);
  INSERT INTO products_fts(rowid, id, name, brand, colors)
  VALUES (new.rowid, new.id, new.name, new.brand, new.colors);
END;
CREATE TABLE IF NOT EXISTS clicks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    clicked_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()

def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn

def upsert_product(conn: sqlite3.Connection, p: Product) -> None:
    conn.execute("""
        INSERT INTO products (id, brand, brand_slug, name, price, sale_price,
            image_url, affiliate_url, style, colors, sizes, in_stock, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
            price=excluded.price, sale_price=excluded.sale_price,
            image_url=excluded.image_url, affiliate_url=excluded.affiliate_url,
            in_stock=excluded.in_stock, updated_at=excluded.updated_at,
            colors=excluded.colors, sizes=excluded.sizes
    """, (
        p.id, p.brand, p.brand_slug, p.name, p.price, p.sale_price,
        p.image_url, p.affiliate_url, p.style,
        json.dumps(p.colors), json.dumps(p.sizes),
        int(p.in_stock), p.updated_at,
    ))
    conn.commit()

def _row_to_dict(row) -> dict:
    d = dict(row)
    d["colors"] = json.loads(d["colors"])
    d["sizes"]  = json.loads(d["sizes"])
    d["in_stock"] = bool(d["in_stock"])
    return d

def get_products(
    conn: sqlite3.Connection,
    brand: str = None,
    style: str = None,
    color: str = None,
    size: str = None,
    min_price: float = None,
    max_price: float = None,
    in_stock: bool = None,
    sort: str = "newest",
    limit: int = 24,
    offset: int = 0,
) -> list[dict]:
    conditions = []
    params = []

    if brand:       conditions.append("brand_slug = ?");   params.append(brand)
    if style:       conditions.append("style = ?");        params.append(style)
    if color:       conditions.append("colors LIKE ?");    params.append(f'%"{color}"%')
    if size:        conditions.append("sizes LIKE ?");     params.append(f'%"{size}"%')
    if min_price is not None: conditions.append("price >= ?"); params.append(min_price)
    if max_price is not None: conditions.append("price <= ?"); params.append(max_price)
    if in_stock is not None:  conditions.append("in_stock = ?"); params.append(int(in_stock))

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    order = {"price_asc": "price ASC", "price_desc": "price DESC"}.get(sort, "updated_at DESC")

    params += [limit, offset]
    rows = conn.execute(
        f"SELECT * FROM products {where} ORDER BY {order} LIMIT ? OFFSET ?", params
    ).fetchall()
    return [_row_to_dict(r) for r in rows]

def get_product_by_id(conn: sqlite3.Connection, product_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return _row_to_dict(row) if row else None

def get_brands(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("""
        SELECT brand, brand_slug, COUNT(*) as product_count
        FROM products GROUP BY brand_slug ORDER BY brand
    """).fetchall()
    return [dict(r) for r in rows]

def search_products(conn: sqlite3.Connection, query: str, limit: int = 24) -> list[dict]:
    rows = conn.execute("""
        SELECT p.* FROM products p
        WHERE p.id IN (
            SELECT id FROM products_fts WHERE products_fts MATCH ?
        )
        LIMIT ?
    """, (query, limit)).fetchall()
    return [_row_to_dict(r) for r in rows]

def log_click(conn: sqlite3.Connection, product_id: str) -> None:
    conn.execute("INSERT INTO clicks (product_id) VALUES (?)", (product_id,))
    conn.commit()
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/test_database.py -v
```
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add backend/pipeline/database.py backend/tests/test_database.py
git commit -m "feat: SQLite database layer with upsert, filters, FTS"
```

---

### Task 3: Affiliate feed parser

**Files:**
- Create: `backend/pipeline/feed_parser.py`
- Create: `backend/tests/test_feed_parser.py`
- Create: `backend/tests/fixtures/sample_feed.csv`

- [ ] **Step 1: Create sample CSV fixture**

`backend/tests/fixtures/sample_feed.csv`:
```csv
sku,name,price,sale_price,image_url,buy_url,category,colors,sizes
SKU001,Malibu Triangle Top,98.00,,https://img.com/1.jpg,https://buy.com/1,bikini-top,"black,white","XS,S,M,L"
SKU002,Monaco Bottom,78.00,60.00,https://img.com/2.jpg,https://buy.com/2,bikini-bottom,"blue","S,M,L"
```

- [ ] **Step 2: Write failing tests**

`backend/tests/test_feed_parser.py`:
```python
import pytest
from pathlib import Path
from pipeline.feed_parser import parse_csv_feed, normalize_brand_slug

FIXTURE = Path(__file__).parent / "fixtures" / "sample_feed.csv"

def test_normalize_brand_slug():
    assert normalize_brand_slug("Frankies Bikinis") == "frankies-bikinis"
    assert normalize_brand_slug("L*Space") == "l-space"
    assert normalize_brand_slug("Monday Swimwear") == "monday-swimwear"

def test_parse_csv_returns_products():
    products = parse_csv_feed(
        filepath=str(FIXTURE),
        brand="Test Brand",
        affiliate_prefix="https://track.com/?url=",
        column_map={
            "sku": "sku", "name": "name", "price": "price",
            "sale_price": "sale_price", "image_url": "image_url",
            "buy_url": "buy_url", "category": "category",
            "colors": "colors", "sizes": "sizes",
        }
    )
    assert len(products) == 2

def test_parse_csv_product_fields():
    products = parse_csv_feed(
        filepath=str(FIXTURE),
        brand="Test Brand",
        affiliate_prefix="https://track.com/?url=",
        column_map={
            "sku": "sku", "name": "name", "price": "price",
            "sale_price": "sale_price", "image_url": "image_url",
            "buy_url": "buy_url", "category": "category",
            "colors": "colors", "sizes": "sizes",
        }
    )
    p = products[0]
    assert p.name == "Malibu Triangle Top"
    assert p.price == 98.0
    assert p.sale_price is None
    assert "black" in p.colors
    assert "XS" in p.sizes
    assert p.affiliate_url.startswith("https://track.com/")

def test_parse_csv_sale_price():
    products = parse_csv_feed(
        filepath=str(FIXTURE),
        brand="Test Brand",
        affiliate_prefix="https://track.com/?url=",
        column_map={
            "sku": "sku", "name": "name", "price": "price",
            "sale_price": "sale_price", "image_url": "image_url",
            "buy_url": "buy_url", "category": "category",
            "colors": "colors", "sizes": "sizes",
        }
    )
    p = products[1]
    assert p.sale_price == 60.0
```

- [ ] **Step 3: Run — expect FAIL**

```bash
pytest tests/test_feed_parser.py -v
```

- [ ] **Step 4: Implement feed_parser.py**

`backend/pipeline/feed_parser.py`:
```python
import csv
import re
from pipeline.models import Product

def normalize_brand_slug(brand: str) -> str:
    slug = brand.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
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
```

- [ ] **Step 5: Run — expect PASS**

```bash
pytest tests/test_feed_parser.py -v
```
Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add backend/pipeline/feed_parser.py backend/tests/
git commit -m "feat: CSV affiliate feed parser"
```

---

### Task 4: Pipeline run script + brand config

**Files:**
- Create: `backend/pipeline/brands.py`
- Create: `backend/pipeline/run.py`

- [ ] **Step 1: Create brands config**

`backend/pipeline/brands.py`:
```python
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
```

- [ ] **Step 2: Create pipeline run script**

`backend/pipeline/run.py`:
```python
import os
import tempfile
import requests
from pipeline.brands import BRANDS
from pipeline.feed_parser import parse_csv_feed
from pipeline.database import get_connection, upsert_product

def download_feed(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb")
    tmp.write(resp.content)
    tmp.close()
    return tmp.name

def run_pipeline(db_path: str) -> dict:
    conn = get_connection(db_path)
    summary = {"brands_processed": 0, "products_upserted": 0, "errors": []}

    for brand_cfg in BRANDS:
        brand = brand_cfg["brand"]
        try:
            feed_url = brand_cfg.get("feed_url", "")
            if not feed_url:
                print(f"[SKIP] {brand} — no feed_url configured")
                continue

            print(f"[FETCH] {brand}")
            filepath = download_feed(feed_url)
            products = parse_csv_feed(
                filepath=filepath,
                brand=brand,
                affiliate_prefix=brand_cfg["affiliate_prefix"],
                column_map=brand_cfg["column_map"],
            )
            os.unlink(filepath)

            for p in products:
                upsert_product(conn, p)

            summary["brands_processed"] += 1
            summary["products_upserted"] += len(products)
            print(f"[OK] {brand} — {len(products)} products")

        except Exception as e:
            summary["errors"].append({"brand": brand, "error": str(e)})
            print(f"[ERR] {brand} — {e}")

    conn.close()
    return summary

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    db_path = os.getenv("DB_PATH", "./data/products.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    result = run_pipeline(db_path)
    print(f"\nDone: {result}")
```

- [ ] **Step 3: Commit**

```bash
git add backend/pipeline/brands.py backend/pipeline/run.py
git commit -m "feat: pipeline run script + brand config"
```

---

### Task 5: FastAPI app + dependencies

**Files:**
- Create: `backend/api/deps.py`
- Create: `backend/api/main.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Write conftest with shared fixtures**

`backend/tests/conftest.py`:
```python
import sqlite3
import pytest
from fastapi.testclient import TestClient
from pipeline.database import init_db, upsert_product
from pipeline.models import Product
from api.main import app

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
    app.state.db = mem_db
    with TestClient(app) as c:
        yield c
```

- [ ] **Step 2: Create deps.py**

`backend/api/deps.py`:
```python
from fastapi import Request
import sqlite3

def get_db(request: Request) -> sqlite3.Connection:
    return request.app.state.db
```

- [ ] **Step 3: Create main.py**

`backend/api/main.py`:
```python
import os
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pipeline.database import get_connection
from api.routes import products, brands, search, clicks

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = os.getenv("DB_PATH", "./data/products.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.state.db = get_connection(db_path)
    yield
    app.state.db.close()

app = FastAPI(title="Bikini Catalog API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(brands.router)
app.include_router(search.router)
app.include_router(clicks.router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Commit**

```bash
git add backend/api/ backend/tests/conftest.py
git commit -m "feat: FastAPI app skeleton + test fixtures"
```

---

### Task 6: Products routes

**Files:**
- Create: `backend/api/routes/products.py`
- Create: `backend/tests/test_api_products.py`

- [ ] **Step 1: Write failing tests**

`backend/tests/test_api_products.py`:
```python
def test_list_products(client):
    r = client.get("/products")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert len(data["items"]) == 1

def test_list_products_filter_brand(client):
    r = client.get("/products?brand=frankies-bikinis")
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1

def test_list_products_filter_no_match(client):
    r = client.get("/products?brand=triangl")
    assert r.status_code == 200
    assert len(r.json()["items"]) == 0

def test_list_products_filter_price(client):
    r = client.get("/products?min_price=50&max_price=200")
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1

def test_get_product_by_id(client):
    r = client.get("/products/frankies_sku001")
    assert r.status_code == 200
    assert r.json()["id"] == "frankies_sku001"

def test_get_product_not_found(client):
    r = client.get("/products/does_not_exist")
    assert r.status_code == 404
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/test_api_products.py -v
```

- [ ] **Step 3: Implement products route**

`backend/api/routes/products.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from api.deps import get_db
from pipeline.database import get_products, get_product_by_id

router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
def list_products(
    brand: Optional[str]  = None,
    style: Optional[str]  = None,
    color: Optional[str]  = None,
    size:  Optional[str]  = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool]   = True,
    sort:  str  = Query("newest", enum=["newest", "price_asc", "price_desc"]),
    page:  int  = Query(1, ge=1),
    db = Depends(get_db),
):
    limit  = 24
    offset = (page - 1) * limit
    items  = get_products(db, brand=brand, style=style, color=color, size=size,
                          min_price=min_price, max_price=max_price,
                          in_stock=in_stock, sort=sort, limit=limit, offset=offset)
    return {"items": items, "page": page, "per_page": limit}

@router.get("/{product_id}")
def get_product(product_id: str, db = Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/test_api_products.py -v
```
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add backend/api/routes/products.py backend/tests/test_api_products.py
git commit -m "feat: GET /products and GET /products/{id}"
```

---

### Task 7: Brands + Search + Clicks routes

**Files:**
- Create: `backend/api/routes/brands.py`
- Create: `backend/api/routes/search.py`
- Create: `backend/api/routes/clicks.py`
- Create: `backend/tests/test_api_brands.py`
- Create: `backend/tests/test_api_search.py`
- Create: `backend/tests/test_api_clicks.py`

- [ ] **Step 1: Write failing tests**

`backend/tests/test_api_brands.py`:
```python
def test_get_brands(client):
    r = client.get("/brands")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert data[0]["brand_slug"] == "frankies-bikinis"
    assert data[0]["product_count"] == 1
```

`backend/tests/test_api_search.py`:
```python
def test_search_finds_product(client):
    r = client.get("/search?q=Malibu")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Malibu Top"

def test_search_no_results(client):
    r = client.get("/search?q=doesnotexist99")
    assert r.status_code == 200
    assert r.json()["items"] == []

def test_search_missing_query(client):
    r = client.get("/search")
    assert r.status_code == 422
```

`backend/tests/test_api_clicks.py`:
```python
def test_click_returns_affiliate_url(client):
    r = client.post("/click/frankies_sku001")
    assert r.status_code == 200
    assert "affiliate_url" in r.json()

def test_click_not_found(client):
    r = client.post("/click/does_not_exist")
    assert r.status_code == 404
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/test_api_brands.py tests/test_api_search.py tests/test_api_clicks.py -v
```

- [ ] **Step 3: Implement brands.py**

`backend/api/routes/brands.py`:
```python
from fastapi import APIRouter, Depends
from api.deps import get_db
from pipeline.database import get_brands

router = APIRouter(prefix="/brands", tags=["brands"])

@router.get("")
def list_brands(db = Depends(get_db)):
    return get_brands(db)
```

- [ ] **Step 4: Implement search.py**

`backend/api/routes/search.py`:
```python
from fastapi import APIRouter, Depends, Query
from api.deps import get_db
from pipeline.database import search_products

router = APIRouter(prefix="/search", tags=["search"])

@router.get("")
def search(q: str = Query(..., min_length=1), db = Depends(get_db)):
    return {"items": search_products(db, q)}
```

- [ ] **Step 5: Implement clicks.py**

`backend/api/routes/clicks.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_db
from pipeline.database import get_product_by_id, log_click

router = APIRouter(prefix="/click", tags=["clicks"])

@router.post("/{product_id}")
def record_click(product_id: str, db = Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    log_click(db, product_id)
    return {"affiliate_url": product["affiliate_url"]}
```

- [ ] **Step 6: Run all tests — expect PASS**

```bash
pytest tests/ -v
```
Expected: all passed

- [ ] **Step 7: Smoke test the running API**

```bash
cd backend
DB_PATH=./data/products.db uvicorn api.main:app --reload
# In another terminal:
curl http://localhost:8000/health
curl http://localhost:8000/brands
curl http://localhost:8000/products
```

- [ ] **Step 8: Final commit**

```bash
git add backend/
git commit -m "feat: complete backend API — brands, search, clicks"
```

---

## Done

Backend is complete when:
- [ ] All pytest tests pass
- [ ] `uvicorn api.main:app` starts without error
- [ ] `/health`, `/products`, `/brands`, `/search`, `/click/{id}` all respond correctly
- [ ] `python -m pipeline.run` runs the pipeline (skips brands with no feed_url configured)

**Next:** See `2026-03-21-frontend.md` for the Next.js catalog UI.
