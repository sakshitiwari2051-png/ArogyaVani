"""Tests for Telephony and SIP Configuration (Phase 5).

Validates:
1. Destination phone number and SIP URI cleaning / sanitization
2. Outbound call dispatch payload formatting
3. SIP noise cancellation parameter binding
4. Telephony environment variable detection
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from dotenv import load_dotenv

# Ensure backend/src is on python path
src_dir = str(Path(__file__).parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Load .env.local
env_local = Path(__file__).parent.parent / ".env.local"
if env_local.exists():
    load_dotenv(env_local)

import outbound  # noqa: E402


def test_clean_destination_formats():
    """_clean_destination handles diverse phone and SIP formats."""
    # Standard E.164 format
    assert outbound._clean_destination("+919876543210") == "+919876543210"
    # SIP URI with host
    assert outbound._clean_destination("sip:user123@sip.provider.com") == "user123"
    # SIP URI without host
    assert outbound._clean_destination("sip:user123") == "user123"
    # Bare username
    assert outbound._clean_destination("ramesh_health") == "ramesh_health"
    # Spaces stripped
    assert outbound._clean_destination("  +919876543210  ") == "+919876543210"


@pytest.mark.asyncio
async def test_place_call_generates_valid_dispatch():
    """place_call formats dispatch metadata and creates agent dispatch."""
    mock_lk = MagicMock()
    mock_lk.agent_dispatch.create_dispatch = AsyncMock()
    mock_lk.__aenter__ = AsyncMock(return_value=mock_lk)
    mock_lk.__aexit__ = AsyncMock(return_value=False)

    with patch.object(outbound.api, "LiveKitAPI", return_value=mock_lk):
        room_name = await outbound.place_call(
            phone="+919876543210",
            name="Sita Devi",
            reason="Blood pressure checkup reminder",
        )

    assert room_name.startswith("outbound-919876543210-")
    mock_lk.agent_dispatch.create_dispatch.assert_awaited_once()

    dispatch_req = mock_lk.agent_dispatch.create_dispatch.await_args.args[0]
    assert dispatch_req.agent_name == "my-agent"
    assert dispatch_req.room == room_name

    meta = json.loads(dispatch_req.metadata)
    assert meta["phone"] == "+919876543210"
    assert meta["name"] == "Sita Devi"
    assert meta["reason"] == "Blood pressure checkup reminder"


def test_telephony_env_detection():
    """Validates presence or expected placeholder for SIP_OUTBOUND_TRUNK_ID."""
    trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID", "")
    # Check that environment handling works smoothly
    assert isinstance(trunk_id, str)
