"""Bharat Vernacular Health Lexicon (BVHL) — Indic Clinical Idiom Mapper.

Inspired by KissanAI/Dhenu's 'Bharat Jargons' layer.
Maps rural and colloquial Hindi/Hinglish idioms to structured clinical concepts,
ensuring high STT interpretation accuracy and prompt contextual grounding for
Gnani AI Evon and Prisma models.
"""

from __future__ import annotations

import re
from typing import Any

# Vernacular dictionary mapping colloquial complaints to clinical terms and urgency
VERNACULAR_HEALTH_MAP: dict[str, dict[str, Any]] = {
    "gas ka gola": {
        "clinical_term": "Acute Abdominal Colic / Severe Gastritis",
        "category": "gastrointestinal",
        "red_flag": False,
        "standard_hindi": "पेट में तेज गैस या दर्द",
        "advice_hint": "Jan Aushadhi Antacid (Pantoprazole/Omeprazole) available, visit PHC if severe.",
    },
    "seene mein jalan": {
        "clinical_term": "Gastroesophageal Reflux / Heartburn",
        "category": "gastrointestinal_cardiac",
        "red_flag": False,
        "standard_hindi": "सीने में जलन या एसिडिटी",
        "advice_hint": "Check if pain radiates to left arm or jaw. If crushing pressure, treat as emergency.",
    },
    "chakkar aana": {
        "clinical_term": "Vertigo / Presyncope / Hypotension",
        "category": "neurological_cardiac",
        "red_flag": False,
        "standard_hindi": "चक्कर आना या कमजोरी",
        "advice_hint": "Hydrate with ORS, measure BP at nearest PHC/Arogya Mandir.",
    },
    "sar ghoomna": {
        "clinical_term": "Dizziness / Postural Hypotension",
        "category": "neurological",
        "red_flag": False,
        "standard_hindi": "सिर घूमना",
        "advice_hint": "Lie down, rest in cool area, drink fluids.",
    },
    "jhatke aana": {
        "clinical_term": "Seizure / Convulsions",
        "category": "emergency_neurological",
        "red_flag": True,
        "standard_hindi": "दौरे या झटके आना",
        "advice_hint": "EMERGENCY: Call 108 immediately. Keep airway clear, do not put anything in mouth.",
    },
    "mirgi ka daura": {
        "clinical_term": "Epileptic Seizure",
        "category": "emergency_neurological",
        "red_flag": True,
        "standard_hindi": "मिर्गी का दौरा",
        "advice_hint": "EMERGENCY: Call 108 immediately.",
    },
    "saans phoolna": {
        "clinical_term": "Dyspnea / Acute Respiratory Distress",
        "category": "emergency_respiratory",
        "red_flag": True,
        "standard_hindi": "सांस फूलना या सांस लेने में भारी तकलीफ",
        "advice_hint": "URGENT: Sit upright, loosen tight clothes, proceed to nearest PHC/108.",
    },
    "dam ghutna": {
        "clinical_term": "Severe Asphyxiation / Respiratory Distress",
        "category": "emergency_respiratory",
        "red_flag": True,
        "standard_hindi": "दम घुटना",
        "advice_hint": "EMERGENCY: Immediate oxygen required via 108 or district hospital.",
    },
    "sugar ki goli": {
        "clinical_term": "Oral Hypoglycemic Agents (Metformin / Glimepiride)",
        "category": "chronic_disease",
        "red_flag": False,
        "standard_hindi": "डायबिटीज (शुगर) की दवा",
        "advice_hint": "Jan Aushadhi generic Metformin 500mg available at ~₹15 for 10 tablets (80% discount).",
    },
    "bp ki goli": {
        "clinical_term": "Antihypertensive Agents (Amlodipine / Telmisartan)",
        "category": "chronic_disease",
        "red_flag": False,
        "standard_hindi": "ब्लड प्रेशर (BP) की दवा",
        "advice_hint": "Jan Aushadhi generic Telmisartan/Amlodipine available at ₹10-₹15 at PMBJP kendras.",
    },
    "pait kharab": {
        "clinical_term": "Acute Gastroenteritis / Diarrhea",
        "category": "gastrointestinal",
        "red_flag": False,
        "standard_hindi": "दस्त या लूज मोशन",
        "advice_hint": "Start ORS and Zinc immediately, free at all government PHCs.",
    },
    "khoon ki ulti": {
        "clinical_term": "Hematemesis / Upper GI Bleeding",
        "category": "emergency_gastrointestinal",
        "red_flag": True,
        "standard_hindi": "खून की उल्टी",
        "advice_hint": "EMERGENCY: Call 108 immediately. Do not give oral solids/liquids.",
    },
    "badan tootna": {
        "clinical_term": "Generalized Body Ache / Myalgia with Fever",
        "category": "systemic",
        "red_flag": False,
        "standard_hindi": "पूरे शरीर में तेज दर्द या टूटन",
        "advice_hint": "Check temperature, hydration, generic Paracetamol available at PHC/Jan Aushadhi.",
    },
}


def analyze_vernacular_phrase(text: str) -> list[dict[str, Any]]:
    """Scan input text for regional Hindi/Hinglish medical idioms.

    Returns matched clinical entities with urgency flags.
    """
    clean_text = text.lower().strip()
    matches = []

    for idiom, details in VERNACULAR_HEALTH_MAP.items():
        if re.search(r"\b" + re.escape(idiom) + r"\b", clean_text, re.IGNORECASE):
            matches.append({"matched_idiom": idiom, **details})

    return matches


def enrich_triage_prompt(user_text: str) -> str:
    """Inject contextual clinical awareness into user prompt if vernacular idioms are found."""
    detected = analyze_vernacular_phrase(user_text)
    if not detected:
        return ""

    context_lines = ["\n[Bharat Vernacular Clinical Grounding]:"]
    for item in detected:
        red_flag_str = "CRITICAL RED FLAG" if item["red_flag"] else "Routine / Clinical"
        context_lines.append(
            f"- Caller idiom '{item['matched_idiom']}' translates to: {item['clinical_term']} ({red_flag_str}). Hint: {item['advice_hint']}"
        )

    return "\n".join(context_lines)
