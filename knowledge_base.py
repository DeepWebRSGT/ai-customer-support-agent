"""
Knowledge Base — In-memory document storage with semantic search.
Hot-plug: swap with Pinecone, ChromaDB, or any vector store.
"""


class KnowledgeBase:
    """Simple keyword + vector hybrid knowledge base for demo purposes."""

    def __init__(self):
        self.documents: list[dict] = []

    def load_defaults(self):
        """Load sample knowledge base entries (TR + EN)."""
        self.documents = [
            # ---- Shipping ----
            {
                "id": "shipping-1",
                "category": "shipping",
                "keywords": ["shipping", "delivery", "shipment", "kargo", "teslimat", "gönderi"],
                "lang": "tr",
                "content": (
                    "Standart teslimat 3-5 iş günü sürer. Hızlı teslimat (ek ücretli) 1-2 iş günü."
                ),
            },
            {
                "id": "shipping-2",
                "category": "shipping",
                "keywords": ["shipping", "delivery", "tracking", "takip"],
                "lang": "en",
                "content": (
                    "Standard delivery takes 3-5 business days. Express (extra fee) takes 1-2 days."
                ),
            },
            # ---- Returns ----
            {
                "id": "returns-1",
                "category": "returns",
                "keywords": ["return", "refund", "iade", "para iadesi", "iptal"],
                "lang": "tr",
                "content": (
                    "İade süresi 14 gün. Ürün kullanılmamış ve orijinal kutusunda olmalı. "
                    "İade başvurusu için destek@ornek.com adresine e-posta gönderin."
                ),
            },
            {
                "id": "returns-2",
                "category": "returns",
                "keywords": ["return", "refund", "cancellation"],
                "lang": "en",
                "content": (
                    "Return window is 14 days. Item must be unused and in original packaging. "
                    "Email support@example.com to start a return."
                ),
            },
            # ---- Hours ----
            {
                "id": "hours-1",
                "category": "hours",
                "keywords": ["hours", "working hours", "open", "çalışma saatleri", "açık"],
                "lang": "tr",
                "content": (
                    "Hafta içi 09:00 - 18:00. Cumartesi 10:00 - 15:00. Pazar kapalı."
                ),
            },
            {
                "id": "hours-2",
                "category": "hours",
                "keywords": ["hours", "opening hours", "working hours"],
                "lang": "en",
                "content": (
                    "Weekdays 09:00 - 18:00. Saturday 10:00 - 15:00. Sunday closed."
                ),
            },
            # ---- Account ----
            {
                "id": "account-1",
                "category": "account",
                "keywords": [
                    "account", "password", "login", "şifre", "hesap", "giriş", "şifre sıfırlama"
                ],
                "lang": "tr",
                "content": (
                    "Şifre sıfırlama: 'Şifremi Unuttum' linkine tıklayın, e-posta adresinize "
                    "sıfırlama bağlantısı gönderilecektir."
                ),
            },
            {
                "id": "account-2",
                "category": "account",
                "keywords": ["account", "password", "login", "reset"],
                "lang": "en",
                "content": (
                    "Password reset: click 'Forgot Password', a reset link will be sent to your email."
                ),
            },
            # ---- Payment ----
            {
                "id": "payment-1",
                "category": "payment",
                "keywords": [
                    "payment", "credit card", "iDEAL", "odeme", "kredi karti", "fatura"
                ],
                "lang": "tr",
                "content": (
                    "Kabul ettiğimiz ödeme yöntemleri: kredi kartı (Visa/Mastercard), "
                    "iDEAL (Hollanda bankaları), PayPal ve banka havalesi."
                ),
            },
            {
                "id": "payment-2",
                "category": "payment",
                "keywords": ["payment", "credit card", "iDEAL", "invoice"],
                "lang": "en",
                "content": (
                    "We accept: credit card (Visa/Mastercard), iDEAL (Dutch banks), "
                    "PayPal, and bank transfer."
                ),
            },
        ]

    def search(self, query: str, top_k: int = 2) -> list[dict]:
        """
        Case-insensitive keyword search across documents.
        Returns top_k most relevant results.
        """
        query_lower = query.lower()
        scored = []

        for doc in self.documents:
            # Score = how many keywords match
            matches = sum(1 for kw in doc["keywords"] if kw in query_lower)
            if matches > 0:
                scored.append((matches, doc))

        # Sort by match count descending, take top_k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]
