# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Hackathon Summary

**Amazon Nova AI Hackathon** — deadline **March 16, 2026 at 5:00 PM PT**.

- **Category**: Agentic AI (primary) + Voice AI (secondary via Nova 2 Sonic)
- **Models**: Nova 2 Lite (`us.amazon.nova-lite-v1:0`) + Nova 2 Sonic (`amazon.nova-sonic-v1:0`)
- **Judging**: 60% technical, 20% impact, 20% creativity

---

## Project: HomeSeeker AI

Real estate chatbot — natural conversation → search 2170 NYC property listings → property cards in UI. Voice mode via Nova 2 Sonic.

---

## Phase Progress

| Phase | Goal | Status |
|-------|------|--------|
| 1 | Scaffold + Data Layer | ✅ Done |
| 2 | Property Search Tool | ✅ Done |
| 3 | Nova 2 Lite Chat Agent | ⬜ |
| 4 | FastAPI + Text Endpoints | ⬜ |
| 5 | Nova 2 Sonic Voice Layer | ⬜ |
| 6 | Frontend | ⬜ |

Full details in [`implementation_plan.md`](implementation_plan.md). Track tasks in [`todo.md`](todo.md).

---

## Architecture

**Tech Stack**: FastAPI + PostgreSQL + asyncpg + SQLAlchemy (async) + Amazon Bedrock + vanilla HTML/JS

**File Structure**:
```
backend/
  config.py            # Settings via pydantic-settings (.env)
  database.py          # Async engine, AsyncSessionLocal, get_db()
  main.py              # FastAPI app, lifespan, StaticFiles
  session_store.py     # Stub — Phase 3
  models/
    property.py        # Property ORM (19 cols)
  tools/
    property_search.py # search_properties() — Phase 2 ✅
  agents/              # Stub — Phase 3
  routers/             # Stub — Phase 4
  scripts/
    seed_db.py         # CSV → PostgreSQL (2170 rows, idempotent)
frontend/              # Phase 6
```

---

## What's Built (Phases 1–2)

**Phase 1 — Data Layer**
- `Property` ORM: price, beds, baths, sqft, address, city, state, neighborhood, property_type, year_built, listing_status, lat/lon, url, zip_code, lot_size, days_on_market, hoa_month
- Async DB setup; `seed_db.py` batch-inserts 500/tx, truncates first (idempotent)
- **DB**: 2170 properties seeded. Top cities: Brooklyn (540), Staten Island (280), Bronx (220)

**Phase 2 — Property Search Tool**
- `backend/tools/property_search.py` — `async search_properties(db, ...)`
- 11 optional filters: min/max price, min/max beds, min_baths, location, property_type, min/max sqft, min_year_built, listing_status
- `location` → `OR(city ILIKE, neighborhood ILIKE)`; string fields use `ilike`
- Separate `COUNT(*)` query for `total_found`; main query `ORDER BY price ASC LIMIT max_results`
- Returns `{total_found, properties: [...], search_criteria: {applied filters}}`
- 42/42 tests passed (all filters, edge cases, combined filters)

---

## Build & Validation

**Requirements** (`requirements.txt`):
```
fastapi, uvicorn[standard], boto3, sqlalchemy[asyncio], asyncpg, pydantic-settings, python-multipart
```

**Setup**:
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL and AWS creds
python -m backend.scripts.seed_db
uvicorn backend.main:app --reload --port 8000
```

**Environment** (`.env`):
- `DATABASE_URL` — e.g. `postgresql+asyncpg://aryan@localhost/homeseeker`
- `CSV_PATH` — default: `backend/data/homes.csv`
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

**Validate search tool**:
```python
from backend.tools.property_search import search_properties
r = await search_properties(db, location="Brooklyn", min_beds=3, max_results=5)
# r["total_found"] == 270, results sorted by price ASC
```
