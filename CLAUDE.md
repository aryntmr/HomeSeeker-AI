# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Hackathon Summary

**Amazon Nova AI Hackathon** — deadline **March 16, 2026 at 5:00 PM PT**.

- **Category**: Agentic AI (primary)
- **Models**: Nova 2 Lite (`us.amazon.nova-lite-v1:0`)
- **Judging**: 60% technical, 20% impact, 20% creativity

---

## Project: HomeSeeker AI

Real estate chatbot — natural conversation → search 217 unique NYC property listings → property cards in UI.

---

## Phase Progress

| Phase | Goal | Status |
|-------|------|--------|
| 1 | Scaffold + Data Layer | ✅ Done |
| 2 | Property Search Tool | ✅ Done |
| 3 | Nova 2 Lite Chat Agent | ✅ Done |
| 4 | FastAPI + Text Endpoints | ✅ Done |
| 5 | Nova 2 Sonic Voice Layer | ⏭ Skipped |
| 6 | Frontend | ✅ Done |

---

## Architecture

**Tech Stack**: FastAPI + PostgreSQL + asyncpg + SQLAlchemy (async) + Amazon Bedrock (Nova 2 Lite) + vanilla HTML/JS

**File Structure**:
```
backend/
  config.py              # Settings via pydantic-settings (.env)
  database.py            # Async engine, AsyncSessionLocal, get_db()
  main.py                # FastAPI app, lifespan, routers, StaticFiles
  session_store.py       # TTL-based in-memory session history store
  models/
    property.py          # Property ORM (19 cols)
    schemas.py           # ChatRequest / ChatResponse Pydantic models
  tools/
    property_search.py   # search_properties() — 11 filters, .unique() dedup
  agents/
    chat_agent.py        # Nova 2 Lite agentic loop; strips <response>/<thinking> tags
  routers/
    chat.py              # POST /api/chat, GET /api/session/new
  scripts/
    seed_db.py           # CSV → PostgreSQL (217 unique rows, deduped by address)
  data/
    homes.csv            # Raw Redfin export (2170 rows; 217 unique after dedup)
frontend/
  index.html             # Single-file UI — sidebar + chat + property cards
```

---

## Key Implementation Notes

- **DB**: 217 unique properties after address-dedup in `seed_db.py`. CSV had each row ×10.
- **Agent**: `full_properties` uses `trimmed["properties"]` (top 5) so reply text and cards are always consistent.
- **Reply format**: System prompt instructs Alex to reply in plain text, 1–2 sentences, no markdown. `<response>` and `<thinking>` tags stripped in `_strip_thinking()`.
- **Frontend**: Session UUID in `localStorage('hs_session_id')`; reused on refresh. Farewell disables input + shows "Start New Chat". `formatReply()` strips residual markdown client-side.

---

## Build & Validation

**Requirements** (`requirements.txt`):
```
fastapi, uvicorn[standard], boto3, sqlalchemy[asyncio], asyncpg, pydantic-settings, python-multipart
```

**Setup**:
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # fill in DATABASE_URL and AWS creds
python -m backend.scripts.seed_db
uvicorn backend.main:app --reload --port 8000
# open http://localhost:8000
```

**Environment** (`.env`):
- `DATABASE_URL` — `postgresql+asyncpg://user@localhost/homeseeker`
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

**Smoke test**:
1. Sidebar + Alex greeting visible on load
2. Click a chip → typing dots → property cards render (no duplicates)
3. Follow-up message → updated cards (multi-turn memory works)
4. "thanks" → input disabled + "Start New Chat" button
5. "Start New Chat" → localStorage cleared, page reloads
