# TODO

## Overall Progress
- [ ] Phase 1: Scaffold + Data Layer
- [ ] Phase 2: Property Search Tool
- [ ] Phase 3: Nova 2 Lite Chat Agent
- [ ] Phase 4: FastAPI + Text Endpoints
- [ ] Phase 5: Nova 2 Sonic Voice Layer
- [ ] Phase 6: Frontend

---

## Phase 1 — Scaffold + Data Layer
- [ ] Create project directory structure
- [ ] `requirements.txt`
- [ ] `config.py` (pydantic-settings, .env)
- [ ] `models/property.py` (SQLAlchemy ORM)
- [ ] `database.py` (async engine + session factory)
- [ ] `scripts/seed_db.py` (CSV → PostgreSQL)
- [ ] Place `homes.csv` in `backend/data/`
- [ ] `main.py` lifespan (create tables on startup)
- [ ] Create local PostgreSQL `homeseeker` database
- [ ] Run seed script, verify 3500 rows loaded

## Phase 2 — Property Search Tool
- [ ] `tools/property_search.py`
- [ ] All optional filter params with dynamic WHERE clauses
- [ ] ILIKE for location and property_type
- [ ] count() + limit query pattern
- [ ] Verify correct results returned for sample queries

## Phase 3 — Nova 2 Lite Chat Agent
- [ ] `session_store.py` (in-memory history store)
- [ ] `agents/chat_agent.py`
- [ ] System prompt (Alex persona)
- [ ] toolSpec JSON for search_properties
- [ ] Agentic tool-use loop
- [ ] String-to-number coercion on tool inputs
- [ ] History trimming after tool results
- [ ] Verify end-to-end via curl

## Phase 4 — FastAPI + Text Endpoints
- [ ] `models/schemas.py` (ChatRequest, ChatResponse)
- [ ] `routers/chat.py` (POST /api/chat, GET /api/session/new)
- [ ] Complete `main.py` (routers + StaticFiles)
- [ ] End-to-end text chat test in browser

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
