"""Automated Clinical SOAP Note Generator — ArogyaVani.

Inspired by ScribeLive (Agora AI Winner) and ABDM (Ayushman Bharat Digital Mission) standards.
Converts conversational voice triage calls into structured, clinician-ready
SOAP Notes with official FHIR R4 ClinicalImpression resource schema.
"""

from __future__ import annotations

import uuid
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
    """Generate a structured clinical SOAP report formatted as an official FHIR R4 ClinicalImpression."""
    now_utc = datetime.now(timezone.utc).isoformat()
    flags = red_flags or []

    # Map urgency to clinical triage category (Emergency / Urgent / Routine)
    triage_category = "ROUTINE"
    if urgency.lower() in ("emergency", "high") or flags:
        triage_category = "EMERGENCY / IMMEDIATE"
    elif "fever" in symptoms_text.lower() or "pain" in symptoms_text.lower():
        triage_category = "URGENT (CARE TODAY)"

    action_recommended = (
        "Call 108 Emergency Ambulance immediately or visit nearest emergency room"
        if triage_category == "EMERGENCY / IMMEDIATE"
        else f"Visit nearest primary health facility: {advised_facility or 'Local Government PHC / CHC'}"
    )
    referral_facility = advised_facility or "Nearest Government PHC / CHC"

    # Official FHIR R4 ClinicalImpression Resource Specification
    soap_record: dict[str, Any] = {
        "resourceType": "ClinicalImpression",
        "id": f"ci-{uuid.uuid4().hex[:12]}",
        "status": "completed",
        "subject": {
            "reference": f"Patient/{user_id or 'anonymous'}",
            "display": caller_name or "Anonymous Caller",
        },
        "patient": {
            "name": caller_name or "Anonymous",
            "id": user_id or "anonymous",
        },
        "effectiveDateTime": now_utc,
        "date": now_utc,
        "description": f"Chief complaint: {symptoms_text or 'Voice triage interaction'}",
        "summary": (
            f"Telephonic preliminary triage completed for {caller_name or 'patient'}. "
            f"Triage category: {triage_category}. Recommended action: {action_recommended}."
        ),
        "investigation": [
            {
                "code": {"text": "Telephonic Triage Findings"},
                "item": [
                    {"display": f"Triage urgency: {triage_category}"},
                    {
                        "display": (
                            f"Red flags: {', '.join(flags) if flags else 'None detected'}"
                        )
                    },
                ],
            }
        ],
        "finding": [
            {
                "itemCodeableConcept": {
                    "text": triage_outcome
                    or "Preliminary voice triage assessment completed."
                }
            }
        ],
        "prognosisCodeableConcept": [{"text": triage_category}],
        "note": [
            {
                "text": (
                    f"Plan: {action_recommended}. Referral: {referral_facility}. "
                    f"Generic medicine guidance: {generic_savings_info or 'Jan Aushadhi (PMBJP) generic equivalent advised.'}"
                )
            }
        ],
        # Structured SOAP Representation for UI & Clinician Dashboard
        "soap": {
            "subjective": {
                "chief_complaint": symptoms_text,
                "history_of_present_illness": f"Caller reported: '{symptoms_text}'. Audio triage via ArogyaVani Telephony.",
            },
            "objective": {
                "vitals_observed": "Telephonic triage (self-reported)",
                "red_flags_detected": flags if flags else ["None detected"],
                "triage_urgency_level": urgency.upper(),
            },
            "assessment": {
                "clinical_impression": triage_outcome
                or "Preliminary non-diagnostic triage completed.",
                "triage_category": triage_category,
                "needs_human_handover": bool(
                    urgency.lower() in ("high", "emergency") or flags
                ),
            },
            "plan": {
                "action_recommended": action_recommended,
                "generic_alternatives": generic_savings_info
                or "Advised Jan Aushadhi generic availability at government PMBJP kendras.",
                "referral_facility": referral_facility,
                "followup": "Review within 24-48 hours if symptoms persist or worsen.",
            },
        },
        "compliance": "ABDM / FHIR R4 Ready",
    }

    return soap_record


def format_soap_for_display(soap_record: dict[str, Any]) -> str:
    """Format a SOAP note for human reading on CLI or clinician dashboard."""
    s = soap_record.get("soap", {})
    subj = s.get("subjective", {})
    obj = s.get("objective", {})
    assess = s.get("assessment", {})
    plan = s.get("plan", {})
    subj_name = soap_record.get("subject", {}).get("display", "Anonymous")

    return (
        f"=====================================================\n"
        f"🏥 AROGYAVANI CLINICAL SOAP NOTE (FHIR R4 / ABDM)\n"
        f"=====================================================\n"
        f"Patient: {subj_name} | ID: {soap_record.get('id', '')}\n"
        f"Timestamp: {soap_record.get('date', '')}\n"
        f"-----------------------------------------------------\n"
        f"[S] SUBJECTIVE:\n"
        f"  Chief Complaint: {subj.get('chief_complaint', '')}\n\n"
        f"[O] OBJECTIVE:\n"
        f"  Urgency: {obj.get('triage_urgency_level', '')}\n"
        f"  Red Flags: {', '.join(obj.get('red_flags_detected', []))}\n\n"
        f"[A] ASSESSMENT:\n"
        f"  Triage Category: {assess.get('triage_category', '')}\n"
        f"  Clinical Summary: {assess.get('clinical_impression', '')}\n\n"
        f"[P] PLAN:\n"
        f"  Immediate Action: {plan.get('action_recommended', '')}\n"
        f"  Generic Medicine: {plan.get('generic_alternatives', '')}\n"
        f"  Facility: {plan.get('referral_facility', '')}\n"
        f"====================================================="
    )
