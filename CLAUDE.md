# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Hackathon Summary

**Amazon Nova AI Hackathon** — submission deadline **March 16, 2026 at 5:00 PM PT**.

- **Category**: Agentic AI (primary) + Voice AI (secondary via Nova 2 Sonic)
- **Models**: Nova 2 Lite (`us.amazon.nova-lite-v1:0`) + Nova 2 Sonic (`amazon.nova-sonic-v1:0`)
- **Judging**: 60% technical, 20% impact, 20% creativity

---

## Project: HomeSeeker AI

Real estate chatbot — natural conversation → search 2170 NYC property listings → property cards in UI. Voice mode via Nova 2 Sonic.

**Stack**: FastAPI + PostgreSQL + vanilla HTML/JS frontend + Amazon Bedrock

---

## Phase Progress

| Phase | Goal | Status |
|-------|------|--------|
| 1 | Scaffold + Data Layer | ✅ Done |
| 2 | Property Search Tool | ⬜ |
| 3 | Nova 2 Lite Chat Agent | ⬜ |
| 4 | FastAPI + Text Endpoints | ⬜ |
| 5 | Nova 2 Sonic Voice Layer | ⬜ |
| 6 | Frontend | ⬜ |

Full details in [`implementation_plan.md`](implementation_plan.md). Track tasks in [`todo.md`](todo.md).

---

## Phase 1 — What Was Built

- `backend/config.py` — `Settings(BaseSettings)`: `database_url`, `csv_path`, AWS creds, model IDs, `max_results`, `session_ttl_seconds`
- `backend/models/property.py` — `Property` ORM (19 cols): price, beds, baths, sqft, city, state, neighborhood, property_type, year_built, listing_status, lat/lon, url, etc.
- `backend/database.py` — async engine, `AsyncSessionLocal`, `get_db()` dependency; re-exports `Base`
- `backend/main.py` — FastAPI lifespan (`create_all` → "Tables ready"), `StaticFiles` on `/`
- `backend/scripts/seed_db.py` — reads `csv_path`, maps 18 CSV cols → DB, batch-inserts 500/tx, truncates first (idempotent)
- `backend/session_store.py` — stub (Phase 3)
- Subpackage stubs: `agents/`, `tools/`, `models/`, `routers/`

**DB**: 2170 properties seeded. All have price. Top cities: Brooklyn (540), Staten Island (280), Bronx (220).

---

## Key Commands

```bash
# Setup (use venv)
python -m venv .venv && .venv/bin/pip install -r requirements.txt

# Seed DB (run once)
python -m backend.scripts.seed_db

# Dev server
uvicorn backend.main:app --reload --port 8000
```

## Environment

Copy `.env.example` → `.env`:
- `DATABASE_URL` — e.g. `postgresql+asyncpg://aryan@localhost/homeseeker`
- `CSV_PATH` — default: `backend/data/homes.csv`
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
