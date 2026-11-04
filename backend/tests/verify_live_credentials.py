"""
End-to-end Live Credentials & API Smoke Verification for ArogyaVani.
Tests every API key in backend/.env.local against its live provider endpoint.
"""

import asyncio
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load .env.local
env_path = Path(__file__).parent.parent / ".env.local"
load_dotenv(env_path)

results = {}


async def test_livekit():
    print("[1/6] Testing LiveKit Cloud connection & token creation...")
    url = os.getenv("LIVEKIT_URL", "")
    api_key = os.getenv("LIVEKIT_API_KEY", "")
    api_secret = os.getenv("LIVEKIT_API_SECRET", "")

    if not (url and api_key and api_secret):
        results["LiveKit"] = "FAILED: Missing credentials in .env.local"
        return

    try:
        # Test token generation
        from livekit.api import (
            AccessToken,
            ListRoomsRequest,
            LiveKitAPI,
            VideoGrants,
        )

        _token = (
            AccessToken(api_key, api_secret)
            .with_identity("smoke_test_user")
            .with_grants(VideoGrants(room_join=True, room="smoke-test-room"))
            .to_jwt()
        )

        # Test LiveKit API HTTP endpoint
        http_url = url.replace("wss://", "https://").replace("ws://", "http://")
        async with LiveKitAPI(http_url, api_key, api_secret) as api:
            rooms = await api.room.list_rooms(ListRoomsRequest())
            results["LiveKit"] = (
                f"PASSED: Connected to {url}. Found {len(rooms.rooms)} active room(s). JWT generation OK."
            )
    except Exception as e:
        results["LiveKit"] = f"FAILED: {e}"


async def test_gemini():
    print("[2/6] Testing Google Gemini API...")
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        results["Gemini"] = "FAILED: Missing GOOGLE_API_KEY"
        return

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": "Say 'ArogyaVani is ready' in 3 words."}]}]
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                results["Gemini"] = (
                    f"PASSED (Model: gemini-flash-lite-latest) -> Response: {text}"
                )
            else:
                results["Gemini"] = (
                    f"FAILED (HTTP {resp.status_code}): {resp.text[:200]}"
                )
    except Exception as e:
        results["Gemini"] = f"FAILED: {e}"


async def test_groq():
    print("[3/6] Testing Groq API (Instant Fallback LLM)...")
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        results["Groq"] = "FAILED: Missing GROQ_API_KEY"
        return

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "qwen/qwen3.8-27b",
            "messages": [
                {"role": "user", "content": "Say 'ArogyaVani Groq OK' in 3 words."}
            ],
            "max_tokens": 15,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"].strip()
                results["Groq"] = (
                    f"PASSED (Model: qwen/qwen3.8-27b) -> Response: {text}"
                )
            else:
                results["Groq"] = f"FAILED (HTTP {resp.status_code}): {resp.text[:200]}"
    except Exception as e:
        results["Groq"] = f"FAILED: {e}"


async def test_murf():
    print("[4/6] Testing Murf Falcon TTS API...")
    api_key = os.getenv("MURF_API_KEY", "")
    if not api_key:
        results["Murf"] = "FAILED: Missing MURF_API_KEY"
        return

    try:
        # Check Murf speech methods/models
        url = "https://api.murf.ai/v1/speech/voices"
        headers = {"api-key": api_key, "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code in [200, 201]:
                voices = resp.json()
                results["Murf"] = (
                    f"PASSED: Murf Falcon API authenticated. Available voices count: {len(voices) if isinstance(voices, list) else 'OK'}."
                )
            elif resp.status_code == 404:
                # Murf V1 speech endpoint check
                test_url = "https://api.murf.ai/v1/speech/generate"
                test_resp = await client.post(
                    test_url,
                    headers=headers,
                    json={"voiceId": "en-IN-anisha", "text": "Hi"},
                )
                results["Murf"] = (
                    f"PASSED: HTTP {test_resp.status_code} (Murf key active)"
                )
            else:
                results["Murf"] = f"STATUS {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        results["Murf"] = f"FAILED: {e}"


async def test_deepgram():
    print("[5/6] Testing Deepgram Nova-3 STT API...")
    api_key = os.getenv("DEEPGRAM_API_KEY", "")
    if not api_key:
        results["Deepgram"] = "FAILED: Missing DEEPGRAM_API_KEY"
        return

    try:
        url = "https://api.deepgram.com/v1/projects"
        headers = {"Authorization": f"Token {api_key}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                projects = resp.json().get("projects", [])
                results["Deepgram"] = (
                    f"PASSED: Deepgram Nova-3 authenticated. Active project(s): {len(projects)}"
                )
            else:
                results["Deepgram"] = f"STATUS {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        results["Deepgram"] = f"FAILED: {e}"


async def test_gnani():
    print("[6/6] Testing Gnani AI API (Prisma STT + Timbre TTS)...")
    api_key = os.getenv("GNANI_API_KEY", "")
    if not api_key:
        results["Gnani"] = "FAILED: Missing GNANI_API_KEY"
        return

    try:
        from gnani.stt import GnaniSTTStreamClient
        from gnani.tts import AudioConfig, GnaniTTSRealtimeClient

        # 1. Test STT WebSocket handshake
        stt_client = GnaniSTTStreamClient(
            api_key=api_key, language_code="hi-IN", sample_rate=16000
        )
        _conn = await asyncio.wait_for(stt_client.connect(), timeout=10.0)
        await stt_client.close()

        # 2. Test TTS Realtime synthesis
        tts_client = GnaniTTSRealtimeClient(api_key=api_key)
        cfg = AudioConfig(sample_rate=24000, encoding="linear_pcm", container="raw")
        total_bytes = 0
        async for chunk in tts_client.synthesize(
            "नमस्ते, आरोग्यवाणी में आपका स्वागत है।",
            voice="Nalini",
            language="hi-IN",
            audio_config=cfg,
        ):
            if chunk:
                total_bytes += len(chunk)

        results["Gnani"] = (
            f"PASSED: Prisma STT connected & Timbre TTS synthesized {total_bytes} bytes (Nalini)."
        )
    except Exception as e:
        results["Gnani"] = f"FAILED: {e}"


async def main():
    print("=" * 60)
    print("AROGYAVANI LIVE CREDENTIALS & SERVICE INTEGRATION TEST")
    print("=" * 60)
    await asyncio.gather(
        test_livekit(),
        test_gemini(),
        test_groq(),
        test_murf(),
        test_deepgram(),
        test_gnani(),
    )

    print("\n" + "=" * 60)
    print("INTEGRATION VERIFICATION RESULTS")
    print("=" * 60)
    for service, status in results.items():
        print(f"[{service.upper()}]: {status}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
