"""
Agent — The core AI agent that processes customer messages.
Uses DeepSeek API (OpenAI-compatible) for intelligent responses.
"""

import os
import json
import requests
from datetime import datetime, timezone
from typing import Literal

from dotenv import load_dotenv
from knowledge_base import KnowledgeBase
from categorizer import Categorizer
from storage import Storage

load_dotenv()  # local .env
load_dotenv(r"C:\Users\rami1\AppData\Local\hermes\profiles\rsgt-03\.env")  # rsgt profile

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


class CustomerSupportAgent:
    """
    AI-powered customer support agent.

    Flow:
      1. Receive customer message
      2. Classify urgency + topic (local categorizer, no API)
      3. Search knowledge base for context
      4. Generate response via DeepSeek (knowledge-augmented)
      5. Log everything
    """

    def __init__(self):
        self.kb = KnowledgeBase()
        self.categorizer = Categorizer()
        self.storage = Storage()
        self.kb.load_defaults()

    def handle(self, message: str, session_id: str | None = None) -> dict:
        if session_id is None:
            session_id = (
                f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            )

        # Step 1: Classify (local — hizli, API'siz)
        classification = self.categorizer.classify(message)

        # Step 2: Search knowledge base
        sources = self.kb.search(message, top_k=2)

        # Step 3: Generate reply via DeepSeek
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
        """Generate a reply using DeepSeek API, with KB context."""

        # Detect language
        turkish_chars = set("çğıöşüĞİÖŞÜÇ")
        lang = "tr" if any(c in message for c in turkish_chars) else "en"

        system_msg = (
            "Sen bir e-ticaret müşteri hizmetleri asistanısın. "
            "Kurallar:\n"
            "- Kısa ve yardımsever ol (2-4 cümle)\n"
            "- Bilgi tabanındaki bilgileri kullan\n"
            "- ACİL durumlarda özür dile ve insan desteğe yönlendir\n"
            "- Şifre, kart numarası gibi özel bilgileri ASLA isteme\n"
            "- Uydurma bilgi verme, bilmiyorsan insan desteğe aktar"
            if lang == "tr"
            else (
                "You are an e-commerce customer support assistant. "
                "Rules:\n"
                "- Be concise and helpful (2-4 sentences)\n"
                "- Use the knowledge base info when relevant\n"
                "- If URGENT, apologise and offer human escalation\n"
                "- NEVER ask for passwords or credit card info\n"
                "- Do not make up policies"
            )
        )

        # Build context from KB
        kb_text = ""
        if sources:
            kb_text = "Bilgi tabanı:\n" + "\n---\n".join(
                s["content"] for s in sources
            ) + "\n\n"

        user_msg = (
            f"**Aciliyet**: {classification['urgency']}\n"
            f"**Konu**: {classification['topic']}\n"
            f"**Müşteri mesajı**: {message}\n\n"
            f"{kb_text}"
            f"Yardımsever bir yanıt yaz:"
            if lang == "tr"
            else (
                f"**Urgency**: {classification['urgency']}\n"
                f"**Topic**: {classification['topic']}\n"
                f"**Customer**: {message}\n\n"
                f"{kb_text}"
                f"Write a helpful reply:"
            )
        )

        # Skip API if no key
        if not DEEPSEEK_API_KEY:
            return self._fallback_reply(message, classification)

        try:
            resp = requests.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
                timeout=20,
            )

            if resp.ok:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                print(f"[DeepSeek API error] {resp.status_code}: {resp.text[:200]}")
                return self._fallback_reply(message, classification)

        except Exception as e:
            print(f"[DeepSeek API exception] {e}")
            return self._fallback_reply(message, classification)

    def _fallback_reply(self, message: str, classification: dict) -> str:
        """Template fallback when API is unavailable."""
        urgency = classification["urgency"]
        topic = classification["topic"]

        templates_tr = {
            "shipping": "Siparişinizle ilgili sorunuz için teşekkürler. Kargo takip numaranız varsa bizimle paylaşabilirsiniz, ekibimiz en kısa sürede size dönecektir.",
            "returns": "İade talebiniz için teşekkürler. İade sürecimiz 14 gün içinde ve ürünün orijinal kutusunda olması gerekiyor. Detaylı bilgi için destek ekibimiz sizinle iletişime geçecek.",
            "payment": "Ödeme ile ilgili sorunuzu aldık. Ekibimiz en kısa sürede size yardımcı olacak.",
            "account": "Hesap işlemlerinizle ilgili talebinizi aldık. Şifre sıfırlama ve diğer hesap işlemleri için size yardımcı olacağız.",
            "technical": "Teknik bir sorun bildirdiniz. Bunu öncelikli olarak ekibimize iletiyoruz.",
        }

        templates_en = {
            "shipping": "Thank you for your shipping inquiry. Please share your tracking number if available, and our team will get back to you shortly.",
            "returns": "Thanks for your return request. Our return window is 14 days. Our support team will contact you with details.",
            "payment": "We received your payment inquiry. Our team will assist you shortly.",
            "account": "We received your account inquiry. We'll help you with password reset and other account matters.",
            "technical": "You've reported a technical issue. We're prioritizing this for our team.",
        }

        templates = templates_tr if any(c in message for c in "çğıöşüĞİÖŞÜÇ") else templates_en

        prefix = "🚨 " if urgency == "urgent" else "⚠️ " if urgency == "high" else ""

        if topic in templates:
            return prefix + templates[topic]
        else:
            return (
                prefix
                + (
                    "Mesajınız için teşekkürler. Talebinizi kaydettik, en kısa sürede size dönüş yapacağız."
                    if "ç" in message or "ğ" in message or "ı" in message or "ö" in message or "ş" in message or "ü" in message
                    else "Thank you for your message. We've logged your inquiry and will get back to you shortly."
                )
            )
