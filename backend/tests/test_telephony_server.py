import pytest
from aiohttp import web

from telephony_server import create_app, detect_language


def test_detect_language_hindi():
    assert detect_language("नमस्ते डॉक्टर साहब, मुझे बहुत बुखार है") == "hi"
    assert detect_language("mujhe bukhar aur pet dard hai") == "hi"
    assert detect_language("Doctor sahab dawa batao") == "hi"


def test_detect_language_english():
    assert detect_language("Hello doctor, I have a persistent headache") == "en"
    assert detect_language("Where is the nearest primary health centre?") == "en"
    assert detect_language("What are the symptoms of dengue fever?") == "en"


@pytest.mark.asyncio
async def test_incoming_route():
    app = create_app()
    client = web.AppRunner(app)
    await client.setup()
    site = web.TCPSite(client, "127.0.0.1", 8089)
    await site.start()

    import httpx

    async with httpx.AsyncClient() as http:
        resp = await http.get("http://127.0.0.1:8089/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

        voice_resp = await http.get("http://127.0.0.1:8089/voice/incoming")
        assert voice_resp.status_code == 200
        assert "application/xml" in voice_resp.headers["content-type"]
        assert "ArogyaVani" in voice_resp.text

    await client.cleanup()
