# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Hackathon Summary

**Amazon Nova AI Hackathon** — submission deadline **March 16, 2026 at 5:00 PM PT**.

- **Category**: Agentic AI (primary) + Voice AI (secondary via Nova 2 Sonic)
- **Models in use**: Nova 2 Lite (`us.amazon.nova-lite-v1:0`) + Nova 2 Sonic (`amazon.nova-sonic-v1:0`)
- **Access**: Amazon Bedrock via own AWS account (no credits available)
- **Judging**: 60% technical implementation, 20% impact, 20% creativity

**What to submit**: text description, ~3 min demo video (`#AmazonNova`), GitHub repo link.

See [`hackathon_information.md`](hackathon_information.md) for full rules, judging criteria, and submission details.

---

## Project: HomeSeeker AI

A real estate chatbot that helps prospective homebuyers find their perfect property through natural conversation.

**What it does**:
- Greets the user and intelligently gathers requirements through conversation (budget, bedrooms, location, property type, etc.)
- When enough info is collected, searches a PostgreSQL database of 3500 real property listings
- Returns matching homes as property cards in the chat UI
- Continues the conversation — refines search, answers follow-up questions — until the user says goodbye
- Voice mode via Nova 2 Sonic: fully speech-to-speech conversation

**Nova integration**:
- **Nova 2 Lite**: drives the entire conversation as an agentic tool-use loop — decides when to search, constructs queries, interprets results
- **Nova 2 Sonic**: speech-to-speech voice mode over WebSocket

**Stack**: FastAPI + PostgreSQL (local → AWS RDS) + vanilla HTML/JS frontend

---

## Plan Overview

Full details in [`implementation_plan.md`](implementation_plan.md).

| Phase | Goal | Scope |
|-------|------|-------|
| 1 | Scaffold + Data Layer | Project skeleton, SQLAlchemy ORM, PostgreSQL setup, CSV seed script |
| 2 | Property Search Tool | Dynamic SQL filter function mapping to Nova tool schema |
| 3 | Nova 2 Lite Chat Agent | Agentic tool-use loop, session history, system prompt |
| 4 | FastAPI + Text Endpoints | `/api/chat`, `/api/session/new`, full request lifecycle |
| 5 | Nova 2 Sonic Voice Layer | WebSocket endpoint, bidirectional audio streaming |
| 6 | Frontend | Single-file HTML/JS chat UI with property cards + voice toggle |

Track progress in [`todo.md`](todo.md). Update this file after each phase is complete.

---

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Seed the database (run once after creating the homeseeker DB)
python -m backend.scripts.seed_db

# Run the development server
uvicorn backend.main:app --reload --port 8000
```

## Environment

Copy `.env.example` to `.env` and fill in:
- `DATABASE_URL` — local: `postgresql+asyncpg://postgres:password@localhost/homeseeker`
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
