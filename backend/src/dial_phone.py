"""ArogyaVani Outbound Telephony Dispatcher.

Usage:
    uv run python src/dial_phone.py +918840301998
"""

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv(".env.local")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+17372508034")

# Default interactive TwiML response in Hindi and English
DEFAULT_TWIML = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="hi-IN">नमस्ते! मैं आरोग्यवाणी स्वास्थ्य सेवा हूँ।</Say>
    <Say voice="Polly.Kajal" language="en-IN">Welcome to ArogyaVani sovereign voice health helpline.</Say>
    <Pause length="1"/>
    <Say voice="Polly.Aditi" language="hi-IN">यदि आपको कोई आपातकालीन समस्या है, जैसे सीने में तेज दर्द, सांस लेने में तकलीफ, या बेहोशी, तो कृपया बिना देरी किए तुरंत 108 एम्बुलेंस पर कॉल करें। सामान्य परामर्श और निशुल्क दवाओं के लिए अपने नजदीकी प्राथमिक स्वास्थ्य केंद्र या जन औषधि केंद्र जाएं।</Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="en-IN">For acute emergencies, dial 108 immediately. Thank you for connecting with ArogyaVani. Stay safe and healthy!</Say>
</Response>"""


def dial(phone: str, voice_url: str = "") -> dict:
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        raise ValueError(
            "Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN in .env.local"
        )

    print(
        f"[*] Initiating interactive voice call to {phone} from {TWILIO_PHONE_NUMBER}..."
    )

    data = {
        "To": phone,
        "From": TWILIO_PHONE_NUMBER,
    }

    if voice_url:
        print(f"[*] Using voice webhook URL: {voice_url}")
        data["Url"] = voice_url
    else:
        print("[*] Using sovereign bilingual TwiML (Hindi/English 108 emergency triage)...")
        data["Twiml"] = DEFAULT_TWIML

    with httpx.Client(
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=15.0
    ) as client:
        resp = client.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json",
            data=data,
        )
        if resp.status_code not in (200, 201):
            print(f"[!] Twilio call failed (HTTP {resp.status_code}): {resp.text}")
            return {"status": "error", "response": resp.json()}

        data = resp.json()
        print(
            f"[+] Call queued successfully! SID: {data.get('sid')}, Status: {data.get('status')}"
        )
        return {"status": "ok", "sid": data.get("sid"), "call": data}


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "+918840301998"
    custom_url = sys.argv[2] if len(sys.argv) > 2 else ""
    dial(target, custom_url)
