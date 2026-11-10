"""Seed script to populate ArogyaVani Call Analytics with realistic Bharat healthcare consultation records."""

import json
import os
import sqlite3
import urllib.request
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone.utc)

SAMPLE_CALLS = [
    {
        "room_name": "voice_room_varanasi_101",
        "channel": "browser",
        "offset_mins": 15,
        "duration_secs": 168,
        "outcome": "success",
        "outcome_reason": "Triage completed (Hindi - Acute high-grade fever & cough, Shivpur PHC assigned)",
        "escalation_created": 0,
        "user_turns": 6,
        "agent_turns": 7,
    },
    {
        "room_name": "sip_outbound_918840301998",
        "channel": "sip",
        "offset_mins": 35,
        "duration_secs": 94,
        "outcome": "success",
        "outcome_reason": "Deterministic 108 Emergency bypass triggered (Retrosternal chest pain & breathlessness)",
        "escalation_created": 1,
        "user_turns": 3,
        "agent_turns": 3,
    },
    {
        "room_name": "voice_room_lucknow_103",
        "channel": "browser",
        "offset_mins": 65,
        "duration_secs": 142,
        "outcome": "success",
        "outcome_reason": "PMBJP Jan Aushadhi generic salt substitution (Augmentin 625 -> Amox-Clav salt)",
        "escalation_created": 0,
        "user_turns": 5,
        "agent_turns": 6,
    },
    {
        "room_name": "sip_inbound_kanpur_104",
        "channel": "sip",
        "offset_mins": 110,
        "duration_secs": 215,
        "outcome": "success",
        "outcome_reason": "Ayushman Bharat PMJAY golden card eligibility verified for rural BPL family",
        "escalation_created": 0,
        "user_turns": 7,
        "agent_turns": 8,
    },
    {
        "room_name": "voice_room_gorakhpur_105",
        "channel": "browser",
        "offset_mins": 140,
        "duration_secs": 185,
        "outcome": "success",
        "outcome_reason": "Maternal & Child Health: Mission Indradhanush vaccination schedule for 9mo infant",
        "escalation_created": 0,
        "user_turns": 4,
        "agent_turns": 5,
    },
    {
        "room_name": "sip_outbound_reminder_106",
        "channel": "sip",
        "offset_mins": 190,
        "duration_secs": 120,
        "outcome": "success",
        "outcome_reason": "Outbound Telephony Reminder: Hypertension amlodipine daily dosage & low-sodium diet",
        "escalation_created": 0,
        "user_turns": 4,
        "agent_turns": 4,
    },
    {
        "room_name": "voice_room_prayagraj_107",
        "channel": "browser",
        "offset_mins": 230,
        "duration_secs": 240,
        "outcome": "success",
        "outcome_reason": "Human Specialist Handoff: Chronic knee osteoarthritis escalated to General Medicine MD",
        "escalation_created": 1,
        "user_turns": 8,
        "agent_turns": 9,
    },
    {
        "room_name": "sip_inbound_rural_108",
        "channel": "sip",
        "offset_mins": 280,
        "duration_secs": 160,
        "outcome": "success",
        "outcome_reason": "Rural 2G Feature Phone: Acute gastroenteritis & ORS hydration advice in Bhojpuri/Hindi",
        "escalation_created": 0,
        "user_turns": 5,
        "agent_turns": 6,
    },
    {
        "room_name": "sip_inbound_short_109",
        "channel": "sip",
        "offset_mins": 340,
        "duration_secs": 32,
        "outcome": "failed",
        "outcome_reason": "user_declined_early",
        "escalation_created": 0,
        "user_turns": 1,
        "agent_turns": 2,
    },
    {
        "room_name": "voice_room_delhi_110",
        "channel": "browser",
        "offset_mins": 400,
        "duration_secs": 130,
        "outcome": "success",
        "outcome_reason": "Jan Aushadhi Price Comparison: Metformin 500mg generic cost comparison vs branded Glycomet",
        "escalation_created": 0,
        "user_turns": 4,
        "agent_turns": 5,
    },
    {
        "room_name": "voice_room_abdm_111",
        "channel": "browser",
        "offset_mins": 470,
        "duration_secs": 175,
        "outcome": "success",
        "outcome_reason": "ABDM FHIR R4 SOAP clinical encounter notes compiled and linked to ABHA ID",
        "escalation_created": 0,
        "user_turns": 5,
        "agent_turns": 6,
    },
    {
        "room_name": "voice_room_dengue_112",
        "channel": "browser",
        "offset_mins": 530,
        "duration_secs": 190,
        "outcome": "success",
        "outcome_reason": "Dengue Warning Signs Triage: Platelet monitoring protocol & warning signs explained",
        "escalation_created": 0,
        "user_turns": 6,
        "agent_turns": 7,
    },
    {
        "room_name": "sip_silent_113",
        "channel": "sip",
        "offset_mins": 600,
        "duration_secs": 20,
        "outcome": "no_answer",
        "outcome_reason": "silent_disconnect",
        "escalation_created": 0,
        "user_turns": 0,
        "agent_turns": 1,
    },
    {
        "room_name": "voice_room_elderly_114",
        "channel": "browser",
        "offset_mins": 660,
        "duration_secs": 155,
        "outcome": "success",
        "outcome_reason": "Elderly Care: Osteoporosis calcium supplement timing & home fall prevention guidance",
        "escalation_created": 0,
        "user_turns": 5,
        "agent_turns": 6,
    },
    {
        "room_name": "sip_trauma_115",
        "channel": "sip",
        "offset_mins": 720,
        "duration_secs": 88,
        "outcome": "success",
        "outcome_reason": "Emergency 108 Dispatch: Road traffic accident acute trauma & local CHC trauma latch",
        "escalation_created": 1,
        "user_turns": 2,
        "agent_turns": 3,
    },
    {
        "room_name": "voice_room_cataract_116",
        "channel": "browser",
        "offset_mins": 790,
        "duration_secs": 140,
        "outcome": "success",
        "outcome_reason": "Eye Health: Free Ayushman Bharat National Blindness Control cataract screening camp",
        "escalation_created": 0,
        "user_turns": 4,
        "agent_turns": 5,
    },
    {
        "room_name": "voice_room_pediatric_117",
        "channel": "browser",
        "offset_mins": 860,
        "duration_secs": 165,
        "outcome": "success",
        "outcome_reason": "Pediatric Care: Paracetamol safe weight-based dosage guidance with strict doctor check",
        "escalation_created": 0,
        "user_turns": 5,
        "agent_turns": 6,
    },
    {
        "room_name": "sip_asha_followup_118",
        "channel": "sip",
        "offset_mins": 920,
        "duration_secs": 110,
        "outcome": "success",
        "outcome_reason": "ASHA Community Worker Follow-up: Pulse polio booster confirmation for village ward",
        "escalation_created": 0,
        "user_turns": 4,
        "agent_turns": 4,
    },
    {
        "room_name": "voice_room_bilingual_119",
        "channel": "browser",
        "offset_mins": 1000,
        "duration_secs": 205,
        "outcome": "success",
        "outcome_reason": "Multilingual Live Switch: Dynamic English to Hindi transition mid-consultation",
        "escalation_created": 0,
        "user_turns": 7,
        "agent_turns": 8,
    },
    {
        "room_name": "sip_dropped_120",
        "channel": "sip",
        "offset_mins": 1080,
        "duration_secs": 45,
        "outcome": "failed",
        "outcome_reason": "user_declined_early",
        "escalation_created": 0,
        "user_turns": 1,
        "agent_turns": 2,
    },
    {
        "room_name": "voice_room_tb_121",
        "channel": "browser",
        "offset_mins": 1150,
        "duration_secs": 210,
        "outcome": "success",
        "outcome_reason": "Tuberculosis DOTS Guidance: Nikshay Poshan Yojana direct benefit transfer advisory",
        "escalation_created": 0,
        "user_turns": 6,
        "agent_turns": 7,
    },
    {
        "room_name": "voice_room_telemanas_122",
        "channel": "browser",
        "offset_mins": 1220,
        "duration_secs": 230,
        "outcome": "success",
        "outcome_reason": "Mental Health: Tele-MANAS national mental health counseling referral (Toll-Free 14416)",
        "escalation_created": 1,
        "user_turns": 7,
        "agent_turns": 8,
    },
    {
        "room_name": "sip_diabetes_123",
        "channel": "sip",
        "offset_mins": 1300,
        "duration_secs": 175,
        "outcome": "success",
        "outcome_reason": "Type-2 Diabetes Fasting Blood Sugar: Glycemic control & morning walking regimen",
        "escalation_created": 0,
        "user_turns": 5,
        "agent_turns": 6,
    },
    {
        "room_name": "voice_room_burns_124",
        "channel": "browser",
        "offset_mins": 1380,
        "duration_secs": 125,
        "outcome": "success",
        "outcome_reason": "First-Aid Burn Triage: Superficial domestic scald immediate cool-water cooling guidance",
        "escalation_created": 0,
        "user_turns": 4,
        "agent_turns": 5,
    },
]


def seed_sqlite():
    db_path = os.path.abspath("data/helpline.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_name TEXT NOT NULL,
        channel TEXT NOT NULL,
        started_at TEXT NOT NULL,
        ended_at TEXT,
        duration_secs REAL,
        outcome TEXT NOT NULL,
        outcome_reason TEXT,
        escalation_created INTEGER DEFAULT 0,
        user_turns INTEGER DEFAULT 0,
        agent_turns INTEGER DEFAULT 0
    )
    """)

    cur.execute("DELETE FROM calls")

    for call in SAMPLE_CALLS:
        start_time = NOW - timedelta(minutes=call["offset_mins"])
        end_time = start_time + timedelta(seconds=call["duration_secs"])
        cur.execute(
            """
            INSERT INTO calls (room_name, channel, started_at, ended_at, duration_secs, outcome, outcome_reason, escalation_created, user_turns, agent_turns)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                call["room_name"],
                call["channel"],
                start_time.isoformat(),
                end_time.isoformat(),
                call["duration_secs"],
                call["outcome"],
                call["outcome_reason"],
                call["escalation_created"],
                call["user_turns"],
                call["agent_turns"],
            ),
        )

    con.commit()
    count = cur.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
    con.close()
    print(f"[+] Successfully seeded {count} calls into local SQLite ({db_path})")


def seed_supabase():
    url = "https://liwfabrlvlvitwnkbsxh.supabase.co/rest/v1/calls"
    key = "sb_publishable_sdad34EuuNb5AQgLf16gKg_RIl2fh-x"

    rows = []
    for call in SAMPLE_CALLS:
        start_time = NOW - timedelta(minutes=call["offset_mins"])
        end_time = start_time + timedelta(seconds=call["duration_secs"])
        rows.append(
            {
                "room_name": call["room_name"],
                "channel": call["channel"],
                "started_at": start_time.isoformat(),
                "ended_at": end_time.isoformat(),
                "duration_secs": call["duration_secs"],
                "outcome": call["outcome"],
                "outcome_reason": call["outcome_reason"],
                "escalation_created": call["escalation_created"],
                "user_turns": call["user_turns"],
                "agent_turns": call["agent_turns"],
            }
        )

    data = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10.0) as res:
            print(f"[+] Successfully seeded {len(rows)} calls into Supabase Cloud (Status: {res.status})")
    except Exception as e:
        print(f"[!] Supabase seed failed: {e}")


if __name__ == "__main__":
    seed_sqlite()
    seed_supabase()

