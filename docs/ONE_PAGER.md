# 🇮🇳 ArogyaVani (आरोग्यवाणी) — Executive One-Pager
### Sovereign Indic Voice AI Health Helpline for 1.4 Billion Citizens
**Built for the Great Indian AI Internship Challenge 2026 · Track: Healthcare Voice AI · Powered by Gnani.ai**

---

### 🌐 Quick Evaluation Links
| Resource | URL | Status |
| :--- | :--- | :---: |
| **Live Web Platform** | [https://arogya-vani-jet.vercel.app](https://arogya-vani-jet.vercel.app) | **Live (Mumbai bom1 Edge)** |
| **Cloud Voice Agent** | [https://arogyavani-6dbk.onrender.com](https://arogyavani-6dbk.onrender.com) | **Healthy (Docker Container)** |
| **GitHub Repository** | [https://github.com/sakshitiwari2051-png/ArogyaVani](https://github.com/sakshitiwari2051-png/ArogyaVani) | **Public (157/157 Tests Pass)** |
| **Full Documentation** | [Read Full Technical Architecture (`README.md`)](../README.md) | **Comprehensive Spec** |

---

### 1. Problem Statement & The Bharat Reality
* **800M+ Indians** in Tier-2/3 cities and rural villages lack fluent English and digital smartphone literacy; traditional chat interfaces fail them.
* **1:1,456 Doctor-to-Patient Ratio**: Rural PHCs (Primary Health Centres) are overcrowded, leading to delayed emergency triage and preventable mortality.
* **Generic LLMs Fail in Clinical Healthcare**: Open-source/Western voice bots hallucinate dangerous dosages, drop regional Indian phonemes, and lack deterministic safety controls for life-threatening emergencies.

### 2. The Solution: ArogyaVani Sovereign Voice Architecture
ArogyaVani is a **bilingual (Hindi/English) voice-first sovereign health helpline** reachable via both modern WebRTC and legacy 2G/PSTN feature phones (Twilio SIP).

```
[ Rural Caller (WebRTC / 2G Phone) ]
                  │
                  ▼
[ Gnani Prisma v2.5 STT ] ──> [ Deterministic 108 Emergency Latch ] ──> (Critical? Immediate 108 Bypass)
                  │                              │ (Non-critical triage)
                  ▼                              ▼
     [ LiveKit Voice Pipeline ]  <───  [ Gnani Evon v3.3 Healthcare LLM ]
                  │
                  ▼
[ Gnani Timbre v2.5 TTS ] ──> Empathic Indic Speech Stream (Nalini / hi-IN)
                  │
                  ├──> Pushes Live OpenStreetMap / PHC Cards to UI (`facility_card`)
                  └──> Compiles ABDM-Compliant HL7 FHIR R4 SOAP Clinical Record
```

### 3. Core Technical & Clinical Innovations
1. **Deterministic 108 Emergency Guardrail**: Hard-coded deterministic triage latch completely bypasses the LLM for red-flag emergencies (chest pain, acute breathlessness, stroke, heavy hemorrhage) to deliver immediate 108 dispatch with zero hallucination.
2. **PMBJP Jan Aushadhi Salt Mapping**: Maps branded, expensive drugs (e.g., Augmentin 625) to affordable generic chemical equivalents (Amoxicillin + Clavulanic Acid), reducing out-of-pocket costs by 50–80% with pharmacist verification disclaimers.
3. **ABDM HL7 FHIR R4 Interoperability**: Every consultation auto-compiles an Ayushman Bharat Digital Mission (ABDM) compliant FHIR R4 Clinical SOAP Note stored securely with SNOMED-CT clinical coding.
4. **DPDP Act 2023 & GDPR Privacy Compliance**: No PII retained in plaintext; sessions authenticated via HMAC-SHA256 signed caller tokens; supports instant 1-click atomic memory purge (`POST /api/forget`).

### 4. Verified Metrics & Engineering Rigor
* **157 / 157 Pytest Tests Passing (100% Pass Rate)**:
  * `47/47` Deterministic Emergency Safety Latches (`test_emergency_guard.py`)
  * `25/25` Red-Team Adversarial Jailbreak & Injection Defenses (`test_red_team_adversarial.py`)
  * `22/22` Gnani.ai Sovereign Stack Integrations (`test_gnani_*.py`)
  * `63/63` Telephony, Multi-Agent Handoff, Tools & Database Evals
* **Voice Pipeline Latency**: Streaming audio Time-to-First-Byte (TTFB) **< 650ms** across Mumbai edge.
* **Production Deployed**: Next.js 15 frontend on Vercel (`bom1`) paired with containerized LiveKit agent backend on Render.

---

> 📖 *For deep architectural blueprints, benchmark charts, red-team methodology, and setup instructions, see the complete [Root README.md](../README.md).*

