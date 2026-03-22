# Where'd you get your Bikini?

A product catalog aggregator for women's swimwear — browse styles from top bikini brands in one place, click through to buy direct.

---

## What it does

Scrapes inventory from Shopify-powered swimwear storefronts and surfaces it in a clean, filterable catalog. No affiliate tracking, no redirects — just a direct link to the brand's product page when you find something you love.

**Current brands:**
- Frankies Bikinis
- Monday Swimwear
- Kulani Kinis
- Hunza G

**Catalog size:** ~7,100+ products, updated on demand.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, Tailwind CSS 4 |
| Backend | FastAPI, Python 3.12, SQLite |
| Data pipeline | Custom Shopify JSON scraper |
| Testing | pytest (backend), Jest + Testing Library (frontend) |

---

## Project Structure

```
.
├── backend/
│   ├── api/               # FastAPI app, routes (products, brands, search, clicks)
│   ├── pipeline/
│   │   ├── scrapers/      # Shopify scraper + per-brand configs
│   │   ├── models.py      # Product dataclass
│   │   ├── database.py    # SQLite connection + upsert logic
│   │   ├── seed.py        # CLI seed script
│   │   └── run.py         # Full pipeline runner
│   ├── tests/             # pytest test suite (39 tests)
│   └── requirements.txt
└── frontend/
    ├── app/               # Next.js App Router pages
    │   ├── page.tsx       # Homepage
    │   ├── catalog/       # Browse + filter all products
    │   ├── brands/        # Per-brand landing pages
    │   └── product/       # Product detail page
    ├── components/        # Shared UI components
    ├── lib/               # API client
    └── types/             # TypeScript types
```

---

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt

# Seed the database (scrapes all brands live)
python -m pipeline.seed

# Start the API
uvicorn api.main:app --reload
# → http://localhost:8000
```

**Seed options:**

```bash
python -m pipeline.seed --dry-run          # Scrape but don't write to DB
python -m pipeline.seed --brand kulani-kinis  # Single brand only
```

**Environment variables** (optional `.env` in `backend/`):

```
DB_PATH=./data/products.db
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

The frontend expects the API at `http://localhost:8000` by default.

---

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/products` | List products (filterable by brand, style, size, color, in_stock, price) |
| `GET` | `/products/{id}` | Single product |
| `GET` | `/brands` | List all brands |
| `GET` | `/brands/{slug}` | Brand detail + products |
| `GET` | `/search?q=` | Full-text search |
| `POST` | `/clicks/{id}` | Track click-through to brand site |

Interactive docs available at `http://localhost:8000/docs`.

---

## Data Pipeline

Products are scraped from each brand's public Shopify JSON endpoint (`/products.json`). The pipeline:

1. Paginates through all products (250 per page)
2. Extracts name, price, sale price, images, sizes, colors
3. Infers style category (`top`, `bottom`, `set`, `one-piece`) from product type + tags
4. Upserts into SQLite — re-running the seed updates existing records

**Not all brands are Shopify stores.** MIKOH (WordPress) and Maaji are currently skipped — custom scrapers are planned.

---

## Running Tests

```bash
# Backend
cd backend
pytest -q

# Frontend
cd frontend
npm test
```

---

## Roadmap

- [ ] Deploy (Vercel + Railway/Fly)
- [ ] Scheduled scraping (keep inventory fresh)
- [ ] MIKOH + Maaji custom scrapers
- [ ] Affiliate link integration (ShareASale / LTK) when approved
- [ ] Size + color availability per variant
- [ ] Saved items / wishlist
