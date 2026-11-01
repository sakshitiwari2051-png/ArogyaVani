"""Tests for Gnani Prisma STT LiveKit Plugin.

Validates:
1. GnaniSTT initialization and default/custom configurations
2. Language normalization and mapping for Indic languages
3. GnaniSpeechStream stream creation and properties
4. Batch STT fallback execution
5. Live WebSocket connection test if GNANI_API_KEY is configured
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv

# Ensure backend/src is on python path
src_dir = str(Path(__file__).parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Load .env.local for live credentials if present
env_local = Path(__file__).parent.parent / ".env.local"
if env_local.exists():
    load_dotenv(env_local)

from livekit.agents.stt import SpeechEventType  # noqa: E402

import gnani_stt  # noqa: E402


def test_gnani_stt_initialization():
    """GnaniSTT instantiates with valid defaults and capabilities."""
    stt_instance = gnani_stt.GnaniSTT()
    assert stt_instance.model == "prisma-v2.5"
    assert stt_instance.provider == "gnani"
    assert stt_instance.language == "hi-IN"
    assert stt_instance.capabilities.streaming is True
    assert stt_instance.capabilities.interim_results is True


def test_gnani_stt_custom_config():
    """GnaniSTT accepts custom model, language, and sample rate."""
    stt_instance = gnani_stt.GnaniSTT(
        model="prisma-v3.0",
        language="ta-IN",
        sample_rate=8000,
        api_key="test_custom_key",
    )
    assert stt_instance.model == "prisma-v3.0"
    assert stt_instance.language == "ta-IN"
    assert stt_instance._sample_rate == 8000
    assert stt_instance._api_key == "test_custom_key"


def test_gnani_stt_language_normalization():
    """Language codes and aliases are normalized to BCP-47 standard."""
    assert gnani_stt.normalize_language_code("hindi") == "hi-IN"
    assert gnani_stt.normalize_language_code("HINDI") == "hi-IN"
    assert gnani_stt.normalize_language_code("english") == "en-IN"
    assert gnani_stt.normalize_language_code("ta") == "ta-IN"
    assert gnani_stt.normalize_language_code("tamil") == "ta-IN"
    assert gnani_stt.normalize_language_code("multi") == "hi-IN"
    assert gnani_stt.normalize_language_code("indic-auto") == "hi-IN"
    assert gnani_stt.normalize_language_code("te-IN") == "te-IN"


@pytest.mark.asyncio
async def test_gnani_stt_stream_creation():
    """stream() returns a configured GnaniSpeechStream instance."""
    stt_instance = gnani_stt.GnaniSTT()
    stream = stt_instance.stream(language="kn-IN")
    assert isinstance(stream, gnani_stt.GnaniSpeechStream)
    assert stream._language == "kn-IN"
    assert stream._sample_rate == 16000
    await stream.aclose()


@pytest.mark.asyncio
async def test_gnani_recognize_mocked():
    """Batch recognition translates audio buffer to final SpeechEvent."""
    stt_instance = gnani_stt.GnaniSTT(api_key="mock_key")

    mock_client = MagicMock()
    mock_client.transcribe.return_value = {
        "transcript": "मुझे सिरदर्द और बुखार है",
        "language_code": "hi-IN",
        "status": "success",
    }

    mock_buffer = MagicMock()
    mock_combined = MagicMock()
    mock_combined.to_wav_bytes.return_value = b"RIFFmockwavbytes"

    with (
        patch("livekit.rtc.combine_audio_frames", return_value=mock_combined),
        patch("gnani.stt.GnaniSTTClient", return_value=mock_client),
    ):
        event = await stt_instance._recognize_impl(mock_buffer, language="hi-IN")

        assert event.type == SpeechEventType.FINAL_TRANSCRIPT
        assert len(event.alternatives) == 1
        assert event.alternatives[0].text == "मुझे सिरदर्द और बुखार है"
        assert event.alternatives[0].language == "hi-IN"


@pytest.mark.asyncio
async def test_gnani_live_websocket_connection():
    """Smoke test connecting to Gnani STT live service with actual API key."""
    api_key = os.getenv("GNANI_API_KEY", "")
    if not api_key or "placeholder" in api_key.lower():
        pytest.skip("GNANI_API_KEY not configured or is placeholder")

    from gnani.stt import GnaniSTTStreamClient, StreamConnectedEvent

    client = GnaniSTTStreamClient(
        api_key=api_key,
        language_code="hi-IN",
        sample_rate=16000,
    )

    try:
        conn = await client.connect()
        assert isinstance(conn, StreamConnectedEvent)
        assert conn.sample_rate == 16000
    finally:
        await client.close()
