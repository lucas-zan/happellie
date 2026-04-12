# HappyEllie Implementation Notes

## Current scope

This repo implements a runnable local prototype for the first HappyEllie loop:

1. request a lesson package from a small vocabulary list
2. render the package as page-based mini game screens in the frontend
3. complete the session and save rewards
4. inspect pet state and feed Ellie
5. inspect trial metrics and cost tracking in the admin panel

## Intentional architectural boundaries

- `LessonGenerator` hides the AI provider choice.
- `TextToSpeechProvider` hides the TTS vendor choice.
- repository interfaces hide SQLite details from services.
- frontend pages only talk to typed API contracts.
- `LessonPackage` is the stable UI contract between backend and frontend.
- the frontend renders a whitelist of page and component types instead of model-generated code.

## Local-first behavior

- If `QWEN_API_KEY` is not configured, lesson generation falls back to a deterministic local lesson.
- Mock TTS creates text files under `backend/data/assets/audio/` and returns `/assets/...` URLs.
- All state lives in SQLite and local files, so the prototype works offline except for optional remote model calls.

## Next recommended extensions

- add richer lesson block types and renderer components
- add more page/component types beyond the initial page-based mini game flow
- add real Aliyun / Doubao TTS providers under `backend/app/infra/tts/`
- add richer profile summarization and next-lesson planning
- add a student summary endpoint and page
- wire real audio playback once a real TTS provider is connected
