# HappyEllie Runnable AI Game Prototype

HappyEllie is a lightweight pet-based English learning game prototype.
This repo is designed for **fast experimentation with real AI providers** while
keeping every capability behind simple, swappable interfaces.

## Core principles

- **Abstract**: domain services depend on interfaces, not vendor SDKs.
- **Simple**: local-first, SQLite + file storage, one Python backend, one React client.
- **Extensible**: lesson planning, lesson generation, profile analysis, TTS, analytics,
  repositories, and UI blocks can all be replaced independently.

## What this version already does

- uses a **real OpenAI-compatible model pipeline** once you configure your own model
- supports a two-stage content flow: **lesson planning -> final lesson package generation**
- generates a **page-based mini game package** instead of a flat lesson preview
- renders a whitelisted set of **game pages and game components** in the frontend
- carries a **story thread** across lessons with recap, mission, and next hook
- introduces **helper animals and soft monster encounters** in the lesson flow
- updates the learner profile after each session using **AI profile analysis**
- keeps pet state independent from lesson generation
- records trial usage and AI cost metadata for the admin panel
- stays runnable without a model when `AI_ENABLE_FALLBACK=true`

## Current product shape

The current playable loop is:

1. choose a few vocabulary items
2. generate a story-driven lesson package
3. play through page-based mini game screens
4. save rewards and update the learner profile
5. feed Ellie with earned food

The current page flow is:

- `hero`
- `learn`
- `quiz`
- `repeat`
- `settlement`
- `feed_pet`

The package is generated as **structured JSON**, not model-generated HTML or frontend code.
The frontend renders only known page and component types.

## Stack

- **Client**: Tauri + React + TypeScript + Vite
- **Backend**: Python + FastAPI
- **Database**: SQLite
- **Vocab library**: JSON file at `backend/config/vocab_library.json`
- **AI transport**: generic OpenAI-compatible chat completion client

## Quick start

### 1) Bootstrap

```bash
./scripts/bootstrap.sh
```

### 2) Configure your model

Edit `backend/.env` and fill:

```env
AI_API_KEY=your_key
AI_BASE_URL=your_openai_compatible_base_url
AI_DEFAULT_MODEL=your_model_name
```

Optional per-stage overrides:

```env
AI_PLANNER_MODEL=...
AI_GENERATOR_MODEL=...
AI_PROFILE_MODEL=...
```

### 3) Run backend

```bash
./scripts/run_backend.sh
```

Backend docs: `http://127.0.0.1:8000/docs`

### 4) Run frontend

```bash
./scripts/run_frontend_web.sh
```

Frontend: `http://127.0.0.1:5173`

### 5) Optional one-command local run

```bash
./scripts/run_local_app.sh
```

Or use the root Makefile:

```bash
make dev
```

## Default trial flow

1. Open **Lesson**.
2. Generate a lesson for `student-demo`.
3. Play through the story pages and complete the lesson.
4. Open **Pet** and feed Ellie.
5. Open **Admin** to inspect sessions, AI calls, and tracked costs.

## Main backend modules

- `LessonService`
  - loads vocab and current profile
  - plans a lesson blueprint
  - generates the final `LessonPackage`
  - caches stable lesson packages
- `SessionService`
  - stores session results
  - updates rewards
  - recomputes learner profile
- `AdminService`
  - summarizes usage and AI cost statistics

## Interface-first modules

- `StructuredLLMClient`
- `LessonPlanner`
- `LessonGenerator`
- `ProfileAnalyzer`
- `VocabRepository`
- `TextToSpeechProvider`
- repositories for sessions, pets, content cache

## Important runtime notes

- The backend expects an **OpenAI-compatible** `/chat/completions` endpoint.
- TTS is disabled by default. You can keep it disabled.
- If `AI_ENABLE_FALLBACK=false`, AI failures will surface directly instead of falling back.

## Smoke test

After bootstrap:

```bash
./scripts/smoke_test.sh
```

## Suggested first real provider configs

- **Alibaba / DashScope / Qwen-compatible**
  - `AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1`
- **ByteDance / Volcano Ark / OpenAI-compatible endpoint**
  - fill in your own Ark base URL and model name from the control panel

## Future extension points

See [docs/STATUS_AND_NEXT_STEPS.md](/Users/lucas/Documents/products/happyellie/docs/STATUS_AND_NEXT_STEPS.md:1) for the active status and next tasks.

The highest-priority next steps are:

- fixed visual asset system for Ellie, helper animals, and monsters
- richer game interactions such as drag, listen-pick, and collectible moments
- stronger pet growth units and persistent avatar state
- real TTS provider and audio playback experience
- finer-grained event logging and profile recompute jobs
