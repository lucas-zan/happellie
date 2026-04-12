# HappyEllie Implementation Notes

## Current scope

This repo implements a runnable local prototype for the first HappyEllie loop:

1. request a lesson package from a small vocabulary list
2. render the package as page-based mini game screens in the frontend
3. complete the session and save rewards
4. inspect pet state and feed Ellie
5. inspect trial metrics and cost tracking in the admin panel

## Completed work

- page-based `LessonPackage` contract replaced the earlier flat block preview
- frontend now renders page and component whitelists instead of lesson blocks
- story metadata is now part of lesson generation
- lesson story continuity is written back into the learner profile after completion
- helper-animal and soft-monster encounter components are part of the lesson flow
- lesson completion can save rewards and immediately feed Ellie

## Current boundaries

The project now supports:

- structured JSON lesson generation
- page-based mini game rendering
- simple story continuation between lessons
- pet state stored independently from lesson generation

The project still does not support:

- fixed illustration assets for Ellie and other characters
- complex branching story logic
- richer interactive mechanics like drag-and-drop or listen-pick
- real audio playback with a production TTS provider
- background jobs for slower profile recompute passes

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

- add fixed character asset keys and layered visual rendering for Ellie, helper animals, and monsters
- add more page/component types beyond the initial page-based mini game flow
- add richer interaction types such as drag match, listen pick, and collectible reward beats
- add real Aliyun / Doubao TTS providers under `backend/app/infra/tts/`
- add finer-grained event logging and slower profile recompute jobs
- add richer profile summarization and next-lesson planning
- add a student summary endpoint and page
- wire real audio playback once a real TTS provider is connected
