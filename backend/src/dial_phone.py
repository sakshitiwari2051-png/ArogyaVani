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

# Sovereign Indic Voice Helpline TwiML URL
TWIML_URL = (
    "https://raw.githubusercontent.com/Niss54/ArogyaVani/main/frontend/public/twiml_arogyavani.xml"
)


def dial(phone: str) -> dict:
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        raise ValueError("Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN in .env.local")

    print(f"[*] Initiating outbound call to {phone} from {TWILIO_PHONE_NUMBER}...")
    with httpx.Client(auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=15.0) as client:
        resp = client.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json",
            data={
                "To": phone,
                "From": TWILIO_PHONE_NUMBER,
                "Url": TWIML_URL,
            },
        )
        if resp.status_code not in (200, 201):
            print(f"[!] Twilio call failed (HTTP {resp.status_code}): {resp.text}")
            return {"status": "error", "response": resp.json()}

        data = resp.json()
        print(f"[+] Call queued successfully! SID: {data.get('sid')}, Status: {data.get('status')}")
        return {"status": "ok", "sid": data.get("sid"), "call": data}


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "+918840301998"
    dial(target)
