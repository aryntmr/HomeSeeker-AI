from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.agents.chat_agent import chat_agent
from backend.models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api")

FAREWELL_PHRASES = {"bye", "goodbye", "see you", "thanks", "thank you", "that's all", "thats all", "done", "exit", "quit"}


def _is_farewell(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in FAREWELL_PHRASES)


@router.get("/session/new")
async def new_session():
    return {"session_id": str(uuid4())}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    reply, properties = await chat_agent.chat(request.session_id, request.message, db)
    is_farewell = _is_farewell(request.message) or _is_farewell(reply)
    return ChatResponse(
        session_id=request.session_id,
        reply=reply,
        properties=properties,
        is_farewell=is_farewell,
    )
