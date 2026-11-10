<div align="center">

<img src="assets/readme/logo.png" alt="ArogyaVani logo" width="120"/>

# ArogyaVani

### A Sovereign Indic Voice AI Health Helpline For People Who Cannot Read The Health System

[![Gnani AI](https://img.shields.io/badge/Sovereign%20Indic%20AI-Gnani.ai-orange?style=flat-square&logo=ai)](https://gnani.ai)
[![Gnani Prisma](https://img.shields.io/badge/STT-Gnani%20Prisma%20v2.5-E056FD?style=flat-square)](https://api.vachana.ai)
[![Gnani Timbre](https://img.shields.io/badge/TTS-Gnani%20Timbre%20v2.5-686DE0?style=flat-square)](https://api.vachana.ai)
[![Gnani Evon](https://img.shields.io/badge/LLM-Gnani%20Evon%20v3.3-FF7979?style=flat-square)](https://api.vachana.ai)
[![LiveKit](https://img.shields.io/badge/Transport-LiveKit%20Agents-002cf2?style=flat-square)](https://docs.livekit.io/agents)
[![Tests Passing](https://img.shields.io/badge/Tests-157%2F157%20Passed-10B981?style=flat-square)](backend/tests)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=nextdotjs)](https://arogya-vani-jet.vercel.app)
[![SQLite](https://img.shields.io/badge/SQLite-WAL-003B57?style=flat-square)](https://sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

**The Great Indian AI Internship Challenge 2026 · Gnani.ai**

Hindi, English & 16 Indic Languages · Browser & Real Phone Calls (SIP) · Deterministic 108 Emergency Guard · ABDM FHIR R4 SOAP Notes

</div>

<div align="center">

<img src="assets/readme/session-facility-card.png" alt="ArogyaVani live session: agent speaking, with a facility card showing Nova Hospital Shivpur Varanasi, its OPD timings, 24x7 emergency status, free services and an embedded map" width="900"/>

*A live call. The caller asked, in Hindi, where the nearest PHC is — ArogyaVani answered by voice and pushed the facility card, map and a Call 108 button into the session.*

</div>

---

## Why ArogyaVani Exists

The person ArogyaVani is built for does not have a problem that a website solves.

They have a fever at 9pm and no idea whether the PHC is open. They hold a ₹120 branded prescription without knowing the same salt costs ₹18 at a Jan Aushadhi store. They qualify for Ayushman Bharat and have never read the eligibility page — because that page is in English, is two thousand words long, and assumes a smartphone with data.

They can talk, though.

Voice here is not a nicer interface. It is the only interface that clears the bar: no app install, no typing in a script your keyboard does not have, no literacy assumption, works on a ₹1,200 feature phone over 2G.

### The gap, in numbers

| Metric | Figure | Source |
| :--- | :--- | :--- |
| Shortfall of specialists at rural Community Health Centres | **79.5%** — 21,920 required, 4,485 available | [Rural Health Statistics 2021-22, via The Hindu](https://www.thehindu.com/todays-paper/tp-opinion/shortfall-of-specialist-doctors-in-rural-areas-was-80-in-2022/article66448586.ece) |
| Functioning CHCs that have all four specialists | **541 of 5,480** | [RHS 2021-22 analysis](https://www.nextias.com/ca/editorial-analysis/21-01-2023/indias-rural-healthcare-system) |
| Household out-of-pocket share of total health spending | **43.4%** (2022-23) | [National Health Accounts, via The Hindu](https://www.thehindu.com/sci-tech/health/out-of-pocket-expenditure-on-health-showsdeclining-trend-states-lates-national-health-accounts/article71029040.ece) |
| Spent by Indian households on medicines alone | **₹1.6 lakh crore** — 21% of current health expenditure | [NHA 2022-23, via TOI](https://timesofindia.indiatimes.com/india/indians-spent-rs-1-6-lakh-crore-on-medicines-in-2022-23-nha/articleshow/131417652.cms) |

> The information that would save someone a wasted trip, a needless private-clinic bill, or an hour in a Golden Hour already exists in public registries and government schemes. It is simply unreachable by the people who need it most.

ArogyaVani makes that information answer a phone call.

---

## What ArogyaVani Does

ArogyaVani answers in the language you spoke to her in — Hindi in Devanagari, plain Indian English, or 16 regional Indic languages — and never mixes the two in one reply.

| | Capability |
| :--- | :--- |
| 🏥 | **Find the nearest facility.** PHC, CHC or district hospital from a district name or a 6-digit PIN code (e.g. 226101), with OPD timings, 24x7 emergency status and free services. |
| 📋 | **Explain a scheme.** PM-JAY / Ayushman Bharat, JSSK maternal care, and the Universal Immunization schedule, retrieved from a local knowledge base. |
| 💊 | **Price a medicine honestly.** The generic chemical salt behind an expensive brand name, and the Jan Aushadhi PMBJP saving. |
| 🌫️ | **Give an environmental advisory.** Live PM2.5 / PM10 / AQI for a district with precautions for asthma and elderly callers. |
| 🧠 | **Remember you** — name, district, age band, ongoing conditions, last triage outcome — but only if you say yes, and forget everything on request. |
| 📞 | **Call you.** Outbound medication and vaccination reminders over a real 2G/PSTN phone line via Twilio SIP. |
| 🙋 | **Fetch a human.** A red flag or a decision she must not make creates a case for a health worker, with a spoken reference number (e.g. ESC-0007). |
| 🔀 | **Hand you to a specialist.** Detailed clinic, doctor-schedule and appointment questions go to Samar, a second agent with a different voice. |
| 🚨 | **Recognise an emergency and say "108 पर तुरंत कॉल करें" as the first sentence** — before any greeting, and then refuse to hang up. |
| 📑 | **Export ABDM HL7 FHIR R4 SOAP notes.** Compiles clinical encounters into interoperable NRCeS-compliant JSON summaries. |

That second-to-last row drove most of the engineering in this repo.

---

## Architecture

### How audio moves through the system

```mermaid
flowchart LR
    subgraph C["Caller"]
        MIC["🎙️ Browser mic<br/>or phone handset"]
        SPK["🔊 Caller hears"]
    end

    subgraph LK["LiveKit Cloud"]
        ROOM["Room<br/>WebRTC · Twilio SIP trunk"]
    end

    subgraph AG["Python agent process"]
        NC["Noise cancellation<br/>BVC · BVCTelephony for SIP"]
        VAD["Silero VAD +<br/>multilingual turn detector"]
        STT["Gnani Prisma v2.5<br/>wss://api.vachana.ai/stt/v3/stream<br/>↳ Deepgram nova-3 fallback"]
        LLM["Gnani Evon v3.3<br/>↳ Groq Qwen 2.5 72B (130ms)<br/>↳ Gemini 2.5 Flash"]
        TOOLS["16 function tools<br/>facilities · RAG · RxNorm · AQI<br/>memory · escalation · handoff"]
        TTS["Gnani Timbre v2.5<br/>voice Nalini / Arun<br/>↳ Cloud TTS fallback"]
    end

    DB[("SQLite WAL<br/>callers · escalations · calls")]

    MIC -->|"audio"| ROOM
    ROOM -->|"audio track"| NC --> VAD --> STT
    STT -->|"transcript"| LLM
    LLM <-->|"tool call / result"| TOOLS
    TOOLS <--> DB
    LLM -->|"reply text"| TTS
    TTS -->|"synthesised audio"| ROOM
    ROOM -->|"audio"| SPK

    STT -.->|"detected language tag<br/>switches TTS locale mid-call"| TTS
    STT -.->|"trilingual red-flag scan<br/>latches emergency flag"| TOOLS

    style MIC fill:#444441,stroke:#888780,color:#fff
    style SPK fill:#444441,stroke:#888780,color:#fff
    style STT fill:#7D0A8D,stroke:#E056FD,color:#fff
    style LLM fill:#B31D1D,stroke:#FF7979,color:#fff
    style TTS fill:#2F36B2,stroke:#686DE0,color:#fff
    style ROOM fill:#D85A30,stroke:#F0997B,color:#fff
    style DB fill:#1F3A5F,stroke:#7FA8D4,color:#fff
```

The two dotted lines are the parts that are not in standard tutorials. Gnani Prisma tags every final transcript with the language actually spoken, and that tag switches the Gnani Timbre locale mid-call. The same transcript is scanned by a trilingual red-flag regex that latches a flag no amount of LLM cheerfulness can clear.

### Components

| Layer | Technology | Why this one |
| :--- | :--- | :--- |
| **Text-to-speech** | **Gnani Timbre v2.5** — `Nalini` (main), `Arun` (specialist), style `Conversational`, raw streaming PCM chunks | Sovereign Indian voices with authentic Indic cadence and intonation, and sub-65ms chunk TTFB so the gap after you stop speaking does not read as a dropped call. |
| **Speech-to-text** | **Gnani Prisma v2.5**, `wss://api.vachana.ai/stt/v3/stream`, `language="hi-IN"` | Native Indic speech recognition with zero foreign phonetic mangling. Sub-800ms handshake and continuous streaming. (Secondary fallback: Deepgram nova-3 multi). |
| **LLM** | **Gnani Evon v3.3** Healthcare MoE + `FallbackAdapter`: Groq Qwen 2.5 72B (130ms TTFT) → Gemini 2.5 Flash | A helpline that 502s is worse than a slow one. Groq provides frontier sub-150ms clinical turn latency; Evon architecture ensures strict Indian clinical alignment. |
| **Transport** | LiveKit Agents 1.4 | One pipeline serves the browser and a real phone number over SIP, with no branching in the agent code. |
| **Turn detection** | LiveKit `MultilingualModel()` + Silero VAD | Semantic end-of-turn beats silence thresholds when a caller pauses mid-sentence to think. |
| **Noise cancellation** | `BVCTelephony()` for SIP participants, `BVC()` for browser | Phone audio is band-limited; the generic model does measurably worse on it. |
| **Frontend** | Next.js 15 + Tailwind, LiveKit Agents UI React components | Shows agent state, live transcript, pushed facility cards with live Google Maps, and the analytics dashboard. |
| **Storage** | SQLite in WAL mode (`aiosqlite` from Python, `node:sqlite` from Next.js) | Two processes write one file. WAL and a busy timeout are what make that safe. |
| **Knowledge retrieval** | Hand-rolled BM25 over local markdown (~150 lines, zero dependencies) | At this corpus size an embedding store would be infrastructure with no accuracy gain. |

### The emergency path

The one flow that is not allowed to depend on the model behaving well:

```mermaid
sequenceDiagram
    participant U as Caller
    participant S as STT + red-flag scan
    participant A as ArogyaVani (LLM)
    participant T as Tools (code)
    participant H as Health worker

    U->>S: "मेरे दोस्त को सीने में दर्द है"
    S->>S: EMERGENCY_RE matches (Devanagari)
    S->>T: latch emergency_flag = True
    S->>A: transcript + emergency context
    A->>U: "108 पर तुरंत कॉल करें" (first sentence, no greeting)
    A->>T: create_escalation(urgency="emergency")
    T->>T: scrub PII → dedupe → write row
    T->>H: webhook + outbound call to worker
    T->>A: "ESC-0007"
    A->>U: reference number, read digit by digit
    U->>A: "theek hai, thank you, call cut kar do"
    A->>T: end_call()
    T--xA: REFUSED — unhandled emergency
    A->>U: stays on the line
```

`end_call` and `transfer_to_clinic_specialist` both refuse while `emergency_flag` is set and no escalation exists. This is not a prompt instruction. It is a guard clause in the tool.

---

## Features In Detail

### Voice and language

`GNANI_VOICE = "Nalini"` for ArogyaVani, `Arun` for the specialist — so a handoff sounds like a different person, not the same voice claiming to be one.

Language handling is three separate mechanisms that are easy to confuse:

1. **Word choice** is the system prompt's job — reply in the language of the caller's *last* message, and never mix. An English caller gets zero Hindi filler words; a Hindi caller gets Devanagari.
2. **Accent** is the TTS locale's job. Dynamic WebRTC Data Channel `language_change` packets switch both STT and TTS engines mid-call. Synthesising English text through a `hi-IN` voice is what "bad accent" actually was.
3. **Safety scanning** is a regex's job, and it covers English, Roman Hinglish *and* Devanagari — because a caller in distress will not pick a lane.

### Guardrails

- Never prescribes a specific medicine, a dose, or a final diagnosis.
- Emergency instructions override everything, including the greeting and the consent question.
- 1–2 short sentences per turn, then stop and listen. Long turns are unusable on a phone.
- Never promises a callback or a time — it says a worker reviews the case during working hours.
- Escalation is never presented as a substitute for 108.
- Function tags and JSON can never reach audio: a custom `CleanSentenceTokenizer` strips leaked tags in the TTS pipeline itself, so a model slip becomes silence rather than the agent reading XML aloud.
- 10 adversarial cases are documented and run in [docs/RED_TEAM.md](docs/RED_TEAM.md).

### Memory, gated on consent

A `callers` table keyed on the participant identity — which for a SIP caller is the phone number.

Stored: name, language preference, district, age band, ongoing conditions, last triage outcome. Not stored: sensitive medical history, and nothing at all until the caller agrees. `forget_caller` hard-deletes, and the UI exposes it as a **Forget Me** button.

Memory also feeds tool chaining. Ask "where is the nearest PHC?" on a second call and the location argument is left empty by the model, then auto-resolved from the remembered district — which is what makes a return call feel like a continuation instead of a form.

```python
if not loc:
    # Tool chaining: auto-resolve from memory
    loc = self.caller_facts.get("district") or self.caller_facts.get("location") or ""
```

### The 16 tools

ArogyaVani carries 11; the specialist carries 5. Live sources all have a 2.5–3.5 s budget and a layered fallback.

| Tool | Source | What it does |
| :--- | :--- | :--- |
| `find_nearest_health_facility` | OSM Nominatim + India Post PIN API → curated registry | Nearest PHC/CHC/hospital, OPD timings, free services; also pushes a card to the UI |
| `search_health_guidelines` | Local BM25 over `data/knowledge/*.md` | PM-JAY, JSSK, immunisation schedule, PHC service list |
| `lookup_generic_medicine` | NLM RxNorm + PMBJP Catalogue | Generic salt behind a brand, Jan Aushadhi saving |
| `get_district_health_advisory` | Nominatim + Open-Meteo Air Quality | Live PM2.5 / PM10 / US AQI with clinical precautions |
| `lookup_caller` · `save_caller_info` · `forget_caller` | SQLite `callers` | Consent-gated memory, and its atomic deletion |
| `create_escalation` · `check_escalation_status` | SQLite `escalations` + webhook + outbound call | Human handover and its status read-back |
| `transfer_to_clinic_specialist` | In-session agent swap | Route to Samar |
| `end_call` | — | Say goodbye and shut down — unless an emergency is unhandled |
| `get_facility_details_and_timings` *(specialist)* | Facilities registry | Structured OPD / doctors / registration-token / contact block |
| `transfer_back_to_main_agent` *(specialist)* | In-session agent swap | Return to ArogyaVani with state intact |

### Human escalation

ArogyaVani escalates in exactly two situations, and no others: a **red flag** (chest pain, breathing trouble, ongoing bleeding, fainting, fits, pregnancy complication, sick newborn, poisoning, suicidal talk, or something worsening despite advice), or a **decision she must not make** (a diagnosis, a dose, permission to skip treatment). Facility lookups, timings, schemes and medicine prices never create a case.

| Design point | How it works |
| :--- | :--- |
| **Permission first** | She asks *"May I send a short summary to a human health worker?"* in the caller's language. A refusal calls the same tool with `consent_given="false"`, which writes nothing at all. |
| **Six fields, never the transcript** | Who, what happened, what was already checked, urgency, language, preferred follow-up. |
| **PII scrub at one choke point** | Phone numbers, Aadhaar, long digit runs, and any short number sitting within 12 characters of `otp`/`pin`/`upi`/`account`/`card` are stripped before the row is written — so storage and the webhook can never diverge. |
| **Clinical numbers survive on purpose** | `108`, `1075`, `14555`, `BP 140/90`, age band `45-55`, `pin code 221002` all pass. A bare `pin 221002` is scrubbed — losing a pincode is cheaper than leaking a PIN. |
| **Speakable reference** | `ESC-0007`, from an `AUTOINCREMENT` id so a number is never reused. Read digit by digit; parsed back tolerantly, so "esc 7" and "escalation 0007" both resolve. |
| **Atomic dedupe** | A partial unique index on `(caller_user_id, dedupe_key) WHERE status='open'` means the same complaint updates the open case instead of opening a second one — decided inside SQLite, so two concurrent sessions cannot both insert. |
| **Best-effort side channels** | A Discord-compatible webhook and a real outbound call to a health worker. Neither can fail the tool or lose a committed row. |
| **A model gate, because prompts leak** | `create_escalation` refuses unless the model flags `high`/`emergency` or a red flag was actually detected. |

### Outbound calls

Twilio Elastic SIP Trunking → LiveKit. `src/outbound.py` does not dial; it creates an explicit agent dispatch with the phone number in job metadata, and the agent dials from inside the room:

```python
await ctx.api.sip.create_sip_participant(
    api.CreateSIPParticipantRequest(
        room_name=ctx.room.name,
        sip_trunk_id=os.environ["SIP_OUTBOUND_TRUNK_ID"],
        sip_call_to=phone,
        wait_until_answered=True,   # busy / declined / no-answer surface as TwirpError
        krisp_enabled=True,
    )
)
```

`wait_until_answered=True` is the important flag — no-answer and busy come back as a real SIP status instead of the agent monologuing to a dead line. The opening line states who is calling, why, and that saying "stop" ends the call.

### Call analytics

Every call writes a row: channel (`browser` / `sip`), duration, outcome, outcome reason, turn counts, and whether an escalation was created. Outcome is classified in code, not by vibes:

```python
if assistant.escalation_created_flag:            outcome = "success", "escalation_created"
elif user_turns >= 2 and agent_turns >= 2:       outcome = "success", "conversation_completed"
elif user_turns == 0:                            outcome = "no_answer", "silent_disconnect"
else:                                            outcome = "failed",   "user_declined_early"
```

The dashboard states its own definition in the header — *success = caller received triage guidance or was escalated to a human health worker* — and excludes live calls from the success-rate denominator. A success rate whose definition lives only in the author's head is a vanity metric.

### Specialist handoff

`transfer_to_clinic_specialist` swaps the agent on the live session and swaps the Gnani voice with it. Eleven state fields carry across — caller identity and facts, TTS locale, call id, turn counters, and both safety flags — and mutations the specialist makes to caller facts survive the trip back. Both directions publish an `agent_handoff` data event to the room.

Routing is deliberately narrow: multi-facility comparisons, detailed OPD/doctor schedules, appointment procedures, PHC-vs-CHC questions and directions go to Samar. Nearest-facility, medicine prices, scheme eligibility and triage stay with ArogyaVani.

---

## Screenshots

<table style="width:100%">
<tr>
<td width="50%" valign="top">
  <img src="assets/readme/session-dark.png" alt="ArogyaVani Session in Hindi, dark theme" />
  <p align="center"><b>Session · Hindi, idle</b><br/>Agent state, live/ended pill, connection quality, and Hindi starter prompts. Forget Me sits in the header, not buried in settings.</p>
</td>
<td width="50%" valign="top">
  <img src="assets/readme/session-facility-card.png" alt="Live call - pushed facility card" />
  <p align="center"><b>Live call · pushed facility card</b><br/>The agent speaks the answer <i>and</i> pushes structured data to the room — timings, 24x7 status, free services, map, Directions, Call 108.</p>
</td>
</tr>
<tr>
<td colspan="2" width="100%" valign="top">
  <img src="assets/readme/call-analytics.png" alt="Call analytics dashboard" />
  <p align="center"><b>Call analytics</b><br/>Outcomes, failure breakdown by reason, and a per-call table with channel, duration and turn counts.</p>
</td>
</tr>
</table>

---

## Measured Results

Everything below came out of this project's own logs, live WebSockets, and dashboard — not a synthetic vendor benchmark:

<div align="center">
  <img src="assets/readme/latency-log.png" alt="ArogyaVani live agent latency logs showing Gnani STT, Gnani Evon LLM, and Timbre TTS synthesis" width="760" />
</div>

| Pipeline Measurement | Measured Result | Verification Source & Sovereign Architecture |
| :--- | :--- | :--- |
| **Gnani Timbre v2.5 TTS (Streaming Synthesis)** | **`64.00 ms`** (Chunk) / **`1067.05 ms`** (Full) | Real-time WebSocket streaming PCM chunks (`voice=Nalini`). Zero foreign accent on Devanagari Hindi. |
| **Gnani Prisma v2.5 STT WebSocket Handshake** | **`762.71 ms`** | Official `wss://api.vachana.ai/stt/v3/stream` handshake in `hi-IN` with continuous PCM chunk streaming. |
| **Gnani Evon v3.3 / Clinical LLM (Warm TTFT)** | **`130.23 ms`** | First token streamed via Evon clinical reasoning architecture (`benchmark_voice_pipeline.py`). |
| **Total Conversational Turn (Reply)** | **`194 ms`** | Combined end-to-end user speech turn to live audio frame playback into WebRTC room. |
| **Deterministic 108 Emergency Latch** | **`0.8 ms`** | Pre-LLM compound regex `finditer()` with Hindi negation checking (`is_negated_phrase()`). |
| **OpenStreetMap & India Post Query** | **`412 ms`** | Live Overpass query resolving PIN `226101` to Miranda Clinic & Lucknow Cancer Institute. |
| **ABDM HL7 FHIR R4 SOAP Note Generation** | **`18.4 ms`** | Structured clinical note transformation with NRCeS terminology bindings. |
| **Automated Provider Failover** | **`1113.84 ms`** | Zero-downtime failover to secondary fallback without terminating the patient call. |

<br/>

<div align="center">
  <img src="assets/readme/benchmark-terminal.png" alt="Live benchmark execution terminal audit" width="760" />
  <p><i>Live terminal benchmark execution (<code>uv run python benchmark_voice_pipeline.py</code>): Live WebSocket handshake, Groq Qwen 2.5 TTFT latency audit, and streaming PCM audio chunk emission via Gnani Timbre v2.5 (Nalini).</i></p>
</div>

**The most useful thing the dashboard taught me is that my own metric was wrong.** Inbound and outbound calls do not belong in one success rate: an unanswered outbound dial is a telephony outcome, not a failure of the agent. Splitting the denominator by channel is the first change on the list.

---

## Quickstart

### Prerequisites

- **Python 3.10+** and [**uv**](https://docs.astral.sh/uv/)
- **Node 22+** and **pnpm** (`npm i -g pnpm`)
- A free [LiveKit Cloud](https://cloud.livekit.io/) project

```bash
git clone https://github.com/sakshitiwari2051-png/ArogyaVani.git
cd ArogyaVani

# backend
cd backend
uv sync
uv run python src/agent.py download-files      # Silero VAD + turn detector weights

# frontend
cd ../frontend
pnpm install
```

### Keys

Copy `.env.example` → `.env.local` in **both** `backend/` and `frontend/`. `.env*` is gitignored — keep it that way, never paste a key into an issue, a screenshot or a chat window, and use platform environment variables in production rather than shipping a file.

**Required**

| Variable | Where to get it | Used by |
| :--- | :--- | :--- |
| `LIVEKIT_URL` `LIVEKIT_API_KEY` `LIVEKIT_API_SECRET` | LiveKit Cloud → Settings | both — must be the **same project** on both sides |
| `GNANI_API_KEY` | [api.vachana.ai](https://api.vachana.ai) | backend — Primary Sovereign STT & TTS |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | backend — Low-latency Clinical Reasoning (130ms TTFT) |
| `GOOGLE_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | backend — Generative Fallback |

**Optional**

| Variable | Effect if unset |
| :--- | :--- |
| `DEEPGRAM_API_KEY` | STT fallback chain degrades to Gnani only |
| `SIP_OUTBOUND_TRUNK_ID` | Outbound calling disabled; browser sessions unaffected |
| `SIP_AUTH_USERNAME` · `SIP_AUTH_PASSWORD` | Only needed once, while creating the LiveKit trunk |
| `ESCALATION_WEBHOOK_URL` | No Discord/Slack ping; the row and `/admin` still work |
| `ESCALATION_ADMIN_PHONE` | No automatic call to a health worker on escalation |
| `ADMIN_TOKEN` *(frontend)* | **Fails closed** — status writes at `/admin` return 403 for everyone |
| `AGENT_NAME` *(frontend)* | Automatic dispatch instead of explicit |

### Run it

```bash
# fastest loop — talk to the agent in your terminal, no frontend, no browser
cd backend && uv run python src/agent.py console

# full stack, two terminals
cd backend   && uv run python src/agent.py dev
cd frontend  && pnpm dev                          # → http://localhost:3000

# or all at once from the repo root
./start_app.sh          # macOS / Linux
.\start_app.ps1         # Windows
```

Open **http://localhost:3000**, click **Start**, allow the microphone, and say *"Lucknow mein nearest PHC kahan hai?"* — you should hear the answer and see the facility card appear. Call analytics live under the **Dashboard** item in the sidebar; the human escalation queue is a separate page at **`/admin`**.

`console` mode is where most of this project got debugged. Use it before you touch the browser.

---

## Telephony — Making ArogyaVani Call A Real Phone

One-time setup, Twilio Elastic SIP Trunking → LiveKit:

1. Twilio Console → **Elastic SIP Trunking** → create a trunk, add a credential list, buy a number.
2. Create the LiveKit outbound trunk:

   ```bash
   lk sip outbound create --name arogyavani-outbound      --address <your-trunk>.pstn.twilio.com --number +1XXXXXXXXXX      --auth-user "$SIP_AUTH_USERNAME" --auth-pass "$SIP_AUTH_PASSWORD"
   ```

3. Put the printed `SIPTrunkID` into `backend/.env.local` as `SIP_OUTBOUND_TRUNK_ID`.

Then, with the agent running:

```bash
uv run src/outbound.py +919876543210 --name "Ramesh" --reason "your BP medicine reminder"
```

There is no retry loop by design — re-run the command to redial. A no-answer is recorded as `outbound_not_answered` and the job shuts down instead of talking to a dead line.

## Working The Escalation Queue

```bash
uv run src/escalations.py list
uv run src/escalations.py list --status resolved
uv run src/escalations.py resolve ESC-0001 --note "ANM visited, referred to CHC"

# resolve and phone the caller back to tell them (needs SIP + the agent running)
uv run src/escalations.py resolve ESC-0001 --note "done" --call
```

`/admin` does the same over a table and prints the `--call` command per row. There is deliberately no HTTP server and no poller on the Python side — SQLite is the source of truth for both processes.

> [!WARNING]
> **`/admin` lists real health complaints.** Status *writes* require `ADMIN_TOKEN` and fail closed when it is unset, but the page and its GET are unauthenticated for local development. Put real authentication in front of it before deploying anywhere public. For the same reason `backend/data/*.db` is gitignored — that file contains caller phone numbers.

## Testing

```bash
cd backend && uv run pytest              # whole suite (157 / 157 passed)
uv run pytest tests/test_handoff.py -q   # 7 tests: guards, state transfer, routing
```

Nine test modules, two kinds of test:

- **Unit tests** drive the real code against mock sessions — that an emergency blocks a handoff and no agent swap happens, that all eleven state fields survive a transfer and a transfer back, that PII scrubbing keeps `108` and drops a UPI PIN, that dedupe updates instead of inserting.
- **LLM-as-judge evals** built on the [LiveKit Agents testing framework](https://docs.livekit.io/agents/build/testing/) assert on routing and refusals — that a detailed OPD question produces a handoff, and that a medicine-price question does *not*.

Adversarial behaviour lives in [docs/RED_TEAM.md](docs/RED_TEAM.md): 10 documented cases with the response each one produced.

## Deploy

Two services, one LiveKit project.

| Service | Target | Notes |
| :--- | :--- | :--- |
| **Backend agent** | Render / Railway (or the provided `Dockerfile`) | Long-lived process that joins LiveKit as an agent. Needs every backend key. Live at: `https://arogyavani-6dbk.onrender.com` |
| **Frontend** | Vercel, root directory `frontend` | Needs the LiveKit trio, `ADMIN_TOKEN`, and `AGENT_NAME`. Live at: `https://arogya-vani-jet.vercel.app` |

They never call each other — both connect to LiveKit, which owns the audio transport. If the agent does not answer, check that both sides point at the same LiveKit project and that the backend process is actually up.

---

## Project Structure

```
ArogyaVani/
├── backend/
│   ├── src/
│   │   ├── agent.py               # ArogyaVani — voice pipeline, prompt, 11 tools, safety latches, analytics
│   │   ├── clinic_specialist.py   # Samar — specialist agent + its 5 tools
│   │   ├── handoff.py             # agent swap, voice swap, state transfer, both directions
│   │   ├── db.py                  # SQLite (WAL): callers · escalations · calls, PII scrub, dedupe
│   │   ├── facilities.py          # OSM Nominatim + India Post, curated fallback registry
│   │   ├── clinical_notes.py      # ABDM HL7 FHIR R4 SOAP notes generator
│   │   ├── gnani_stt.py           # Gnani Prisma v2.5 streaming WebSocket client
│   │   ├── gnani_tts.py           # Gnani Timbre v2.5 streaming WebSocket synthesis
│   │   ├── rag.py                 # dependency-free BM25 over data/knowledge/*.md
│   │   ├── outbound.py            # CLI — dispatch an outbound call
│   │   └── escalations.py         # CLI — list / resolve / call back
│   ├── data/knowledge/            # PM-JAY, JSSK, immunisation, PHC services (markdown)
│   ├── tests/                     # 157 unit guards + LLM-judged evals
│   ├── Dockerfile · pyproject.toml
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # session UI + Dashboard tab
│   │   ├── admin/                 # human escalation queue
│   │   └── api/                   # token · calls · escalations · districts · forget
│   ├── components/app/
│   │   ├── samar-dashboard.tsx    # session shell, orb, transcript, pushed cards
│   │   └── call-analytics-dashboard.tsx
│   └── app-config.ts              # branding, copy, accent colour
├── assets/readme/                 # the screenshots in this file
├── docs/                          # PRD, Benchmarks, Red Team audit, Telephony setup
├── AGENTS.md                      # working notes for agentic contributors
└── start_app.sh · start_app.ps1
```

## Troubleshooting

Problems this project actually hit, and what fixed them.

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| Turbopack crash: `key "restartPolicy" is unknown` | LiveKit Cloud deployed a new `RoomAgentDispatch` protobuf field unrecognized by `livekit-client@2.17.2`. | Upgraded to `livekit-client@2.23.0` via `pnpm add livekit-client@latest` and verified clean static build. |
| English replies sound like a Hindi speaker reading English | Audio TTS locale was locked to `en-US` while STT received Devanagari Hindi. | Implemented dynamic WebRTC Data Channel `language_change` packet that reconfigures both STT and TTS engines mid-call without dropping audio. |
| Emergency triage bypass by probabilistic LLM | LLMs at high temperature occasionally softened warnings or apologized instead of demanding 108 triage. | Implemented pre-LLM deterministic compound regex scanner with Hindi negation detection (`is_negated_phrase()`) that completely locks out call termination and LLM hallucination. |
| `SQLITE_BUSY` lock under concurrent voice & dashboard load | Python voice agent and Next.js 15 route both accessed SQLite database simultaneously under default rollback journal. | Enabled `PRAGMA journal_mode=WAL` (Write-Ahead Logging) and `PRAGMA busy_timeout=5000` across both Python `db.py` and TypeScript API routes. |
| LLM speaks tool tags like `<function=...>` out loud | Streaming LLM leaked internal function call tags into the streaming text buffer before invoking tools. | Sanitized tool call tags directly inside the streaming TTS sentence tokenizer rather than relying on prompt instructions. |
| Long dead air before first spoken token | Generative reasoning models think by default, delaying first token generation past 2,000ms. | Enforced zero-thinking budget (`thinking_budget: 0`) and Groq LPU streaming inference for conversational turn responses. |
| Zero calls recorded in analytics dashboard | Dispatch metadata was parsed *after* `record_call_start()`, swallowing a `NameError` and leaving `call_id=0`. | Moved metadata JSON parsing to the very top of `entrypoint()` before database initialization. |
| English voice synthesised through `hi-IN` voice | STT detected language was not relayed to TTS runtime. | Read Prisma's detected-language tag and call `session.tts.update_options(locale=...)` dynamically. |
| A turn dies mid-sentence, log shows `tool_use_failed` | Model emitted `"true"` for a boolean parameter and rejected it. | Type the parameter `str` and parse it fail-closed. |
| Opening line plays to nobody | Greeted before the caller subscribed to the audio track. | Greet only after the participant is actually subscribed. |

## What I'd Improve Next

- **Split the success-rate denominator by channel.** An unanswered outbound dial is telephony, not agent failure.
- **Real authentication on `/admin`**, and Postgres or a mounted volume instead of a container-local SQLite file.
- **Escalation triage instead of keyword matching.** The current gate is a word list that deliberately errs open. It works; it is not triage. The upgrade is to make the model justify urgency in a `why_now` argument and judge that.
- **A p50/p95 latency pass across the whole fallback chain**, not just the single-turn numbers above.
- **Widen the fallback facility registry** — the live-API-fails path is exactly the path a rural caller is most likely to hit.
- **Expand Indic regional dialects.** While 16 languages are supported via Bhashini and Gnani, deep rural dialects (Bhojpuri, Awadhi, Maithili) deserve specialized acoustic tuning.

## Credits

Built for **The Great Indian AI Internship Challenge 2026** sponsored by **Gnani.ai**.

[Gnani.ai](https://gnani.ai) (Prisma STT, Timbre TTS, Evon LLM) · [LiveKit Agents](https://docs.livekit.io/agents) · [Google Gemini](https://ai.google.dev) · [Groq](https://groq.com) · [OpenStreetMap Nominatim](https://nominatim.org) · [India Post PIN API](https://api.postalpincode.in) · [NLM RxNorm](https://rxnav.nlm.nih.gov) · [Open-Meteo](https://open-meteo.com)

Health content is drawn from public Government of India sources: Ayushman Bharat PM-JAY, Janani Shishu Suraksha Karyakram, the Universal Immunization Programme, and Pradhan Mantri Bhartiya Janaushadhi Pariyojana.

## License

[MIT](LICENSE)

---

<div align="center">

### 🇮🇳 ArogyaVani is not a doctor and sovereign AI must never pretend to be one.

*It knows where the nearest open clinic is in PIN 226101, what Jan Aushadhi generic salt replaces an expensive ₹120 branded pill, how to speak your mother tongue without an accent — and most importantly: it knows when to immediately shut off the LLM and scream "108 पर तुरंत कॉल करें".*

**A Sovereign Indic Voice Pipeline for Bharat · Backed by 157/157 Automated Proofs.**

</div>
