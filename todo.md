# TODO

## Overall Progress
- [x] Phase 1: Scaffold + Data Layer
- [x] Phase 2: Property Search Tool
- [x] Phase 3: Nova 2 Lite Chat Agent
- [x] Phase 4: FastAPI + Text Endpoints
- [~] Phase 5: Nova 2 Sonic Voice Layer — **skipped** (deadline constraint)
- [x] Phase 6: Frontend

---

## Phase 1 — Scaffold + Data Layer ✅
- [x] Project directory structure, `requirements.txt`, `config.py`
- [x] `models/property.py` (SQLAlchemy ORM, 19 columns)
- [x] `database.py` (async engine + session factory)
- [x] `scripts/seed_db.py` (CSV → PostgreSQL, batch 500, idempotent, address dedup)
- [x] `main.py` lifespan (create tables on startup)
- [x] Seeded 217 unique properties

## Phase 2 — Property Search Tool ✅
- [x] `tools/property_search.py` — 11 optional filters, ILIKE, count + limit pattern
- [x] `.unique()` on scalars to prevent ORM identity map duplicates

## Phase 3 — Nova 2 Lite Chat Agent ✅
- [x] `session_store.py` (TTL in-memory history store)
- [x] `agents/chat_agent.py` — Alex persona, toolSpec, agentic loop
- [x] Input coercion, history trimming (top 5), `<thinking>`/`<response>` tag stripping
- [x] Plain-text reply enforcement in system prompt

## Phase 4 — FastAPI + Text Endpoints ✅
- [x] `models/schemas.py` (ChatRequest, ChatResponse)
- [x] `routers/chat.py` (POST /api/chat, GET /api/session/new, farewell detection)
- [x] `main.py` — routers + StaticFiles

## Phase 5 — Nova 2 Sonic Voice Layer ⏭ Skipped

## Phase 6 — Frontend ✅
- [x] `frontend/index.html` — single file, all CSS + JS inline
- [x] Two-column layout: dark navy sidebar + chat panel
- [x] Session init (`GET /api/session/new`) + `localStorage` persistence
- [x] User/bot bubbles, typing indicator (bouncing dots)
- [x] Property cards — CSS Grid, 11 fields, null-safe, XSS-safe
- [x] Farewell state + "Start New Chat" button
- [x] 3 sidebar chips with queries matching real data
- [x] `formatReply()` strips residual markdown client-side
- [x] Mobile: sidebar hidden under 640px
