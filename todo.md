# TODO

## Overall Progress
- [x] Phase 1: Scaffold + Data Layer
- [x] Phase 2: Property Search Tool
- [x] Phase 3: Nova 2 Lite Chat Agent
- [x] Phase 4: FastAPI + Text Endpoints
- [ ] Phase 5: Nova 2 Sonic Voice Layer
- [ ] Phase 6: Frontend

---

## Phase 1 — Scaffold + Data Layer ✅
- [x] Create project directory structure
- [x] `requirements.txt`
- [x] `config.py` (pydantic-settings, .env, csv_path)
- [x] `models/property.py` (SQLAlchemy ORM, 19 columns)
- [x] `database.py` (async engine + session factory)
- [x] `scripts/seed_db.py` (CSV → PostgreSQL, batch 500, idempotent)
- [x] Place `homes.csv` in `backend/data/`
- [x] `main.py` lifespan (create tables on startup)
- [x] Create local PostgreSQL `homeseeker` database
- [x] Seeded 2170 properties, verified with psql queries

## Phase 2 — Property Search Tool ✅
- [x] `tools/property_search.py`
- [x] All optional filter params with dynamic WHERE clauses
- [x] ILIKE for location and property_type
- [x] count() + limit query pattern
- [x] Verify correct results returned for sample queries (42/42 tests passed)

## Phase 3 — Nova 2 Lite Chat Agent ✅
- [x] `session_store.py` (in-memory history store)
- [x] `agents/chat_agent.py`
- [x] System prompt (Alex persona)
- [x] toolSpec JSON for search_properties
- [x] Agentic tool-use loop
- [x] String-to-number coercion on tool inputs
- [x] History trimming after tool results
- [x] Verify end-to-end (multi-turn, verbose, tool dispatch confirmed)

## Phase 4 — FastAPI + Text Endpoints ✅
- [x] `models/schemas.py` (ChatRequest, ChatResponse)
- [x] `routers/chat.py` (POST /api/chat, GET /api/session/new)
- [x] Complete `main.py` (routers + StaticFiles)
- [x] End-to-end text chat test in browser

## Phase 5 — Nova 2 Sonic Voice Layer
- [ ] `agents/voice_agent.py` (VoiceSession + event builders)
- [ ] `routers/voice.py` (WebSocket endpoint)
- [ ] Concurrent asyncio send/receive tasks
- [ ] Test WebSocket connection and audio round-trip

## Phase 6 — Frontend
- [ ] `frontend/index.html` (single file)
- [ ] Session init + localStorage
- [ ] Text chat UI with bot/user bubbles
- [ ] Property cards (CSS Grid)
- [ ] Voice mode toggle + mic capture (ScriptProcessorNode)
- [ ] Audio playback (AudioContext)
- [ ] Farewell state + "Start New Chat" button
- [ ] Full end-to-end demo
