"""
Ticket Categorizer — classifies customer inquiries by urgency and topic.
"""


class Categorizer:
    """Categorizes customer messages into urgency levels + topic."""

    URGENCY_MAP = {
        "urgent": [
            "bug", "crash", "broken", "not working", "error", "emergency",
            "acil", "bozuk", "calismiyor", "hata", "kilitlendi", "acil yardim",
        ],
        "high": [
            "refund", "charge", "payment", "lost", "missing",
            "iade", "ucret", "odeme", "kayip", "kayboldu",
        ],
        "normal": [
            "how", "help", "question", "please", "support",
            "nasil", "yardim", "soru", "lutfen", "destek",
        ],
        "low": [
            "info", "hours", "location", "contact", "price",
            "bilgi", "saat", "adres", "iletisim", "fiyat",
        ],
    }

    TOPIC_KEYWORDS = {
        "shipping": ["shipping", "delivery", "track", "kargo", "teslimat", "siparis"],
        "returns": ["return", "refund", "iade", "para iadesi", "degi"],
        "payment": ["payment", "card", "iDEAL", "odeme", "kart", "fatura"],
        "account": ["account", "password", "login", "hesap", "sifre", "giris"],
        "technical": ["bug", "error", "crash", "hata", "bug", "calismiyor"],
        "general": ["info", "question", "hours", "bilgi", "soru", "genel"],
    }

    def classify(self, message: str) -> dict:
        """Returns {urgency, topic, summary}."""
        msg_lower = message.lower()

        # ---- Urgency ----
        urgency = "normal"  # default
        for level, keywords in self.URGENCY_MAP.items():
            if any(kw in msg_lower for kw in keywords):
                urgency = level
                break

        # ---- Topic ----
        topic = "general"
        best_count = 0
        for cat, keywords in self.TOPIC_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in msg_lower)
            if count > best_count:
                best_count = count
                topic = cat

        # ---- Generate short summary ----
        summary = message[:80] + ("..." if len(message) > 80 else "")

        return {
            "urgency": urgency,
            "topic": topic,
            "summary": summary,
        }
