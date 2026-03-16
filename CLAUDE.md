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
| 3 | Nova 2 Lite Chat Agent | ✅ Done |
| 4 | FastAPI + Text Endpoints | ⬜ |
| 5 | Nova 2 Sonic Voice Layer | ⬜ |
| 6 | Frontend | ⬜ |

Full details in [`implementation_plan.md`](implementation_plan.md). Track tasks in [`todo.md`](todo.md).

---

## Architecture

**Tech Stack**: FastAPI + PostgreSQL + asyncpg + SQLAlchemy (async) + Amazon Bedrock (Nova 2 Lite + Nova 2 Sonic) + vanilla HTML/JS

**File Structure**:
```
backend/
  config.py              # Settings via pydantic-settings (.env)
  database.py            # Async engine, AsyncSessionLocal, get_db()
  main.py                # FastAPI app, lifespan, StaticFiles
  session_store.py       # In-memory session history store ✅
  models/
    property.py          # Property ORM (19 cols)
  tools/
    property_search.py   # search_properties() — 11 filters ✅
  agents/
    chat_agent.py        # Nova 2 Lite agentic loop ✅
  routers/               # Phase 4
  scripts/
    seed_db.py           # CSV → PostgreSQL (2170 rows, idempotent)
frontend/                # Phase 6
test_phase3.py           # Phase 3 smoke test (multi-turn, verbose mode)
```

---

## What's Built (Phases 1–3)

**Phase 1 — Data Layer**
- `Property` ORM: 19 cols — price, beds, baths, sqft, address, city, state, neighborhood, property_type, year_built, listing_status, lat/lon, url, zip_code, lot_size, days_on_market, hoa_month
- Async DB setup; `seed_db.py` batch-inserts 500/tx, truncates first (idempotent)
- **DB**: 2170 properties seeded. Top cities: Brooklyn (540), Staten Island (280), Bronx (220)

**Phase 2 — Property Search Tool**
- `async search_properties(db, ...)` — 11 optional filters
- `location` → `OR(city ILIKE, neighborhood ILIKE)`; string fields use `ilike`
- Separate `COUNT(*)` for `total_found`; `ORDER BY price ASC LIMIT max_results`
- Returns `{total_found, properties: [...], search_criteria: {...}}`

**Phase 3 — Nova 2 Lite Chat Agent**
- `session_store.py` — `SessionStore`: `get_or_create`, `append_message`, `get_history`, `delete`, `cleanup_expired` (TTL-based); module-level singleton
- `agents/chat_agent.py` — `ChatAgent.chat(session_id, message, db, verbose=False) -> (str, list)`:
  - Alex persona system prompt with tool definition + DB schema inline
  - Full `toolSpec` for all 11 `search_properties` params
  - Agentic loop: `converse()` → `tool_use` → coerce inputs → `search_properties` → trim to top 3 in history → loop → `end_turn`
  - `<thinking>` tag stripping from replies
  - `verbose=True` prints each loop iteration, tool inputs, and tool results
  - Module-level `chat_agent` singleton

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
- `DATABASE_URL` — `postgresql+asyncpg://aryan@localhost/homeseeker`
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

**Test Phase 3 agent**:
```bash
python -m test_phase3   # VERBOSE=True in script to see loop trace
```
Sends 3 messages in one session; verifies tool dispatch, multi-turn history, and property results.
