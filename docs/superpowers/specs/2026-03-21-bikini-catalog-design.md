# Bikini Catalog Aggregator — Design Spec

**Date:** 2026-03-21
**Status:** Draft
**Repo:** DPlll/Apparel-All-In-One-Database

---

## Overview

A women's bikini catalog aggregator — one website that consolidates product listings from 10-20 top swimwear brands. Users browse and search across all brands in one place, click through to buy on the brand's site via affiliate links.

**Revenue at launch:** Affiliate commissions only. No ads. Clean experience.
**Future revenue:** Featured brand placements, newsletter sponsorships, social content.

---

## Architecture

Three independent layers, each with a single responsibility:

```
[Brand Sites / Affiliate Feeds]
          ↓
  [Data Pipeline — Python]
     scraper + feed parser
          ↓
    [SQLite Database]
     normalized products
          ↓
  [FastAPI Backend — Python]
       REST API
          ↓
  [Next.js Frontend]
   catalog + search UI
```

---

## Layer 1: Data Pipeline

**Purpose:** Pull product data from brands, normalize it, store it.

**Sources (priority order):**
1. Affiliate network feeds (ShareASale, CJ Affiliate, Rakuten) — structured CSV/XML, most reliable
2. Web scraping fallback — for brands not on affiliate networks

**Normalized product schema:**
```python
{
  "id":          str,       # brand_slug + sku
  "brand":       str,       # e.g. "Frankies Bikinis"
  "brand_slug":  str,       # e.g. "frankies-bikinis"
  "name":        str,       # product name
  "price":       float,     # USD
  "sale_price":  float,     # nullable
  "image_url":   str,       # primary product image
  "affiliate_url": str,     # tracked outbound link
  "style":       str,       # top / bottom / set / one-piece
  "colors":      list[str], # ["black", "white"]
  "sizes":       list[str], # ["XS", "S", "M", "L"]
  "in_stock":    bool,
  "updated_at":  datetime
}
```

**Scheduler:** Runs daily via cron or manual trigger. Re-fetches all feeds, upserts changed products, marks out-of-stock items.

**Launch brands (10-15):**
Frankies Bikinis, Triangl, Monday Swimwear, Kulani Kinis, Vitamin A, L*Space, Vix Swimwear, Camila Coelho, PQ Swim, Cleonie, Hunza G, MIKOH, Maaji

---

## Layer 2: Backend API (FastAPI)

**Purpose:** Serve filtered, paginated product data to the frontend.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/products` | List products with filters + pagination |
| GET | `/products/{id}` | Single product detail |
| GET | `/brands` | List all brands with product counts |
| GET | `/search?q=` | Full-text search across name, brand, color |
| POST | `/click/{id}` | Log affiliate click, return affiliate_url |

**Filter params for `/products`:**
`brand`, `style`, `color`, `size`, `min_price`, `max_price`, `in_stock`, `sort` (price_asc, price_desc, newest)

**Pagination:** cursor-based, 24 products per page (grid-friendly).

---

## Layer 3: Frontend (Next.js)

**Purpose:** Browsable, searchable product catalog with a light feminine aesthetic.

**Design direction:** Clean white/cream background, soft pink/coral accents, minimal chrome. Product imagery is the hero. Mobile-first.

**Pages:**

- `/` — Homepage: hero banner (placeholder name + tagline), featured brands strip, new arrivals grid
- `/catalog` — Full catalog: filter sidebar (brand, style, color, size, price), product grid, search bar
- `/brands/[slug]` — Single brand page: brand header, all products from that brand
- `/product/[id]` — Product detail: large image, price, sizes, colors, "Shop at [Brand]" CTA button → affiliate link

**Product card:**
- Product image (full bleed)
- Brand name (small, muted)
- Product name
- Price (sale price if applicable)
- "Shop Now" → affiliate link (opens in new tab)

**No user accounts at launch.** No cart. No checkout. Pure catalog + affiliate redirect.

---

## Data Flow

```
User visits /catalog
    → Next.js calls GET /products?filters
    → FastAPI queries SQLite
    → Returns paginated JSON
    → Grid renders product cards

User clicks "Shop Now"
    → POST /click/{id} (logs click for analytics)
    → Redirect to affiliate_url in new tab
    → Brand site handles checkout
    → Affiliate network tracks sale → commission paid
```

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Data pipeline | Python 3.11, requests, BeautifulSoup, feedparser |
| Database | SQLite (upgradeable to Postgres when traffic grows) |
| Backend | FastAPI, uvicorn |
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| Hosting | Vercel (frontend) + Railway or Render (backend) |
| Affiliate networks | ShareASale, CJ Affiliate, Rakuten |

---

## MVP Scope (Launch)

**In:**
- 10-15 brands
- Browse + filter catalog
- Search
- Product detail page
- Affiliate click tracking
- Mobile responsive
- Placeholder name/logo

**Out (post-launch):**
- User accounts / wishlists
- Email newsletter
- Featured brand placements
- Display ads
- Social content integration
- Size guides

---

## Revenue Model

**Launch:** Affiliate commissions (5-15% per sale, tracked via network)

**Phase 2:**
- Newsletter — weekly "new drops" email, sponsored slots
- Featured placements — brands pay for homepage/top-of-results visibility
- TikTok/Instagram content — short-form showing finds, affiliate links in bio

---

## Open Questions

1. **Site name** — TBD, need to brainstorm
2. **Logo** — TBD, placeholder at launch
3. **Affiliate network signup** — need to apply to ShareASale/CJ for each brand
4. **Hosting costs** — Vercel free tier + Railway $5/mo should cover MVP
