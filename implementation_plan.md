# Plan: HomeSeeker AI — Real Estate Chatbot (Amazon Nova Hackathon)

## Context
Building a real estate chatbot for the Amazon Nova AI Hackathon (submission deadline: March 16, 2026). The app takes natural-language homebuyer requirements, searches 3500 property listings, and returns matching homes in a chat UI. Uses **Nova 2 Lite** for agentic tool-use conversation and **Nova 2 Sonic** for voice mode. Submitting under the **Agentic AI** category with dual Nova model usage as a differentiator.

Database: **PostgreSQL** — local during development, swap to **AWS RDS** for production by changing one env var.

---

## Project Structure

```
amazon-realestate-chatbot/
├── backend/
│   ├── main.py                  # FastAPI app + lifespan (DB init)
│   ├── config.py                # Settings via pydantic-settings + .env
│   ├── database.py              # SQLAlchemy async engine + session factory
│   ├── session_store.py         # In-memory session dict (chat history + timestamps)
│   ├── agents/
│   │   ├── chat_agent.py        # Nova 2 Lite agentic tool-use loop
│   │   └── voice_agent.py       # Nova 2 Sonic bidirectional stream session
│   ├── tools/
│   │   └── property_search.py   # SQLAlchemy-based property filter function
│   ├── models/
│   │   ├── property.py          # SQLAlchemy ORM model (Property table)
│   │   └── schemas.py           # Pydantic ChatRequest / ChatResponse
│   ├── routers/
│   │   ├── chat.py              # POST /api/chat, GET /api/session/new
│   │   └── voice.py             # WebSocket /ws/voice/{session_id}
│   ├── scripts/
│   │   └── seed_db.py           # One-time CSV → PostgreSQL loader
│   └── data/
│       └── homes.csv            # 3500 MLS listings (seed source only)
├── frontend/
│   └── index.html               # Single-file chat UI (no build step)
├── requirements.txt
└── .env.example
```

---

## Tech Stack

- **Backend**: Python, FastAPI, uvicorn
- **Database**: PostgreSQL (local) → AWS RDS PostgreSQL (production)
  - SQLAlchemy 2.0 async (`sqlalchemy[asyncio]`) + `asyncpg` driver
- **AI**: `boto3` → Amazon Bedrock
  - Nova 2 Lite (`us.amazon.nova-lite-v1:0`) — text conversation + tool use
  - Nova 2 Sonic (`amazon.nova-sonic-v1:0`) — speech-to-speech voice mode
- **Frontend**: Vanilla HTML/JS/CSS, single file, served by FastAPI `StaticFiles`
- **Sessions**: In-memory `dict` (session_id → chat history + timestamp), no Redis

---

## Implementation Plan

### Phase 1: Scaffold + Data Layer

**`requirements.txt`**:
```
fastapi
uvicorn[standard]
boto3
sqlalchemy[asyncio]
asyncpg
pydantic-settings
python-multipart
```

**`config.py`** — `pydantic_settings.BaseSettings` loading from `.env`:
- `database_url`: `postgresql+asyncpg://user:pass@localhost/homeseeker` (local) → swap to RDS endpoint for prod
- `aws_region`, `nova_lite_model_id`, `nova_sonic_model_id`
- `csv_path`, `max_results`, `session_ttl_seconds`

**`models/property.py`** — SQLAlchemy `Property` ORM model:
```
id, price (Numeric), beds (Integer), baths (Numeric), sqft (Integer),
location (String), property_type (String), year_built (Integer),
listing_status (String), address (String)
```
- `Base = declarative_base()` defined here; imported by `database.py`

**`database.py`** — async engine + session factory:
```python
engine = create_async_engine(settings.database_url, pool_size=10, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

**`scripts/seed_db.py`** — one-time CSV → DB loader:
- Reads `homes.csv` with Python's `csv` module (no pandas dependency)
- Normalizes column names to snake_case
- Bulk inserts in batches of 500 using `session.execute(insert(Property), rows)`
- Run once: `python -m backend.scripts.seed_db`
- Idempotent: truncates table before insert so safe to re-run

**`main.py` lifespan**:
- On startup: `async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)`
- Creates tables if not exist; no-op if already exist

### Phase 2: Property Search Tool

**`tools/property_search.py`** — `async search_properties(db: AsyncSession, **kwargs) -> dict`:
- All params optional: `min_price`, `max_price`, `min_beds`, `max_beds`, `min_baths`, `location` (ILIKE `%value%`), `property_type` (ILIKE), `min_sqft`, `max_sqft`, `min_year_built`, `listing_status`, `max_results`
- Builds dynamic SQLAlchemy `select(Property)` with conditional `.where()` clauses
- `ORDER BY price ASC LIMIT max_results`
- Returns `{total_found: int, properties: [dict, ...], search_criteria: {applied filters}}`
- `total_found` uses a separate `count()` query before the limit
- Input params map 1:1 to the Nova tool's `inputSchema`

### Phase 3: Nova 2 Lite Chat Agent

**`session_store.py`** — `SessionStore` class:
- `get_or_create(session_id)`, `append_message(session_id, role, content)`, `get_history(session_id)`, `delete(session_id)`, `cleanup_expired()`
- Module-level singleton

**`agents/chat_agent.py`** — `ChatAgent` class with `async chat(session_id, user_message, db) -> (str, list)`:
- System prompt: Alex the friendly real estate agent — gather requirements naturally, call `search_properties` when has ≥1 criterion
- Full `toolSpec` JSON for `search_properties` matching the function signature
- **Agentic loop**: call `bedrock.converse()` (via `run_in_executor`) → if `stopReason == "tool_use"`, dispatch to `await search_properties(db, **tool_input)`, append `toolResult` to history, loop → until `stopReason == "end_turn"`
- Coerce string-typed numbers before passing to search (model may return `"500000"` instead of `500000`)
- Trim tool result content in history to top 3 properties + `total_found` to prevent context bloat
- Module-level `chat_agent` singleton

### Phase 4: FastAPI + Text Endpoints

**`models/schemas.py`** — `ChatRequest(session_id, message)`, `ChatResponse(session_id, reply, properties, is_farewell)`

**`routers/chat.py`**:
- `POST /api/chat` — injects `db: AsyncSession = Depends(get_db)`, calls `await chat_agent.chat(...)`, detects farewell phrases
- `GET /api/session/new` — returns `{"session_id": str(uuid4())}`

**`main.py`** — mounts routers + `StaticFiles("/", directory="frontend")`

### Phase 5: Nova 2 Sonic Voice Layer

**`agents/voice_agent.py`** — `VoiceSession` class:
- Wraps `boto3.invoke_model_with_bidirectional_stream` for Nova Sonic
- JSON event builders: `_session_start_event`, `_prompt_start_event` (PCM16 24kHz output, voice system prompt), `_audio_chunk_event`, `_content_block_end_event`, `_prompt_end_event`, `_session_end_event`
- All boto3 calls via `loop.run_in_executor(None, ...)` — never block the async loop
- `receive_events()` async generator yielding decoded JSON events

**`routers/voice.py`** — WebSocket `/ws/voice/{session_id}`:
- Browser → server: `{"type": "audio_chunk", "data": "<base64 PCM16>"}`, `{"type": "audio_end"}`, `{"type": "close"}`
- Server → browser: `{"type": "audio_chunk", "data": "..."}`, `{"type": "text", "data": "..."}` (transcript), `{"type": "done"}`
- Nova receive loop runs as a concurrent `asyncio.create_task()`

### Phase 6: Frontend

**`frontend/index.html`** — single file, all CSS + JS inline:
- Session init: `GET /api/session/new` on load, store in `localStorage`
- Text chat: `POST /api/chat` → render bot bubble + property cards in CSS Grid
- Property card: price (bold), beds/baths/sqft, location, listing status badge
- Voice toggle: shows mic button, opens WebSocket, captures PCM16 via `ScriptProcessorNode` (float32 → Int16Array → base64), plays response via `AudioContext`
- On `is_farewell: true`: show "Start New Chat" button

---

## Critical Data Flow

```
User message
  → POST /api/chat
  → chat_agent.chat(session_id, message, db)
  → bedrock.converse(Nova 2 Lite, history, tools)        [run_in_executor]
  → [if tool_use] await search_properties(db, **args)
      → SQLAlchemy SELECT ... WHERE ... ORDER BY price LIMIT n
      → returns {total_found, properties[]}
  → append toolResult to history, loop converse()
  → [end_turn] return (reply_text, properties_list)
  → ChatResponse → frontend renders bubble + property cards
```

---

## Local → AWS Migration Path

Only `.env` changes needed — zero code changes:
```
# Local
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/homeseeker

# AWS RDS (production)
DATABASE_URL=postgresql+asyncpg://user:pass@<rds-endpoint>.rds.amazonaws.com/homeseeker
```

When deploying to AWS:
1. Provision RDS PostgreSQL instance
2. Run `python -m backend.scripts.seed_db` once against RDS endpoint
3. Deploy FastAPI app (EC2, ECS, or App Runner)
4. Update `DATABASE_URL` in environment

---

## Key Implementation Notes

1. **Async DB + boto3**: SQLAlchemy queries are async; `bedrock.converse()` is sync — always wrap boto3 in `await loop.run_in_executor(None, fn)`
2. **History context bloat**: After tool_use, trim the toolResult stored in history to only `total_found` + top 3 property dicts. Full result lives only in the returned `properties` list.
3. **Tool input coercion**: Cast all numeric inputs at the `chat_agent.py` dispatch boundary before passing to `search_properties` — model may return strings.
4. **DB connection in tool call**: `search_properties` takes the `AsyncSession` injected from the FastAPI route so it participates in the same request lifecycle. Pass it through `ChatAgent.chat()`.
5. **Voice audio format**: Browser captures float32 → Int16Array in JS → base64 → WebSocket. Server passes raw bytes directly to Nova Sonic (PCM16 16kHz). No ffmpeg needed.
6. **ILIKE for location/type**: Use PostgreSQL `ILIKE '%value%'` for case-insensitive substring matching on location and property_type fields.

---

## Verification

1. Start local PostgreSQL, create `homeseeker` database
2. `python -m backend.scripts.seed_db` — confirm "Seeded 3500 properties"
3. `uvicorn backend.main:app --reload` — confirm "Tables ready" in startup log
4. `curl -X POST /api/chat` with a test message — confirm Nova 2 Lite responds
5. Send "I want a 3-bedroom under $400k in Austin" — confirm SQL query fires and properties return
6. Open `http://localhost:8000` — test full chat flow with property cards
7. Click voice toggle — confirm WebSocket connects and mic captures audio
8. Say "bye" — confirm `is_farewell: true` and farewell message

---

## Files to Create (all new)

- `backend/main.py`
- `backend/config.py`
- `backend/database.py`
- `backend/session_store.py`
- `backend/agents/chat_agent.py`
- `backend/agents/voice_agent.py`
- `backend/tools/property_search.py`
- `backend/models/property.py`
- `backend/models/schemas.py`
- `backend/routers/chat.py`
- `backend/routers/voice.py`
- `backend/scripts/seed_db.py`
- `frontend/index.html`
- `requirements.txt`
- `.env.example`
