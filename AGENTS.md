# AGENTS

## Purpose

This project is built for fast product validation. Every design and implementation decision should optimize for:

- abstract boundaries
- concise modules
- easy extension
- fast replacement of implementations
- low-cost experimentation

Do not couple product flows to a single provider, renderer, rule set, storage layer, or AI vendor unless there is no practical alternative.

## Core Principles

### 1. Interface-first design

All core feature modules must be designed around interfaces or stable contracts first.

Examples:

- lesson planning depends on a planner interface, not a specific model SDK
- lesson generation depends on a package generator interface, not a prompt implementation
- pet state depends on a repository interface, not a specific database
- audio depends on a TTS interface, not a single provider
- frontend rendering depends on a page/component contract, not model-generated code

If an implementation changes later, the calling layer should not need a rewrite.

### 2. Keep modules small and replaceable

Each module should do one clear job.

Good:

- `LessonPlanner`
- `LessonGenerator`
- `ProfileAnalyzer`
- `PetRepository`
- `TextToSpeechProvider`

Bad:

- one service that selects vocab, calls models, writes DB, renders UI payloads, and updates pet growth in one place

### 3. Prefer stable contracts over implicit behavior

Use explicit schemas and typed payloads between layers.

Examples:

- backend returns validated `LessonPackage`
- frontend renders only known page and component types
- session events use typed payloads
- pet updates are driven by structured state, not ad hoc UI logic

Avoid hidden assumptions spread across files.

### 4. Separate policy from implementation

Business decisions should be isolated from transport and provider logic.

Examples:

- recommendation strategy should not depend on one model vendor
- growth rules should not be embedded inside UI components
- cache policy should not be embedded inside route handlers

Keep these concerns independently swappable.

### 5. Optimize for rapid trial-and-error

The architecture should make it easy to:

- replace rules with model implementations
- replace one model with another
- replace mock audio with real audio
- replace local SQLite with another repository implementation
- expand page/component types without rewriting the full stack

When in doubt, choose the option that reduces rewrite cost for future experiments.

## Backend Guidance

- Keep route handlers thin.
- Put orchestration in services.
- Put vendor-specific logic behind interfaces.
- Put persistence behind repository interfaces.
- Keep prompt logic isolated from domain logic.
- Validate all model outputs before using them.
- Do not let AI return arbitrary frontend code or HTML.
- Generate structured lesson/page data, then render it through the frontend contract.

## Frontend Guidance

- Treat backend lesson data as a stable rendering contract.
- Render only whitelisted page and component types.
- Keep page orchestration separate from presentation components.
- Keep gameplay state separate from reusable UI primitives.
- Do not hardcode backend business rules into page components.

## Pet System Guidance

- Pet identity is a long-lived asset and must remain independent from lesson generation.
- Lessons may produce rewards and state-change intents, but must not redefine pet appearance.
- Growth should be incremental and state-driven.
- The UI should derive visuals from persisted pet state, not from generated lesson content.

## Definition of Done

A feature is not complete unless:

- the contract boundary is clear
- implementation details are replaceable
- the module remains concise
- downstream code is not tightly coupled to one implementation
- the result can support rapid future iteration

## Default Decision Rule

When choosing between two implementations, prefer the one that is:

1. more abstract
2. simpler to reason about
3. easier to swap later
4. safer for fast experimentation
