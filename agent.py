"""
Agent — The core AI agent that processes customer messages.
Loads knowledge, classifies intent, and generates helpful replies.
"""

from datetime import datetime, timezone
from knowledge_base import KnowledgeBase
from categorizer import Categorizer
from storage import Storage


class CustomerSupportAgent:
    """
    AI-powered customer support agent.

    Flow:
      1. Receive customer message
      2. Classify urgency + topic
      3. Search knowledge base
      4. Generate response (AI or template-based)
    """

    def __init__(self):
        self.kb = KnowledgeBase()
        self.categorizer = Categorizer()
        self.storage = Storage()
        self.kb.load_defaults()

    def handle(self, message: str, session_id: str | None = None) -> dict:
        """
        Process a customer message end-to-end.

        Returns:
            {
                "reply": "...",
                "classification": {urgency, topic, summary},
                "sources": [...],
            }
        """
        if session_id is None:
            session_id = f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # Step 1: Classify
        classification = self.categorizer.classify(message)

        # Step 2: Search knowledge base
        sources = self.kb.search(message, top_k=2)

        # Step 3: Generate reply
        reply = self._generate_reply(message, classification, sources)

        # Step 4: Log
        self.storage.save_message(session_id, "customer", message, classification)
        self.storage.save_message(session_id, "agent", reply)

        return {
            "reply": reply,
            "classification": classification,
            "sources": [s["id"] for s in sources],
            "session_id": session_id,
        }

    def _generate_reply(
        self, message: str, classification: dict, sources: list[dict]
    ) -> str:
        """Generate a context-aware reply using KB results."""
        # Emoji prefix based on urgency
        urgency_emoji = {
            "urgent": "🚨",
            "high": "⚠️",
            "normal": "ℹ️",
            "low": "💬",
        }.get(classification["urgency"], "💬")

        topic_emoji = {
            "shipping": "📦",
            "returns": "🔄",
            "payment": "💳",
            "account": "🔑",
            "technical": "🔧",
            "general": "📋",
        }.get(classification["topic"], "💬")

        # Build reply
        lines = [f"{urgency_emoji} **{classification['urgency'].upper()}** | {topic_emoji} {classification['topic']}"]

        if sources:
            # Use the most relevant source
            best = sources[0]
            lines.append("")
            lines.append(best["content"])
        else:
            lines.append("")
            lines.append(
                "Thank you for your message. I've noted your inquiry and will make "
                "sure the right team looks into it. Is there anything else I can help you with?"
                if "en" in message.lower()
                else "Mesajınız için teşekkürler. Talebinizi not aldım, ilgili ekip en kısa sürede size dönecektir."
            )

        # Escalation hint if urgent
        if classification["urgency"] == "urgent":
            lines.append("")
            lines.append("⏰ *This has been flagged as urgent. A human agent will be notified immediately.*")

        return "\n".join(lines)
