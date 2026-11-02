"""Tests for Gnani Evon LLM LiveKit Plugin.

Validates:
1. GnaniLLM initialization and default model/provider configurations
2. create_gnani_llm factory function
3. Custom parameter configuration (temperature, custom models)
4. Compatibility with LiveKit's FallbackAdapter
"""

from __future__ import annotations

import sys
from pathlib import Path

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


def test_gnani_llm_initialization():
    """GnaniLLM instantiates with correct defaults."""
    llm_inst = gnani_llm.GnaniLLM()
    assert "evon" in llm_inst._model or "evon" in llm_inst.model
    assert llm_inst.provider == "gnani"
    assert llm_inst.model == "evon-v3.3"


def test_gnani_llm_factory():
    """Factory function creates configured GnaniLLM instance."""
    llm_inst = gnani_llm.create_gnani_llm(temperature=0.3)
    assert isinstance(llm_inst, gnani_llm.GnaniLLM)
    assert llm_inst._opts.temperature == 0.3


def test_gnani_llm_custom_config():
    """GnaniLLM accepts custom model and API key."""
    llm_inst = gnani_llm.GnaniLLM(
        model="evon-v3.3-indic",
        api_key="test_custom_key",
        temperature=0.1,
    )
    assert llm_inst.model == "evon-v3.3-indic"
    assert llm_inst._model == "evon-v3.3-indic"
    assert llm_inst._opts.temperature == 0.1


def test_gnani_llm_fallback_adapter_compatibility():
    """GnaniLLM is fully compatible as primary in LiveKit FallbackAdapter."""
    primary_llm = gnani_llm.GnaniLLM(api_key="mock_key")
    fallback_llm = gnani_llm.GnaniLLM(model="evon-v3.3-fast", api_key="mock_key")

    adapter = FallbackAdapter([primary_llm, fallback_llm])
    assert adapter is not None
    assert len(adapter._llm_instances) == 2
