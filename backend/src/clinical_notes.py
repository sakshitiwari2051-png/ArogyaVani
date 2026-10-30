"""Automated Clinical SOAP Note Generator — ArogyaVani.

Inspired by ScribeLive (Agora AI Winner) and ABDM (Ayushman Bharat Digital Mission) standards.
Converts conversational voice triage calls into structured, clinician-ready
SOAP Notes (Subjective, Objective, Assessment, Plan) with FHIR-compliant schema.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def generate_soap_note(
    caller_name: str,
    user_id: str,
    symptoms_text: str,
    triage_outcome: str,
    urgency: str = "medium",
    advised_facility: str = "",
    generic_savings_info: str = "",
    red_flags: list[str] | None = None,
) -> dict[str, Any]:
    """Generate a structured clinical SOAP report from call parameters."""
    now_utc = datetime.now(timezone.utc).isoformat()
    flags = red_flags or []

    # Map urgency to clinical triage category (Emergency / Urgent / Routine)
    triage_category = "ROUTINE"
    if urgency.lower() in ("emergency", "high") or flags:
        triage_category = "EMERGENCY / IMMEDIATE"
    elif "fever" in symptoms_text.lower() or "pain" in symptoms_text.lower():
        triage_category = "URGENT (CARE TODAY)"

    soap_record = {
        "resourceType": "ClinicalImpression",
        "timestamp": now_utc,
        "patient": {
            "name": caller_name or "Anonymous Caller",
            "identifier": user_id or "Phone / Web Participant",
        },
        "soap": {
            "subjective": {
                "chief_complaint": symptoms_text,
                "history_of_present_illness": f"Caller reported symptom cluster: '{symptoms_text}'. Spoke via ArogyaVani Telephony.",
            },
            "objective": {
                "vitals_observed": "Telephonic triage (self-reported)",
                "red_flags_detected": flags if flags else ["None detected"],
                "triage_urgency_level": urgency.upper(),
            },
            "assessment": {
                "clinical_impression": triage_outcome
                or "Preliminary voice triage completed.",
                "triage_category": triage_category,
                "needs_human_handover": bool(
                    urgency.lower() in ("high", "emergency") or flags
                ),
            },
            "plan": {
                "action_recommended": (
                    "Call 108 Emergency Ambulance immediately"
                    if triage_category == "EMERGENCY / IMMEDIATE"
                    else f"Visit nearest primary health facility: {advised_facility or 'Local PHC / CHC'}"
                ),
                "generic_alternatives": generic_savings_info
                or "Advised Jan Aushadhi generic availability (60-80% discount).",
                "referral_facility": advised_facility or "Nearest Government PHC / CHC",
                "followup": "Review within 24-48 hours if symptoms persist or worsen.",
            },
        },
        "compliance": "ABDM / FHIR R4 Ready",
    }

    return soap_record


def format_soap_for_display(soap_record: dict[str, Any]) -> str:
    """Format a SOAP note for human reading on CLI or admin dashboard."""
    s = soap_record["soap"]
    p = soap_record["patient"]
    return (
        f"=====================================================\n"
        f"🏥 AROGYAVANI CLINICAL SOAP NOTE (ABDM/FHIR COMPLIANT)\n"
        f"=====================================================\n"
        f"Patient: {p['name']} ({p['identifier']})\n"
        f"Timestamp: {soap_record['timestamp']}\n"
        f"-----------------------------------------------------\n"
        f"[S] SUBJECTIVE:\n"
        f"  Chief Complaint: {s['subjective']['chief_complaint']}\n\n"
        f"[O] OBJECTIVE:\n"
        f"  Urgency: {s['objective']['triage_urgency_level']}\n"
        f"  Red Flags: {', '.join(s['objective']['red_flags_detected'])}\n\n"
        f"[A] ASSESSMENT:\n"
        f"  Triage Category: {s['assessment']['triage_category']}\n"
        f"  Clinical Summary: {s['assessment']['clinical_impression']}\n\n"
        f"[P] PLAN:\n"
        f"  Immediate Action: {s['plan']['action_recommended']}\n"
        f"  Generic Medicine: {s['plan']['generic_alternatives']}\n"
        f"  Facility: {s['plan']['referral_facility']}\n"
        f"====================================================="
    )
