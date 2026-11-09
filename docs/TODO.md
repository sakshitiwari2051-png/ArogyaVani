# 📋 ArogyaVani Execution Roadmap — Phase-by-Phase TODO

> **Target:** 1st Place Champion — Great Indian AI Internship Challenge 2026 (Gnani.ai)  
> **Key Milestones:** Telephony Live Call + 22 Indian Languages (Gnani + Bhashini) + Video Demo

---

## 📌 PHASE 1: Telephony SIP Setup (Live Physical Phone Call)
- [ ] **1.1** Connect Twilio Elastic SIP Trunking or Softphone (MicroSIP / Linphone).
- [ ] **1.2** Set up Inbound SIP route on `arogyavani-8ztj5eef.livekit.cloud`.
- [ ] **1.3** Configure `SIP_OUTBOUND_TRUNK_ID` and credentials in `backend/.env.local`.
- [ ] **1.4** Execute test call using `backend/src/outbound.py` to a real mobile number.
- [ ] **1.5** Record audio log & verify 108 emergency latch on telephony call.

---

## 📌 PHASE 2: Frontend Pan-India Language Switcher
- [ ] **2.1** Expand `LANGUAGES` array in `frontend/components/app/samar-dashboard.tsx` to 16+ languages:
  - Hindi (`hi`), English (`en`), Kannada (`kn`), Tamil (`ta`), Telugu (`te`), Marathi (`mr`), Bengali (`bn`), Gujarati (`gu`), Malayalam (`ml`), Punjabi (`pa`), Odia (`or`), Kashmiri (`ks`), Nepali (`ne`), Assamese (`as`), Urdu (`ur`), Maithili (`mai`).
- [ ] **2.2** Add native script labels and flags for each language.
- [ ] **2.3** Add localized `QUICK_SUGGESTIONS` in native script for Kannada, Tamil, Telugu, Marathi, Bengali, etc.
- [ ] **2.4** Wire active language state change to propagate to LiveKit agent session via Room metadata / chat channel.

---

## 📌 PHASE 3: Backend Bhashini Adapter Development
- [ ] **3.1** Create `backend/src/bhashini_adapter.py` supporting:
  - Bhashini ULCA Pipeline Configuration endpoint (`POST https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline`)
  - Bhashini Compute endpoint (`POST https://dhruva-api.bhashini.gov.in/services/inference/pipeline`)
  - ASR (Speech-to-Text) across 22 languages
  - NMT (Machine Translation via IndicTrans2)
  - TTS (Text-to-Speech) for Kashmiri, Nepali, Bengali, etc.
- [ ] **3.2** Create fallback routing in `backend/src/agent.py`:
  - Primary languages (Hindi, English, Kannada, Tamil, Telugu) ➔ **Gnani.ai Sovereign Core (Prisma STT + Timbre TTS)**
  - Extended languages (Kashmiri, Nepali, Marathi, etc.) ➔ **Bhashini ULCA Layer**
- [ ] **3.3** Add unit tests in `backend/tests/test_bhashini.py`.

---

## 📌 PHASE 4: Credential Collection (Awaiting User API Keys)
- [ ] **4.1** Request Bhashini credentials from user:
  - `BHASHINI_USER_ID`
  - `BHASHINI_API_KEY` (Inference API Key)
  - `BHASHINI_PIPELINE_ID` (optional / auto-discovered)
- [ ] **4.2** Add keys securely to `backend/.env.local`.

---

## 📌 PHASE 5: Live Integration, End-to-End Testing & Debugging
- [ ] **5.1** Run `uv run pytest` to ensure all existing 122 tests + new Bhashini tests pass (100% pass rate).
- [ ] **5.2** Run `next build` to verify frontend compilation.
- [ ] **5.3** Test live language switching on `http://localhost:3000` with Kannada, Tamil, and Kashmiri.
- [ ] **5.4** Validate latency benchmarks (<350ms TTFB across all engines).

---

## 📌 PHASE 6: Git Commit & GitHub Push
- [ ] **6.1** Stage all new modules and tests.
- [ ] **6.2** Create structured conventional commits.
- [ ] **6.3** Fast-forward push to `https://github.com/sakshitiwari2051-png/ArogyaVani`.

---

## 📌 PHASE 7: Final Judge Re-Audit & Video Recording Readiness
- [ ] **7.1** Re-audit project against Gnani judging rubrics with Telephony & Bhashini live.
- [ ] **7.2** Finalize 90-second video demo rehearsal with phone call + multilingual voice switch.

