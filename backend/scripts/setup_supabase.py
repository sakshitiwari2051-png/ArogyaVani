"""Supabase verification and health-check script for ArogyaVani.

Checks if Supabase REST API is accessible and verifies that the 4 required
tables (callers, escalations, calls, clinical_notes) exist.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY") or os.getenv(
    "SUPABASE_PUBLISHABLE_KEY", ""
)

REQUIRED_TABLES = ["callers", "escalations", "calls", "clinical_notes"]


def check_tables() -> dict[str, bool]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        print(
            "[!] ERROR: SUPABASE_URL or SUPABASE_SECRET_KEY is missing from .env.local"
        )
        return {}

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    status: dict[str, bool] = {}
    with httpx.Client(timeout=10.0) as client:
        # Check REST root OpenAPI definitions
        try:
            r = client.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
            if r.status_code == 200:
                defs = r.json().get("definitions", {})
                for table in REQUIRED_TABLES:
                    status[table] = table in defs
            else:
                print(f"[!] REST API returned HTTP {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[!] Failed to reach Supabase REST API: {e}")

    return status


def main():
    print("=" * 60)
    print("AROGYAVANI SUPABASE CLUSTER VERIFICATION")
    print(f"URL: {SUPABASE_URL}")
    print("=" * 60)

    tables = check_tables()
    missing = [t for t, exists in tables.items() if not exists]

    if not tables:
        print("[X] Could not connect to Supabase.")
        sys.exit(1)

    print("\nTable Status:")
    for t, exists in tables.items():
        status_str = "EXISTS (Ready)" if exists else "NOT FOUND"
        symbol = "[OK]" if exists else "[--]"
        print(f"  {symbol} public.{t.ljust(16)} : {status_str}")

    if missing:
        print("\n" + "!" * 60)
        print("ACTION REQUIRED TO COMPLETE SUPABASE MIGRATION:")
        print("1. Open Supabase SQL Editor:")
        print("   https://supabase.com/dashboard/project/liwfabrlvlvitwnkbsxh/sql/new")
        print("2. Copy the SQL from:")
        print("   supabase/migrations/20261106_init_arogyavani.sql")
        print("3. Paste and click 'Run'.")
        print("4. Re-run this check: uv run python scripts/setup_supabase.py")
        print("!" * 60)
    else:
        print(
            "\n[SUCCESS] All 4 Supabase tables are initialized and ready for production!"
        )


if __name__ == "__main__":
    main()
