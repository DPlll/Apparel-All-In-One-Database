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
    colors       TEXT NOT NULL,
    sizes        TEXT NOT NULL,
    in_stock     INTEGER NOT NULL DEFAULT 1,
    updated_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_brand_slug ON products(brand_slug);
CREATE INDEX IF NOT EXISTS idx_style     ON products(style);
CREATE INDEX IF NOT EXISTS idx_in_stock  ON products(in_stock);
CREATE VIRTUAL TABLE IF NOT EXISTS products_fts USING fts5(
    id UNINDEXED, name, brand, colors,
    content=products, content_rowid=rowid
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
    # Use DELETE + INSERT rather than ON CONFLICT DO UPDATE to avoid FTS5
    # trigger conflicts: the AFTER UPDATE trigger on the products table fires
    # during upsert and attempts to manipulate FTS rowids that are in flux,
    # causing "SQL logic error". A DELETE followed by INSERT triggers the
    # simpler AFTER DELETE and AFTER INSERT paths which work correctly.
    conn.execute("DELETE FROM products WHERE id = ?", (p.id,))
    conn.execute("""
        INSERT INTO products (id, brand, brand_slug, name, price, sale_price,
            image_url, affiliate_url, style, colors, sizes, in_stock, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
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
    d["sizes"] = json.loads(d["sizes"])
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
    # content=products FTS5 table: join on rowid, not on id column
    rows = conn.execute("""
        SELECT p.* FROM products p
        WHERE p.rowid IN (
            SELECT rowid FROM products_fts WHERE products_fts MATCH ?
        )
        LIMIT ?
    """, (query, limit)).fetchall()
    return [_row_to_dict(r) for r in rows]


def log_click(conn: sqlite3.Connection, product_id: str) -> None:
    conn.execute("INSERT INTO clicks (product_id) VALUES (?)", (product_id,))
    conn.commit()
