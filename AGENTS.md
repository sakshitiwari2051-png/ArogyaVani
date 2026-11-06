# AGENTS.md

This is the repository for **ArogyaVani**, a sovereign Indic voice AI health helpline powered by Gnani.ai (Prisma STT, Timbre TTS, Evon LLM) and LiveKit Agents with fallback support (Murf Falcon TTS, Deepgram Nova-3 STT, Groq/Gemini).

## Repository structure

```
ArogyaVani/
├── backend/          # Python voice agent (LiveKit Agents + Gnani.ai / Murf / Deepgram / Groq)
│   ├── src/agent.py  # Agent entrypoint — voice pipeline, clinical tools, and emergency latches
│   └── tests/        # Pytest test suite (157 unit and integration tests)
├── frontend/         # Next.js UI (LiveKit Agents UI components, SAMAR health analytics)
│   ├── app/          # Pages and API routes
│   ├── components/   # UI components (agents-ui, app dashboards, shadcn ui)
│   └── app-config.ts # Branding and feature config
├── start_app.sh      # Start all services (macOS/Linux)
└── start_app.ps1     # Start all services (Windows)
```

## Backend

### Tech stack
- **Python 3.10+** with **uv** package manager
- **LiveKit Agents SDK** (`livekit-agents ~1.4`) — real-time voice pipeline
- **Gnani.ai Sovereign Stack**:
  - **Prisma v2.5** — Indic Speech-to-Text
  - **Timbre v2.5** — Indic Text-to-Speech
  - **Evon v3.3** — Indic Healthcare LLM
- **Fallback Stack**:
  - **Murf Falcon** (`livekit-murf`) — fallback TTS
  - **Deepgram Nova-3** — fallback STT
  - **Groq Qwen 2.5 / Google Gemini** — fallback LLM
- **Silero VAD** + **LiveKit Turn Detector** — voice activity & turn detection
- **Model Context Protocol (MCP)** — health tools & facilities lookup

### Key file: `backend/src/agent.py`
This is the single voice entrypoint. It contains:
- `SYSTEM_PROMPT` — Sovereign Indic health assistant prompt (bilingual Hindi/English, triage latches)
- `HealthAssistant` class — clinical routing, 108 emergency triage, hospital/PHC search, handoff
- `my_agent()` — sets up the pipeline (Gnani with graceful fallback) and connects to LiveKit
- `prewarm()` — pre-loads VAD models

### Running the backend
```bash
cd backend
uv sync
uv run python src/agent.py download-files   # first time only
uv run python src/agent.py dev              # development
uv run python src/agent.py console          # terminal-only testing
```

### Environment variables
Copy `backend/.env.example` to `backend/.env.local`. Required keys:
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- `MURF_API_KEY`
- `DEEPGRAM_API_KEY`
- `GOOGLE_API_KEY`

### Code style
Uses **ruff** for linting and formatting:
```bash
uv run ruff check .
uv run ruff format .
```
Config is in `pyproject.toml` — 88 char line length, double quotes, space indent.

### Testing
Tests are in `backend/tests/test_agent.py`. They use LiveKit's testing framework with LLM-as-judge evaluation (not mocks). Run with:
```bash
uv run pytest
```
Requires `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` to be set.

When modifying the system prompt or adding tools, write tests first. Use the existing tests as a pattern — they call `session.run(user_input=...)` and use `.judge()` to evaluate responses.

### Dependencies
Managed via `uv` and defined in `pyproject.toml`. Always use `uv sync` and `uv run` — never `pip install`.

## Frontend

### Tech stack
- **Next.js** (React, TypeScript)
- **pnpm** package manager
- **LiveKit Agents UI** (shadcn-based components)
- **Tailwind CSS**

### Key files
- `frontend/app-config.ts` — branding, feature flags, accent colors, visualizer config
- `frontend/app/page.tsx` — main page
- `frontend/app/api/token/route.ts` — LiveKit token endpoint
- `frontend/components/app/` — app-level logic (welcome view, view controller, theme)
- `frontend/components/agents-ui/` — voice UI components (visualizers, controls, chat)

### Running the frontend
```bash
cd frontend
pnpm install
pnpm dev
```

### Environment variables
Copy `frontend/.env.example` to `frontend/.env.local`. Required:
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- `AGENT_NAME` (optional — set to `my-agent` for explicit dispatch)

### Linting
```bash
pnpm lint         # ESLint
pnpm format:check # Prettier
```

## Common tasks

### Change what the agent does
Edit `SYSTEM_PROMPT` in `backend/src/agent.py`. See `backend/README.md` for example prompts.

### Change the voice
Edit the `voice` argument in `murf.TTS(...)` in `backend/src/agent.py`. Browse voices at https://murf.ai/api/docs/voices-styles/voice-library.

### Add a tool to the agent
Add a method to the `Assistant` class in `backend/src/agent.py` with the `@function_tool` decorator. There's a commented example (weather lookup) in the file. Import `function_tool` and `RunContext` from `livekit.agents`.

### Switch the LLM
Replace the `llm=google.LLM(...)` call in `agent.py`. For OpenAI: install `livekit-agents[openai]`, set `OPENAI_API_KEY`, import `openai` from `livekit.plugins`, and use `openai.LLM(...)`.

### Change frontend branding
Edit `frontend/app-config.ts` — company name, page title, logo paths, accent colors, button text, visualizer type.

## Documentation references

- Murf Falcon TTS: https://murf.ai/api/docs/text-to-speech/streaming
- Murf Voice Library: https://murf.ai/api/docs/voices-styles/voice-library
- LiveKit Agents SDK: https://docs.livekit.io/agents
- LiveKit Agents UI: https://livekit.io/ui
- Deepgram STT: https://developers.deepgram.com
