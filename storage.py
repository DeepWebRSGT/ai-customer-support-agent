"""
Storage — Lightweight JSON-based conversation logging.
Drop-in replace with SQLite, PostgreSQL, or any DB later.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


class Storage:
    """Logs conversations to a JSON file."""

    def __init__(self, path: str = "sessions.json"):
        self.path = Path(path)
        self._ensure_file()

    def _ensure_file(self):
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def save_message(self, session_id: str, role: str, content: str, classification: dict | None = None):
        """Save a single message to the session log."""
        records = json.loads(self.path.read_text(encoding="utf-8"))

        entry = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "content": content,
        }
        if classification:
            entry["classification"] = classification

        records.append(entry)
        self.path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def get_session(self, session_id: str) -> list[dict]:
        """Retrieve all messages for a session."""
        records = json.loads(self.path.read_text(encoding="utf-8"))
        return [r for r in records if r["session_id"] == session_id]

    def get_stats(self) -> dict:
        """Quick session statistics."""
        records = json.loads(self.path.read_text(encoding="utf-8"))
        total = len(records)
        sessions = len(set(r["session_id"] for r in records))
        return {"total_messages": total, "total_sessions": sessions}
