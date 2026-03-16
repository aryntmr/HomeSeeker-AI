import time
from backend.config import settings


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def get_or_create(self, session_id: str) -> dict:
        if session_id not in self._sessions:
            self._sessions[session_id] = {"history": [], "last_active": time.time()}
        return self._sessions[session_id]

    def append_message(self, session_id: str, role: str, content: list) -> None:
        session = self.get_or_create(session_id)
        session["history"].append({"role": role, "content": content})
        session["last_active"] = time.time()

    def get_history(self, session_id: str) -> list:
        return self.get_or_create(session_id)["history"]

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def cleanup_expired(self) -> None:
        now = time.time()
        expired = [
            sid
            for sid, data in self._sessions.items()
            if now - data["last_active"] > settings.session_ttl_seconds
        ]
        for sid in expired:
            del self._sessions[sid]


session_store = SessionStore()
