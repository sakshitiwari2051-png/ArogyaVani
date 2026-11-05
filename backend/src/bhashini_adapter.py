"""Bhashini (Digital India / MeitY) Sovereign Multilingual Adapter for ArogyaVani.

Connects to Government of India's Bhashini ULCA / Dhruva inference pipelines
to support ASR (Speech-to-Text), NMT (Machine Translation via IndicTrans2),
and TTS across 22 scheduled Indian languages (Kannada, Tamil, Telugu,
Marathi, Bengali, Gujarati, Malayalam, Punjabi, Odia, Kashmiri, Nepali,
Assamese, Urdu, Maithili, etc.).

Works as an interoperability and regional dialect expansion bridge alongside
Gnani.ai's primary sovereign voice AI stack.
"""

from __future__ import annotations

import base64
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger("bhashini_adapter")

BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID", "")
BHASHINI_UDYAT_KEY = os.getenv("BHASHINI_UDYAT_KEY", "")
BHASHINI_INFERENCE_KEY = os.getenv("BHASHINI_INFERENCE_KEY", "")
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY", BHASHINI_UDYAT_KEY)
BHASHINI_PIPELINE_ID = os.getenv("BHASHINI_PIPELINE_ID", "")
BHASHINI_AUTH_URL = os.getenv(
    "BHASHINI_AUTH_URL",
    "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline",
)
BHASHINI_INFERENCE_URL = os.getenv(
    "BHASHINI_INFERENCE_URL",
    "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
)

# Supported 22 Scheduled Indian Languages Mapping
BHASHINI_LANGUAGES: dict[str, str] = {
    "hi": "Hindi",
    "en": "English",
    "kn": "Kannada",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "ks": "Kashmiri",
    "ne": "Nepali",
    "as": "Assamese",
    "ur": "Urdu",
    "mai": "Maithili",
    "sa": "Sanskrit",
    "sd": "Sindhi",
    "kok": "Konkani",
    "doi": "Dogri",
    "mni": "Manipuri",
    "sat": "Santali",
    "brx": "Bodo",
}


class BhashiniClient:
    """Client for Bhashini Digital India ULCA Multilingual Voice Pipelines."""

    def __init__(
        self,
        user_id: str | None = None,
        api_key: str | None = None,
        inference_key: str | None = None,
        pipeline_id: str = "",
        inference_url: str = "",
    ) -> None:
        self.user_id = user_id if user_id is not None else BHASHINI_USER_ID
        self.api_key = (
            api_key if api_key is not None else (BHASHINI_UDYAT_KEY or BHASHINI_API_KEY)
        )
        self.inference_key = (
            inference_key if inference_key is not None else BHASHINI_INFERENCE_KEY
        )
        self.pipeline_id = pipeline_id or BHASHINI_PIPELINE_ID
        self.inference_url = inference_url or BHASHINI_INFERENCE_URL

        self.is_configured = bool(
            (self.api_key or self.inference_key)
            and self.api_key != "your_bhashini_api_key_here"
        )
        self._callback_url: str = self.inference_url
        self._auth_token: str = self.inference_key or self.api_key

    async def initialize_pipeline(
        self,
        source_lang: str = "kn",
        target_lang: str = "hi",
        tasks: list[str] | None = None,
    ) -> bool:
        """Fetch active service providers and callback endpoints from ULCA auth."""
        if not self.is_configured:
            logger.info(
                "Bhashini API not configured; running in simulation fallback mode."
            )
            return False

        tasks = tasks or ["asr", "translation", "tts"]
        pipeline_tasks = []
        for t in tasks:
            cfg: dict[str, Any] = {"language": {"sourceLanguage": source_lang}}
            if t == "translation":
                cfg["language"]["targetLanguage"] = target_lang
            pipeline_tasks.append({"taskType": t, "config": cfg})

        payload = {
            "pipelineTasks": pipeline_tasks,
            "pipelineRequestConfig": {
                "pipelineId": self.pipeline_id or "64392f96daac500b55c543cd"
            },
        }

        headers = {
            "userID": self.user_id,
            "ulcaApiKey": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    BHASHINI_AUTH_URL, headers=headers, json=payload
                )
                if res.status_code == 200:
                    data = res.json()
                    callback_cfg = data.get("pipelineInferenceAPIEndPoint", {})
                    self._callback_url = callback_cfg.get(
                        "callbackUrl", self.inference_url
                    )
                    inf_key = callback_cfg.get("inferenceApiKey", {})
                    self._auth_token = inf_key.get("value", self.inference_key)
                    logger.info(
                        "Bhashini pipeline initialized successfully for %s -> %s",
                        source_lang,
                        target_lang,
                    )
                    return True
                else:
                    logger.info(
                        "Bhashini auth pipeline returned HTTP %d, falling back to Dhruva inference gateway",
                        res.status_code,
                    )
                    return False
        except Exception as e:
            logger.info("Bhashini auth pipeline fallback: %s", e)
            return False

    async def translate_text(
        self,
        text: str,
        source_lang: str = "kn",
        target_lang: str = "hi",
    ) -> str:
        """Translate text across Indian languages using IndicTrans2 NMT."""
        if not text.strip():
            return ""

        if source_lang == target_lang:
            return text

        if not self.is_configured:
            logger.debug(
                "Bhashini unconfigured; returning original text for %s -> %s",
                source_lang,
                target_lang,
            )
            return text

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            "targetLanguage": target_lang,
                        },
                        "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4",
                    },
                }
            ],
            "inputData": {"input": [{"source": text}]},
        }

        headers = {
            "Authorization": self._auth_token,
            "Content-Type": "application/json",
        }
        if self.user_id:
            headers["userID"] = self.user_id

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(
                    self._callback_url, headers=headers, json=payload
                )
                if res.status_code == 200:
                    data = res.json()
                    outputs = data.get("pipelineResponse", [{}])[0].get("output", [])
                    if outputs and "target" in outputs[0]:
                        return str(outputs[0]["target"])
        except Exception as e:
            logger.debug("Bhashini NMT translation fallback: %s", e)

        return text

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        source_lang: str = "kn",
    ) -> str:
        """Transcribe vernacular audio using Bhashini ASR."""
        if not audio_bytes:
            return ""

        if not self.is_configured:
            logger.debug("Bhashini unconfigured; skipping ASR.")
            return ""

        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {"sourceLanguage": source_lang},
                        "audioFormat": "wav",
                    },
                }
            ],
            "inputData": {"audio": [{"audioContent": b64_audio}]},
        }

        headers = {
            "Authorization": self._auth_token,
            "Content-Type": "application/json",
        }
        if self.user_id:
            headers["userID"] = self.user_id

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    self._callback_url, headers=headers, json=payload
                )
                if res.status_code == 200:
                    data = res.json()
                    outputs = data.get("pipelineResponse", [{}])[0].get("output", [])
                    if outputs and "source" in outputs[0]:
                        return str(outputs[0]["source"])
        except Exception as e:
            logger.debug("Bhashini ASR fallback: %s", e)

        return ""

    async def synthesize_speech(
        self,
        text: str,
        target_lang: str = "kn",
        gender: str = "female",
    ) -> bytes | None:
        """Synthesize vernacular audio using Bhashini TTS."""
        if not text.strip() or not self.is_configured:
            return None

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": {
                        "language": {"sourceLanguage": target_lang},
                        "gender": gender,
                    },
                }
            ],
            "inputData": {"input": [{"source": text}]},
        }

        headers = {
            "Authorization": self._auth_token,
            "Content-Type": "application/json",
        }
        if self.user_id:
            headers["userID"] = self.user_id

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    self._callback_url, headers=headers, json=payload
                )
                if res.status_code == 200:
                    data = res.json()
                    outputs = data.get("pipelineResponse", [{}])[0].get("audio", [])
                    if outputs and "audioContent" in outputs[0]:
                        return base64.b64decode(outputs[0]["audioContent"])
        except Exception as e:
            logger.debug("Bhashini TTS fallback: %s", e)

        return None
