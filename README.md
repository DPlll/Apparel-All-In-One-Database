<p align="center">
  <img src="https://img.shields.io/badge/style-bikini%20season-ff6eb4?style=for-the-badge" />
  <img src="https://img.shields.io/badge/stack-Next.js%20%7C%20FastAPI-00c2cb?style=for-the-badge" />
  <img src="https://img.shields.io/badge/products-7%2C100%2B-ffd166?style=for-the-badge" />
</p>

<h1 align="center">🌊 Where'd You Get Your Bikini? 👙</h1>

<p align="center">
  <em>Your one-stop destination for women's swimwear — browse styles from the best bikini brands, all in one place.</em>
</p>

---

## What It Does

Aggregates inventory from top Shopify-powered swimwear brands into a clean, filterable catalog. No affiliate redirects, no clutter — just find something you love and go straight to the brand to buy it.

### Brands

| Brand | Status |
|---|---|
| Frankies Bikinis | ✅ Live |
| Monday Swimwear | ✅ Live |
| Kulani Kinis | ✅ Live |
| Hunza G | ✅ Live |
| MIKOH | 🔜 Coming soon |
| Maaji | 🔜 Coming soon |

**~7,100+ products**, updated on demand.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, Tailwind CSS 4 |
| Backend | FastAPI, Python 3.12, SQLite |
| Data Pipeline | Custom Shopify JSON scraper |
| Testing | pytest · Jest · Testing Library |

---

## Project Structure

```
.
├── backend/
│   ├── api/               # FastAPI app — routes for products, brands, search, clicks
│   ├── pipeline/
│   │   ├── scrapers/      # Shopify scraper + per-brand configs
│   │   ├── models.py      # Product dataclass
│   │   ├── database.py    # SQLite connection + upsert logic
│   │   ├── seed.py        # CLI seed script
│   │   └── run.py         # Full pipeline runner
│   ├── tests/             # pytest suite (39 tests)
│   └── requirements.txt
└── frontend/
    ├── app/               # Next.js App Router
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
python -m pipeline.seed --dry-run                 # Scrape without writing to DB
python -m pipeline.seed --brand kulani-kinis      # Single brand only
```

**Environment variables** (optional `.env` in `backend/`):

```env
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

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/products` | List products — filter by brand, style, size, color, in_stock, price |
| `GET` | `/products/{id}` | Single product detail |
| `GET` | `/brands` | List all brands |
| `GET` | `/brands/{slug}` | Brand detail + its products |
| `GET` | `/search?q=` | Full-text search |
| `POST` | `/clicks/{id}` | Track click-through to brand site |

Interactive docs: `http://localhost:8000/docs`

---

## Data Pipeline

Products are scraped from each brand's public Shopify JSON endpoint (`/products.json`). The pipeline:

1. Paginates through all products (250 per page)
2. Extracts name, price, sale price, images, sizes, and colors
3. Infers style category — `top`, `bottom`, `set`, or `one-piece` — from product type and tags
4. Upserts into SQLite, so re-running the seed refreshes existing records without duplicates

> Non-Shopify brands like MIKOH (WordPress) and Maaji are currently skipped — custom scrapers are in the roadmap.

---

## Running Tests

```bash
# Backend
cd backend && pytest -q

# Frontend
cd frontend && npm test
```

---

## Roadmap

- [ ] Deploy — Vercel (frontend) + Railway or Fly (backend)
- [ ] Scheduled scraping to keep inventory fresh
- [ ] MIKOH + Maaji custom scrapers
- [ ] Affiliate link integration (ShareASale / LTK)
- [ ] Per-variant size + color availability
- [ ] Saved items / wishlist
