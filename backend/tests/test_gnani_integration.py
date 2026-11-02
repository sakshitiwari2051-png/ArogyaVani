"""End-to-end integration tests for ArogyaVani Gnani AI sovereign stack.

Validates:
1. Full stack imports (GnaniSTT, GnaniTTS, GnaniLLM)
2. STT, TTS, and LLM plugin instantiation and provider identification
3. Pipeline configuration consistency with agent.py
4. Live STT WebSocket handshake with production servers
5. Live TTS WebSocket synthesis with production servers
6. FallbackAdapter resilience with GnaniLLM as primary
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

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

from livekit.agents.llm import FallbackAdapter  # noqa: E402

import gnani_llm  # noqa: E402
import gnani_stt  # noqa: E402
import gnani_tts  # noqa: E402

GNANI_KEY = os.getenv("GNANI_API_KEY", "")
HAS_KEY = bool(GNANI_KEY and "placeholder" not in GNANI_KEY.lower())


def test_full_stack_imports():
    """All Gnani plugins import successfully."""
    assert gnani_stt.GnaniSTT is not None
    assert gnani_tts.GnaniTTS is not None
    assert gnani_llm.GnaniLLM is not None


def test_stt_tts_llm_instantiation():
    """All three plugins instantiate without errors and declare provider 'gnani'."""
    stt_inst = gnani_stt.GnaniSTT(language="hi-IN")
    tts_inst = gnani_tts.GnaniTTS(voice="Nalini")
    llm_inst = gnani_llm.GnaniLLM()

    assert stt_inst.provider == "gnani"
    assert tts_inst.provider == "gnani"
    assert llm_inst.provider == "gnani"


def test_pipeline_config_matches_agent():
    """Plugin configurations match what agent.py expects."""
    stt_inst = gnani_stt.GnaniSTT(language="multi")
    assert stt_inst.capabilities.streaming is True
    assert stt_inst.capabilities.interim_results is True

    tts_inst = gnani_tts.GnaniTTS(voice="Nalini", language="hi-IN", sample_rate=24000)
    assert tts_inst.sample_rate == 24000
    assert tts_inst.num_channels == 1
    assert tts_inst.voice == "Nalini"

    llm_inst = gnani_llm.GnaniLLM(model="evon-v3.3")
    assert llm_inst.model == "evon-v3.3"


@pytest.mark.skipif(
    not HAS_KEY, reason="GNANI_API_KEY not configured or is placeholder"
)
@pytest.mark.asyncio
async def test_live_gnani_stt_websocket_handshake():
    """Live test: Gnani Prisma STT WebSocket connects and returns VAD confirmation."""
    from gnani.stt import GnaniSTTStreamClient, StreamConnectedEvent

    client = GnaniSTTStreamClient(
        api_key=GNANI_KEY,
        language_code="hi-IN",
        sample_rate=16000,
    )
    try:
        conn = await client.connect()
        assert isinstance(conn, StreamConnectedEvent)
        assert conn.sample_rate == 16000
    finally:
        await client.close()


@pytest.mark.skipif(
    not HAS_KEY, reason="GNANI_API_KEY not configured or is placeholder"
)
@pytest.mark.asyncio
async def test_live_gnani_tts_realtime_synthesis():
    """Live test: Gnani Timbre TTS synthesizes Hindi audio stream via WebSocket."""
    from gnani.tts import AudioConfig, GnaniTTSRealtimeClient

    client = GnaniTTSRealtimeClient(api_key=GNANI_KEY)
    cfg = AudioConfig(sample_rate=24000, encoding="linear_pcm", container="raw")

    received_bytes = 0
    async for chunk in client.synthesize(
        "नमस्ते आरोग्यवाणी",
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


def test_fallback_adapter_e2e_resilience():
    """FallbackAdapter correctly prioritizes GnaniLLM and retains fallbacks."""
    primary = gnani_llm.GnaniLLM(model="evon-v3.3", api_key="test_key")
    backup = gnani_llm.GnaniLLM(model="evon-v3.3-fast", api_key="test_key")

    adapter = FallbackAdapter([primary, backup], attempt_timeout=10.0)
    assert adapter._llm_instances[0].provider == "gnani"
    assert adapter._llm_instances[0].model == "evon-v3.3"
