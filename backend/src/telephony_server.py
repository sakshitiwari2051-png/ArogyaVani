"""ArogyaVani Interactive Multilingual Telephony Server.

Powers real two-way conversational voice calls over Twilio:
- Detects caller's spoken language (Hindi, English, Hinglish, regional).
- Routes through Groq (qwen/qwen3.8-27b) ultra-low-latency clinical reasoning.
- Enforces 108 emergency triage latches and PHC referral guidance.
- Streams back TwiML with native Indic voice synthesis (Polly.Aditi for Hindi, Polly.Kajal for English).
"""

import logging
import os
import re

import httpx
from aiohttp import web
from dotenv import load_dotenv

load_dotenv(".env.local")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("telephony")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Emergency Red Flag Keywords
EMERGENCY_RE = re.compile(
    r"\b(chest pain|heart attack|cannot breathe|difficulty breathing|behoshi|chhati me dard|"
    r"saans lene me takleef|khoon|poison|zeher|fits|daura|unconscious|fainted|serious accident)\b",
    re.IGNORECASE,
)

SYSTEM_PROMPT = """You are ArogyaVani, an empathetic, clinical Indic Voice AI Health Helpline doctor for Bharat.
Rules:
1. Speak concisely in 1 to 2 short, crisp sentences suitable for a mobile phone call.
2. STRICT LANGUAGE MATCHING:
   - If user speaks in English (or asks to speak in English) -> Reply in clear, warm Indian English.
   - If user speaks in Hindi or Hinglish (or asks to speak in Hindi) -> Reply in natural, warm Hindi (in Devanagari script).
3. If it is an emergency (chest pain, breathing trouble, severe bleeding, poisoning), immediately tell them to dial 108 for an ambulance.
4. Provide safe, practical first-aid advice and recommend seeing a doctor at their nearest Primary Health Centre (PHC).
5. Never prescribe exact prescription dosages over phone. Keep the tone friendly, reassuring and professional.
"""


def detect_language(text: str) -> str:
    """Detect if caller spoke Hindi, English, or regional language."""
    text_lower = text.lower()

    # Explicit language switch requests
    if re.search(
        r"\b(english|speak in english|in english|talk in english)\b", text_lower
    ):
        return "en"
    if re.search(r"\b(hindi|hindi me|hindi mein|speak in hindi)\b", text_lower):
        return "hi"

    # Devanagari script detection
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"

    # Distinctive Romanized Hindi / Hinglish markers
    hindi_markers = {
        "namaste",
        "namaskar",
        "haan",
        "nahi",
        "bukhar",
        "dard",
        "pet",
        "sar",
        "sir",
        "dawa",
        "dawai",
        "madad",
        "chahiye",
        "kya",
        "kaise",
        "hoga",
        "hai",
        "hain",
        "hoon",
        "kripya",
        "batao",
        "batayein",
        "theek",
        "khoon",
        "saans",
        "ulti",
        "chakkar",
        "mujhe",
        "mera",
        "meri",
        "mere",
        "aap",
        "sahab",
        "ji",
        "bhai",
        "kuch",
        "bolo",
    }

    english_markers = {
        "i",
        "have",
        "the",
        "is",
        "are",
        "am",
        "my",
        "where",
        "what",
        "how",
        "please",
        "can",
        "you",
        "tell",
        "me",
        "persistent",
        "headache",
        "fever",
        "pain",
        "hospital",
        "centre",
        "help",
        "need",
        "symptoms",
        "medicine",
        "tablets",
        "cough",
        "cold",
        "hello",
        "hi",
        "good",
        "morning",
        "evening",
        "doctor",
    }

    words = set(re.findall(r"\b\w+\b", text_lower))
    hi_count = len(words & hindi_markers)
    en_count = len(words & english_markers)

    if hi_count > en_count:
        return "hi"
    if en_count > 0:
        return "en"
    if hi_count > 0:
        return "hi"

    return "en"


async def get_ai_response(user_query: str, lang: str) -> str:
    """Get clinical triage response from Groq ultra-low-latency LLM."""
    if not GROQ_API_KEY:
        if lang == "hi":
            return "नमस्ते, हमें आपकी बात सुनाई दी। कृपया अपने नजदीकी प्राथमिक स्वास्थ्य केंद्र से संपर्क करें।"
        return "Thank you for reaching ArogyaVani. Please consult your nearest health centre for medical assistance."

    # Emergency latch check
    if EMERGENCY_RE.search(user_query):
        if lang == "hi":
            return "यह एक आपातकालीन स्थिति लग रही है! कृपया बिना देरी किए तुरंत 108 एम्बुलेंस पर कॉल करें और नजदीकी आपातकालीन कक्ष में जाएं।"
        return "This sounds like a medical emergency. Please call 108 ambulance immediately or visit your nearest emergency room."

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "qwen/qwen3.8-27b",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"The caller said: '{user_query}'. Target language: {lang}. Give your 1-2 sentence voice reply now in {lang}.",
                        },
                    ],
                    "temperature": 0.3,
                    "max_tokens": 120,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                reply = data["choices"][0]["message"]["content"].strip()
                reply = re.sub(r"\*+", "", reply)
                return reply
            else:
                logger.error("Groq API error: %s %s", resp.status_code, resp.text)
    except Exception as e:
        logger.error("Error querying LLM: %s", e)

    if lang == "hi":
        return "आरोग्यवाणी हेल्पलाइन में आपका स्वागत है। हम आपकी स्वास्थ्य समस्या समझ रहे हैं, कृपया नजदीकी डॉक्टर से परामर्श लें।"
    return "Welcome to ArogyaVani. We understand your concern. Please stay hydrated and consult your local primary health centre."


async def handle_incoming(request: web.Request) -> web.Response:
    """Initial greeting when phone connects."""
    logger.info("Incoming telephony call connected!")
    host = request.headers.get("Host", "localhost:8080")
    proto = request.headers.get("X-Forwarded-Proto", "https")
    base_url = f"{proto}://{host}"
    action_url = f"{base_url}/voice/reply"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="{action_url}" method="POST" language="en-IN" speechTimeout="auto" timeout="10">
        <Say voice="Polly.Kajal" language="en-IN">Hello! Welcome to ArogyaVani sovereign health helpline.</Say>
        <Say voice="Polly.Aditi" language="hi-IN">नमस्ते! मैं आरोग्यवाणी स्वास्थ्य सेवा हूँ।</Say>
        <Say voice="Polly.Kajal" language="en-IN">Please tell me, how are you feeling today? You can speak in English or Hindi.</Say>
    </Gather>
    <Say voice="Polly.Kajal" language="en-IN">I did not hear any voice. Please call back whenever you need medical assistance. Take care!</Say>
</Response>"""
    return web.Response(text=twiml, content_type="application/xml", charset="utf-8")


async def handle_reply(request: web.Request) -> web.Response:
    """Processes caller speech, runs clinical reasoning, switches language dynamically."""
    data = await request.post()
    speech_result = data.get("SpeechResult", "").strip()
    caller = data.get("From", "unknown")
    call_sid = data.get("CallSid", "")

    logger.info("Call %s from %s said: %r", call_sid, caller, speech_result)

    host = request.headers.get("Host", "localhost:8080")
    proto = request.headers.get("X-Forwarded-Proto", "https")
    base_url = f"{proto}://{host}"
    action_url = f"{base_url}/voice/reply"

    if not speech_result:
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="{action_url}" method="POST" language="en-IN" speechTimeout="auto" timeout="5">
        <Say voice="Polly.Kajal" language="en-IN">I could not hear you clearly. Please tell me your symptoms or health question.</Say>
    </Gather>
    <Say voice="Polly.Kajal" language="en-IN">Thank you for calling ArogyaVani. Stay healthy!</Say>
</Response>"""
        return web.Response(text=twiml, content_type="application/xml", charset="utf-8")

    # Detect user language
    lang = detect_language(speech_result)
    logger.info("Detected language: %s for query: %r", lang, speech_result)

    # Get clinical AI response
    reply_text = await get_ai_response(speech_result, lang)
    logger.info("AI Reply (%s): %r", lang, reply_text)

    # Clean reply for XML safety
    clean_reply = (
        reply_text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )

    if lang == "hi":
        voice = "Polly.Aditi"
        voice_lang = "hi-IN"
        gather_lang = "hi-IN"
        followup = "क्या आप कुछ और पूछना चाहते हैं?"
        goodbye = "आरोग्यवाणी स्वास्थ्य सेवा में कॉल करने के लिए धन्यवाद। आपका दिन शुभ हो।"
    else:
        voice = "Polly.Kajal"
        voice_lang = "en-IN"
        gather_lang = "en-IN"
        followup = "Do you have any other questions?"
        goodbye = (
            "Thank you for calling ArogyaVani health helpline. Stay safe and healthy."
        )

    clean_followup = (
        followup.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    clean_goodbye = (
        goodbye.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="{action_url}" method="POST" language="{gather_lang}" speechTimeout="auto" timeout="10">
        <Say voice="{voice}" language="{voice_lang}">{clean_reply} {clean_followup}</Say>
    </Gather>
    <Say voice="{voice}" language="{voice_lang}">{clean_goodbye}</Say>
</Response>"""
    return web.Response(text=twiml, content_type="application/xml", charset="utf-8")


def create_app() -> web.Application:
    app = web.Application()

    async def _health(r):
        return web.json_response({"status": "ok", "agent": "ArogyaVani"})

    app.router.add_get("/health", _health)
    app.router.add_get("/voice/incoming", handle_incoming)
    app.router.add_post("/voice/incoming", handle_incoming)
    app.router.add_post("/voice/reply", handle_reply)
    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("TELEPHONY_PORT", "8080"))
    logger.info("Starting ArogyaVani Interactive Telephony Server on port %d...", port)
    web.run_app(app, host="0.0.0.0", port=port)
