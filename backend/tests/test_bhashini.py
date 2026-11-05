import pytest

from bhashini_adapter import BHASHINI_LANGUAGES, BhashiniClient


def test_bhashini_language_catalog():
    assert len(BHASHINI_LANGUAGES) >= 22
    assert "kn" in BHASHINI_LANGUAGES
    assert "ta" in BHASHINI_LANGUAGES
    assert "te" in BHASHINI_LANGUAGES
    assert "ks" in BHASHINI_LANGUAGES
    assert "ne" in BHASHINI_LANGUAGES
    assert "mai" in BHASHINI_LANGUAGES


@pytest.mark.asyncio
async def test_bhashini_unconfigured_fallback():
    client = BhashiniClient(api_key="", inference_key="")
    assert not client.is_configured

    # Unconfigured translate should gracefully return original text without crashing
    text = "ನಮಸ್ಕಾರ, ನನಗೆ ಜ್ವರವಿದೆ"
    res = await client.translate_text(text, source_lang="kn", target_lang="hi")
    assert res == text

    # Same source and target should return immediately
    res_same = await client.translate_text("Hello", source_lang="en", target_lang="en")
    assert res_same == "Hello"


@pytest.mark.asyncio
async def test_bhashini_asr_tts_safeguards():
    client = BhashiniClient(api_key="", inference_key="")
    assert await client.transcribe_audio(b"") == ""
    assert await client.synthesize_speech("") is None
