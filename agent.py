"""
Agent — The core AI agent that processes customer messages.
Uses DeepSeek / OpenAI-compatible API for intelligent responses.
Supports Turkish, English, and Dutch with auto-detection.
"""

import os
import json
import requests
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from knowledge_base import KnowledgeBase
from categorizer import Categorizer
from storage import Storage

load_dotenv()  # local .env (not committed — see .env.example)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"  # DeepSeek-V3


class CustomerSupportAgent:
    """
    AI-powered customer support agent.

    Flow:
      1. Receive customer message
      2. Classify urgency + topic (local categorizer, no API cost)
      3. Search knowledge base for relevant context
      4. Generate response via DeepSeek (knowledge-augmented)
      5. Log everything to persistent storage

    The agent works fully offline (template fallback) when no API key is set.
    """

    def __init__(self):
        self.kb = KnowledgeBase()
        self.categorizer = Categorizer()
        self.storage = Storage()
        self.kb.load_defaults()

    def handle(self, message: str, session_id: Optional[str] = None) -> dict:
        """Process a single customer message end-to-end."""
        if session_id is None:
            session_id = (
                f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            )

        # Step 1: Classify urgency + topic (local, instant)
        classification = self.categorizer.classify(message)

        # Step 2: Search knowledge base for context
        sources = self.kb.search(message, top_k=2)

        # Step 3: Generate reply via DeepSeek (with KB context)
        reply = self._generate_reply(message, classification, sources)

        # Step 4: Persist conversation
        self.storage.save_message(session_id, "customer", message, classification)
        self.storage.save_message(session_id, "agent", reply)

        return {
            "reply": reply,
            "classification": classification,
            "sources": [s["id"] for s in sources],
            "session_id": session_id,
        }

    def _detect_language(self, text: str) -> str:
        """Detect language: tr, nl, or en."""
        turkish_chars = set("çğıöşüĞİÖŞÜÇ")
        dutch_chars = set("ijIJ")  # 'ij' digraph is uniquely Dutch
        text_lower = text.lower()

        if any(c in text_lower for c in turkish_chars):
            return "tr"
        if "ij" in text_lower or text_lower.startswith("ik ") or text_lower.startswith("mijn "):
            return "nl"
        return "en"

    def _build_system_prompt(self, lang: str) -> str:
        """Return a system prompt in the detected language."""
        prompts = {
            "tr": (
                "Sen profesyonel bir e-ticaret müşteri hizmetleri asistanısın.\n"
                "Kurallar:\n"
                "- Kısa, net ve yardımsever ol (2-4 cümle)\n"
                "- Bilgi tabanındaki bilgileri kullan, uydurma bilgi verme\n"
                "- ACİL (urgent) durumlarda özür dile ve insan desteğe yönlendir\n"
                "- Şifre, kart numarası, IBAN gibi özel bilgileri ASLA isteme\n"
                "- Müşteriye her zaman saygılı ve sabırlı ol\n"
                "- Yanıtında kategorizasyon bilgisini gösterme"
            ),
            "nl": (
                "Je bent een professionele klantenservice medewerker voor een e-commerce bedrijf.\n"
                "Regels:\n"
                "- Wees kort, duidelijk en behulpzaam (2-4 zinnen)\n"
                "- Gebruik informatie uit de kennisdatabase, verzin geen dingen\n"
                "- Bij SPOED (urgent) excuses aanbieden en doorverwijzen naar een mens\n"
                "- Vraag NOOIT naar wachtwoorden, creditcardnummers of IBAN\n"
                "- Wees altijd respectvol en geduldig\n"
                "- Toon de categorisatie niet in je antwoord"
            ),
            "en": (
                "You are a professional e-commerce customer support assistant.\n"
                "Rules:\n"
                "- Be concise, clear and helpful (2-4 sentences)\n"
                "- Use knowledge base information when relevant, never make up policies\n"
                "- If URGENT, apologise and offer human escalation\n"
                "- NEVER ask for passwords, credit card numbers, or IBAN\n"
                "- Always be respectful and patient\n"
                "- Do not show the categorisation in your reply"
            ),
        }
        return prompts.get(lang, prompts["en"])

    def _build_kb_context(self, sources: list[dict]) -> str:
        """Format knowledge base results into a compact context block."""
        if not sources:
            return ""
        parts = []
        for s in sources:
            label = f"[{s.get('category', 'general').upper()}] {s['id']}"
            parts.append(f"{label}\n{s['content']}")
        return "Knowledge base:\n" + "\n---\n".join(parts) + "\n\n"

    def _generate_reply(
        self, message: str, classification: dict, sources: list[dict]
    ) -> str:
        """Generate a reply using DeepSeek API, augmented with KB context."""
        lang = self._detect_language(message)
        system_msg = self._build_system_prompt(lang)
        kb_text = self._build_kb_context(sources)

        # Build user message with context
        lang_prefix = {
            "tr": (
                f"**Aciliyet**: {classification['urgency']}\n"
                f"**Konu**: {classification['topic']}\n"
                f"**Müşteri mesajı**: {message}\n\n"
                f"{kb_text}"
                "Kullanıcıya yardımsever bir yanıt yaz:"
            ),
            "nl": (
                f"**Urgentie**: {classification['urgency']}\n"
                f"**Onderwerp**: {classification['topic']}\n"
                f"**Klantbericht**: {message}\n\n"
                f"{kb_text}"
                "Schrijf een behulpzaam antwoord voor de klant:"
            ),
            "en": (
                f"**Urgency**: {classification['urgency']}\n"
                f"**Topic**: {classification['topic']}\n"
                f"**Customer**: {message}\n\n"
                f"{kb_text}"
                "Write a helpful reply to the customer:"
            ),
        }
        user_msg = lang_prefix.get(lang, lang_prefix["en"])

        # Skip API call if no key is configured
        if not DEEPSEEK_API_KEY:
            return self._fallback_reply(message, classification, lang)

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

            print(f"[DeepSeek API error] {resp.status_code}: {resp.text[:200]}")
            return self._fallback_reply(message, classification, lang)

        except Exception as e:
            print(f"[DeepSeek API exception] {e}")
            return self._fallback_reply(message, classification, lang)

    def _fallback_reply(self, message: str, classification: dict, lang: str = "en") -> str:
        """Template-based fallback when the API is unreachable."""
        urgency = classification["urgency"]
        topic = classification["topic"]

        templates = {
            "shipping": {
                "tr": "Siparişinizle ilgili sorunuz için teşekkürler. Kargo takip durumunu kontrol edebilmemiz için sipariş numaranızı paylaşır mısınız?",
                "nl": "Bedankt voor uw vraag over de verzending. Kunt u uw bestelnummer delen zodat we de status kunnen controleren?",
                "en": "Thank you for your shipping inquiry. Could you please share your order number so we can check the status?",
            },
            "returns": {
                "tr": "İade talebiniz için teşekkürler. İade süremiz 14 gündür ve ürünün kullanılmamış olması gerekir. support@example.com adresine e-posta göndererek süreci başlatabilirsiniz.",
                "nl": "Bedankt voor uw retourverzoek. Onze retourtermijn is 14 dagen en het product moet ongebruikt zijn. Stuur een e-mail naar support@example.com om het proces te starten.",
                "en": "Thank you for your return request. Our return window is 14 days and the item must be unused. Email support@example.com to start the process.",
            },
            "payment": {
                "tr": "Ödeme sorunuz için teşekkürler. Kabul ettiğimiz yöntemler: kredi kartı (Visa/Mastercard), iDEAL, PayPal ve banka havalesi.",
                "nl": "Bedankt voor uw betalingsvraag. We accepteren: creditcard (Visa/Mastercard), iDEAL, PayPal en overschrijving.",
                "en": "Thank you for your payment inquiry. We accept: credit card (Visa/Mastercard), iDEAL, PayPal, and bank transfer.",
            },
            "account": {
                "tr": "Hesap işleminiz için teşekkürler. Şifre sıfırlama için giriş sayfasındaki 'Şifremi Unuttum' linkini kullanabilirsiniz.",
                "nl": "Bedankt voor uw accountvraag. Gebruik de 'Wachtwoord vergeten' link op de inlogpagina om uw wachtwoord te resetten.",
                "en": "Thank you for your account inquiry. Use the 'Forgot Password' link on the login page to reset your password.",
            },
            "technical": {
                "tr": "Teknik bir sorun bildirdiniz. Bunu öncelikli olarak teknik ekibimize iletiyoruz. En kısa sürede size dönüş yapılacaktır.",
                "nl": "U heeft een technisch probleem gemeld. We geven dit met prioriteit door aan ons technische team.",
                "en": "You've reported a technical issue. We're prioritising this for our technical team.",
            },
        }

        default_tr = "Mesajınız için teşekkürler. Talebinizi kaydettik, en kısa sürede size dönüş yapacağız."
        default_nl = "Bedankt voor uw bericht. We hebben uw verzoek genoteerd en komen er zo snel mogelijk op terug."
        default_en = "Thank you for your message. We've logged your inquiry and will get back to you shortly."

        defaults = {"tr": default_tr, "nl": default_nl, "en": default_en}

        prefix = "🚨 " if urgency == "urgent" else "⚠️ " if urgency == "high" else ""

        if topic in templates:
            reply = templates[topic].get(lang, templates[topic]["en"])
        else:
            reply = defaults.get(lang, default_en)

        return prefix + reply
