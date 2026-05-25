"""
Ticket Categorizer — classifies customer inquiries by urgency and topic.
Keyword-based, zero API cost. Fast enough for real-time classification.
"""


class Categorizer:
    """Categorizes customer messages into urgency levels + topic."""

    URGENCY_MAP = {
        "urgent": [
            "bug", "crash", "broken", "not working", "error", "emergency",
            "acil", "bozuk", "calismiyor", "hata", "kilitlendi", "acil yardim",
            "yardım edin", "hemen", "cozulmedi", "çözülmedi",
            "spoed", "storing", "kapot", "noodgeval", "niet werkend",
        ],
        "high": [
            "refund", "charge", "payment", "lost", "missing", "wrong",
            "iade", "ucret", "odeme", "kayip", "kayboldu", "yanlis", "yank",
            "terugbetaling", "kwijt", "verkeerd", "betaling",
        ],
        "normal": [
            "how", "help", "question", "please", "support", "can you",
            "nasil", "yardim", "soru", "lutfen", "destek", "yapabilir",
            "hoe", "hulp", "vraag", "alsjeblieft", "ondersteuning",
        ],
        "low": [
            "info", "hours", "location", "contact", "price", "opening",
            "bilgi", "saat", "adres", "iletisim", "fiyat",
            "informatie", "tijden", "locatie", "contact", "prijs",
        ],
    }

    # Stem-friendly: include common inflected forms
    TOPIC_KEYWORDS = {
        "shipping": [
            "shipping", "delivery", "track", "shipment", "order", "arrive",
            "kargo", "teslimat", "sipari", "gonderi", "kurye", "ulasmadi",
            "verzending", "levering", "bestelling", "track", "trace",
        ],
        "returns": [
            "return", "refund", "exchange", "replace",
            "iade", "para iadesi", "degis", "degistir", "iptal",
            "retour", "terugbetaling", "omruilen", "annuleren",
        ],
        "payment": [
            "payment", "card", "credit", "invoice", "bill", "charge",
            "odeme", "kart", "fatura", "banka", "hesap no",
            "betaling", "creditcard", "factuur", "rekening",
        ],
        "account": [
            "account", "password", "login", "sign in", "register",
            "hesap", "sifre", "giris", "kayit", "profile",
            "account", "wachtwoord", "inloggen", "registreren",
        ],
        "technical": [
            "bug", "error", "crash", "not loading", "freeze", "timeout",
            "hata", "bug", "calismiyor", "yuklenmiyor", "dondu",
            "fout", "crash", "laadt niet", "bevroren",
        ],
    }

    # Always falls back to "general"
    GENERAL = ["info", "question", "hours", "other",
               "bilgi", "soru", "genel", "diger",
               "informatie", "vraag", "algemeen", "overig"]

    def classify(self, message: str) -> dict:
        """
        Returns dict: {urgency, topic, summary}.

        Urgency is first-match (urgent > high > normal > low).
        Topic is best-match (highest keyword count wins).
        """
        msg_lower = message.lower()

        # ---- Urgency (first match wins) ----
        urgency = "low"
        for level in ["urgent", "high", "normal", "low"]:
            if any(kw in msg_lower for kw in self.URGENCY_MAP[level]):
                urgency = level
                break

        # ---- Topic (best match wins) ----
        topic = "general"
        best_count = 0
        for cat, keywords in self.TOPIC_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in msg_lower)
            if count > best_count:
                best_count = count
                topic = cat

        # ---- Short summary ----
        summary = message[:80] + ("..." if len(message) > 80 else "")

        return {
            "urgency": urgency,
            "topic": topic,
            "summary": summary,
        }
