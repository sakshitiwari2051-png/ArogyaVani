"""Tests for Gnani Timbre TTS LiveKit Plugin.

Validates:
1. GnaniTTS initialization and default configurations
2. Custom voice (e.g. Arun) and language configuration
3. Dynamic option updates (language and voice switching mid-session)
4. synthesize() returns an executable GnaniChunkedStream
5. Stream execution and AudioEmitter integration (mocked)
6. Live WebSocket synthesis against Gnani Timbre servers
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

import gnani_tts  # noqa: E402


def test_gnani_tts_initialization():
    """GnaniTTS instantiates with correct defaults."""
    t = gnani_tts.GnaniTTS()
    assert t.model == "timbre-v2.5"
    assert t.provider == "gnani"
    assert t.sample_rate == 24000
    assert t.num_channels == 1
    assert t._voice == "Nalini"
    assert t._language == "hi-IN"


def test_gnani_tts_custom_voice():
    """GnaniTTS accepts custom voice and language."""
    t = gnani_tts.GnaniTTS(voice="Arun", language="en-IN")
    assert t._voice == "Arun"
    assert t._language == "en-IN"


def test_gnani_tts_update_options():
    """update_options correctly changes voice and language mid-session."""
    t = gnani_tts.GnaniTTS()
    t.update_options(locale="en-IN", voice="Arun")
    assert t._language == "en-IN"
    assert t._voice == "Arun"

    t.update_options(locale="hi-IN")
    assert t._language == "hi-IN"


@pytest.mark.asyncio
async def test_gnani_tts_synthesize_returns_stream():
    """synthesize() returns a GnaniChunkedStream."""
    t = gnani_tts.GnaniTTS()
    stream = t.synthesize("नमस्ते")
    assert isinstance(stream, gnani_tts.GnaniChunkedStream)
    await stream.aclose()


@pytest.mark.asyncio
async def test_gnani_chunked_stream_execution_mocked():
    """GnaniChunkedStream._run correctly pushes audio to AudioEmitter."""
    t = gnani_tts.GnaniTTS(api_key="mock_key")
    stream = t.synthesize("परीक्षण संदेश")

    mock_emitter = MagicMock()
    mock_emitter.initialize = MagicMock()
    mock_emitter.push = MagicMock()
    mock_emitter.flush = MagicMock()

    async def fake_synthesize(*args, **kwargs):
        yield b"\x00\x01\x02\x03" * 256
        yield b"\x04\x05\x06\x07" * 256

    mock_client = MagicMock()
    mock_client.synthesize = fake_synthesize

    with patch("gnani.tts.GnaniTTSRealtimeClient", return_value=mock_client):
        await stream._run(mock_emitter)

        mock_emitter.initialize.assert_called_once()
        assert mock_emitter.push.call_count == 2
        mock_emitter.flush.assert_called_once()

    await stream.aclose()


@pytest.mark.asyncio
async def test_gnani_tts_live_realtime_synthesis():
    """Smoke test synthesizing audio through live Gnani Timbre WebSocket API."""
    api_key = os.getenv("GNANI_API_KEY", "")
    if not api_key or "placeholder" in api_key.lower():
        pytest.skip("GNANI_API_KEY not configured or is placeholder")

    from gnani.tts import AudioConfig, GnaniTTSRealtimeClient

    client = GnaniTTSRealtimeClient(api_key=api_key)
    cfg = AudioConfig(sample_rate=24000, encoding="linear_pcm", container="raw")

    received_bytes = 0
    async for chunk in client.synthesize(
        "नमस्ते",
        voice="Nalini",
        model="timbre-v2.5",
        language="hi-IN",
        audio_config=cfg,
    ):
        if chunk:
            received_bytes += len(chunk)

    assert received_bytes > 0, (
        "Expected non-zero audio bytes from live Timbre synthesis"
    )
