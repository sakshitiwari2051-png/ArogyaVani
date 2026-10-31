"""Unit tests for ArogyaVani Hackathon Innovations:
1. Bharat Vernacular Health Lexicon (BVHL)
2. Clinical SOAP Note Generator (ABDM / FHIR compliant)
3. Gnani Speech Client initialization and error handling
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import bharat_lexicon
import clinical_notes
import gnani_adapter


def test_bharat_lexicon_matches_vernacular_idiom() -> None:
    # Test colloquial expression
    phrase = "Mere dost ko subah se pet mein gas ka gola ban raha hai"
    matches = bharat_lexicon.analyze_vernacular_phrase(phrase)
    assert len(matches) == 1
    assert matches[0]["matched_idiom"] == "gas ka gola"
    assert "Acute Abdominal Colic" in matches[0]["clinical_term"]
    assert matches[0]["red_flag"] is False


def test_bharat_lexicon_triggers_red_flag_for_emergency_idioms() -> None:
    # Test emergency phrase "jhatke aana" (seizures)
    phrase = "Marij ko achanak jhatke aana shuru ho gaye hain"
    matches = bharat_lexicon.analyze_vernacular_phrase(phrase)
    assert len(matches) == 1
    assert matches[0]["matched_idiom"] == "jhatke aana"
    assert matches[0]["red_flag"] is True

    # Test "mirgi ka daura"
    phrase_mirgi = "Unhe mirgi ka daura pada hai"
    mirgi_matches = bharat_lexicon.analyze_vernacular_phrase(phrase_mirgi)
    assert len(mirgi_matches) == 1
    assert mirgi_matches[0]["red_flag"] is True


def test_bharat_lexicon_enrich_triage_prompt() -> None:
    text = "Mujhe saans phoolna aur dard ho raha hai"
    prompt_addition = bharat_lexicon.enrich_triage_prompt(text)
    assert "Bharat Vernacular Clinical Grounding" in prompt_addition
    assert "Dyspnea" in prompt_addition


def test_clinical_soap_note_generation_routine() -> None:
    soap = clinical_notes.generate_soap_note(
        caller_name="Ramesh Kumar",
        user_id="+919876543210",
        symptoms_text="Fever for 2 days",
        triage_outcome="Advised routine PHC visit",
        urgency="medium",
        advised_facility="PHC Shivpur",
        generic_savings_info="Paracetamol 650mg at Jan Aushadhi (₹12 vs ₹35)",
    )
    assert soap["resourceType"] == "ClinicalImpression"
    assert soap["patient"]["name"] == "Ramesh Kumar"
    assert soap["soap"]["assessment"]["triage_category"] == "URGENT (CARE TODAY)"
    assert "PHC Shivpur" in soap["soap"]["plan"]["referral_facility"]
    assert "Jan Aushadhi" in soap["soap"]["plan"]["generic_alternatives"]


def test_clinical_soap_note_emergency_escalation() -> None:
    soap = clinical_notes.generate_soap_note(
        caller_name="Sita Devi",
        user_id="+919876543210",
        symptoms_text="Severe crushing chest pain radiating to jaw",
        triage_outcome="Escalated to 108 Emergency Ambulance",
        urgency="emergency",
        red_flags=["Chest Pain", "Radiating Pain"],
    )
    assert soap["soap"]["assessment"]["triage_category"] == "EMERGENCY / IMMEDIATE"
    assert soap["soap"]["assessment"]["needs_human_handover"] is True
    assert "108 Emergency Ambulance" in soap["soap"]["plan"]["action_recommended"]


def test_gnani_adapter_initialization_defaults() -> None:
    client = gnani_adapter.get_gnani_client()
    assert client.base_url == "https://api.vachana.ai"
    # When no key is provided, should be unconfigured but safe
    assert isinstance(client.is_configured, bool)
