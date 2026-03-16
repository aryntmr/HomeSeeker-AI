"""
Phase 3 smoke test — run with:
  python -m test_phase3
Requires .env with DATABASE_URL + AWS credentials.
"""
import asyncio
import uuid
from backend.database import AsyncSessionLocal
from backend.agents.chat_agent import chat_agent
from backend.session_store import session_store


async def main():
    session_id = str(uuid.uuid4())
    print(f"Session: {session_id}\n{'='*60}")

    VERBOSE = True  # set False to hide agent internals

    messages = [
        "Hey! I'm looking for a place in Brooklyn.",
        "Budget is around $600k, need at least 2 bedrooms.",
        "Actually, can you also check Manhattan under $2.8M with same beds?",
    ]

    async with AsyncSessionLocal() as db:
        for user_msg in messages:
            print(f"\nUSER: {user_msg}")
            reply, properties = await chat_agent.chat(session_id, user_msg, db, verbose=VERBOSE)
            print(f"ALEX: {reply}")
            if properties:
                print(f"  → {len(properties)} properties returned (first: {properties[0].get('address')}, ${properties[0].get('price'):,})")

    print(f"\n{'='*60}")
    print("Session history turns:", len(session_store.get_history(session_id)))
    history = session_store.get_history(session_id)
    for i, msg in enumerate(history):
        role = msg["role"]
        content_summary = []
        for block in msg["content"]:
            if "text" in block:
                content_summary.append(f"text({len(block['text'])} chars)")
            elif "toolUse" in block:
                content_summary.append(f"toolUse({block['toolUse']['name']})")
            elif "toolResult" in block:
                content_summary.append("toolResult")
        print(f"  [{i}] {role}: {', '.join(content_summary)}")


if __name__ == "__main__":
    asyncio.run(main())
