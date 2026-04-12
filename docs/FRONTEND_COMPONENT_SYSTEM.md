# Frontend Component System

The frontend now follows two layers of reusable UI:

## 1. Primitive shared UI

These components define the visual language and should stay platform-neutral:

- `Button`
- `Card`
- `Field`
- `PageHeader`
- `StatCard`
- `StatusMessage`
- `EmptyState`
- `MetricList`
- `Pill`
- `ProgressBar`
- `KeyValueGrid`

They rely only on the local stylesheet tokens in `styles.css` and do not depend on page logic.

## 2. Business-level shared UI

These components package repeated product flows:

### Lesson
- `LessonRequestForm`
- `LessonSummaryCard`
- `SessionFeedbackCard`
- `LessonActionBar`

### Pet
- `PetAvatarCard`
- `PetStatsPanel`
- `PetCarePanel`

### Admin
- `AdminSummaryGrid`
- `AdminBreakdownPanel`

## 3. Renderer-level game modules

The lesson experience now uses a page renderer plus whitelisted component renderers:

- `PageRenderer`
- `hero_banner`
- `word_card`
- `choice_quiz`
- `repeat_prompt`
- `reward_panel`
- `feed_panel`
- `pet_reaction`

This keeps gameplay rendering contract-driven instead of relying on model-generated UI code.

## Design rule

Pages should orchestrate data loading and actions only.

- Visual consistency belongs in primitives.
- Repeated product flows belong in business components.
- Lesson page and component mapping belongs in renderer modules.

This keeps Web and desktop rendering aligned because the app uses its own component system rather than page-local styling.
