import type { LessonComponent, LessonPage, SessionBlockResult } from '../api/types';
import { Button } from '../components/Button';
import { Card, CardContent, CardDescription, CardTitle } from '../components/Card';
import { Pill } from '../components/primitives/Pill';

type Props = {
  page: LessonPage;
  results: Record<string, SessionBlockResult>;
  onResult: (result: SessionBlockResult) => void;
};

function emotionEmoji(emotion: unknown) {
  const value = String(emotion || '').toLowerCase();
  if (value.includes('hungry')) return '🍎';
  if (value.includes('curious')) return '👀';
  if (value.includes('excited')) return '✨';
  if (value.includes('happy')) return '😄';
  return '🐰';
}

function HeroBanner({ component }: { component: LessonComponent }) {
  return (
    <div className="game-component game-component--hero">
      <div className="game-hero-banner">
        <Pill tone="brand">Mission</Pill>
        <h3 className="game-hero-banner__title">{component.title}</h3>
        <p className="game-hero-banner__prompt">{component.prompt}</p>
      </div>
    </div>
  );
}

function StoryPanel({ component }: { component: LessonComponent }) {
  return (
    <div className="game-component">
      <div className="game-story-panel">
        <Pill tone="warning">Story</Pill>
        <h3 className="game-choice-card__title">{component.title}</h3>
        <p className="game-choice-card__prompt">{String(component.payload.recap || component.prompt)}</p>
        <div className="game-story-panel__mission">
          <strong>Mission</strong>
          <span>{String(component.payload.mission || '')}</span>
        </div>
      </div>
    </div>
  );
}

function EncounterCard({ component }: { component: LessonComponent }) {
  return (
    <div className="game-component">
      <div className="game-encounter-card">
        <div className="game-encounter-card__icons" aria-hidden="true">
          <span>🦊</span>
          <span>⚔️</span>
          <span>👾</span>
        </div>
        <div className="game-encounter-card__copy">
          <strong>{component.title}</strong>
          <span>{component.prompt}</span>
          <p>{String(component.payload.challenge || '')}</p>
        </div>
      </div>
    </div>
  );
}

function WordCardGroup({ component }: { component: LessonComponent }) {
  const items = Array.isArray(component.payload.items) ? component.payload.items as Array<Record<string, unknown>> : [];
  return (
    <div className="game-component">
      <div className="game-word-grid">
        {items.map((item, index) => (
          <article key={`${component.component_id}-${index}`} className="game-word-card">
            <strong>{String(item.word || '')}</strong>
            <span>{String(item.meaning || '')}</span>
          </article>
        ))}
      </div>
    </div>
  );
}

function ChoiceQuiz({
  component,
  result,
  onResult,
}: {
  component: LessonComponent;
  result?: SessionBlockResult;
  onResult: (result: SessionBlockResult) => void;
}) {
  const options = Array.isArray(component.payload.options) ? component.payload.options as string[] : [];
  const answer = String(component.payload.answer || '');

  return (
    <div className="game-component">
      <div className="game-choice-card">
        <h3 className="game-choice-card__title">{component.title}</h3>
        <p className="game-choice-card__prompt">{String(component.payload.question || component.prompt)}</p>
        <div className="game-choice-grid">
          {options.map((option) => {
            const isChosen = Boolean(result && option === answer);
            return (
              <Button
                key={option}
                variant={isChosen ? (result?.correct ? 'primary' : 'soft') : 'secondary'}
                size="lg"
                onClick={() =>
                  onResult({
                    block_id: component.component_id,
                    block_type: component.type,
                    correct: option === answer,
                    score: option === answer ? 25 : 0,
                    duration_ms: 2500,
                  })
                }
              >
                {option}
              </Button>
            );
          })}
        </div>
        {result ? (
          <p className={`game-feedback ${result.correct ? 'game-feedback--success' : 'game-feedback--warning'}`}>
            {result.correct ? 'Correct. Ellie found the snack.' : `Try again next time. The answer is ${answer}.`}
          </p>
        ) : null}
      </div>
    </div>
  );
}

function RepeatPrompt({
  component,
  result,
  onResult,
}: {
  component: LessonComponent;
  result?: SessionBlockResult;
  onResult: (result: SessionBlockResult) => void;
}) {
  return (
    <div className="game-component">
      <div className="game-repeat-card">
        <h3 className="game-choice-card__title">{component.title}</h3>
        <p className="game-repeat-card__text">{String(component.payload.text || component.prompt)}</p>
        <Button
          variant={result ? 'primary' : 'secondary'}
          size="lg"
          onClick={() =>
            onResult({
              block_id: component.component_id,
              block_type: component.type,
              correct: true,
              score: 15,
              duration_ms: 2000,
            })
          }
        >
          {result ? 'Done' : 'I said it'}
        </Button>
      </div>
    </div>
  );
}

function RewardPanel({ component }: { component: LessonComponent }) {
  return (
    <div className="game-component">
      <div className="ui-reward-grid">
        <div className="ui-reward-item">
          <span>Coins</span>
          <strong>{Number(component.payload.coins ?? 0)}</strong>
        </div>
        <div className="ui-reward-item">
          <span>Food</span>
          <strong>{Number(component.payload.food ?? 0)}</strong>
        </div>
      </div>
    </div>
  );
}

function FeedPanel({ component }: { component: LessonComponent }) {
  return (
    <div className="game-component">
      <div className="game-feed-card">
        <h3 className="game-choice-card__title">{component.title}</h3>
        <p className="game-choice-card__prompt">{component.prompt}</p>
        <div className="ui-meta-row">
          <Pill tone="success">{String(component.payload.food_type || 'basic_food')}</Pill>
          <Pill tone="warning">x{Number(component.payload.quantity ?? 1)}</Pill>
        </div>
      </div>
    </div>
  );
}

function PetReaction({ component }: { component: LessonComponent }) {
  return (
    <div className="game-component">
      <div className="game-pet-reaction">
        <span className="game-pet-reaction__emoji" aria-hidden="true">
          {emotionEmoji(component.payload.emotion)}
        </span>
        <div className="game-pet-reaction__copy">
          <strong>{component.title}</strong>
          <span>{component.prompt}</span>
        </div>
      </div>
    </div>
  );
}

function renderComponent(
  component: LessonComponent,
  result: SessionBlockResult | undefined,
  onResult: (result: SessionBlockResult) => void,
) {
  switch (component.type) {
    case 'hero_banner':
      return <HeroBanner component={component} />;
    case 'story_panel':
      return <StoryPanel component={component} />;
    case 'encounter_card':
      return <EncounterCard component={component} />;
    case 'word_card':
      return <WordCardGroup component={component} />;
    case 'choice_quiz':
      return <ChoiceQuiz component={component} result={result} onResult={onResult} />;
    case 'repeat_prompt':
      return <RepeatPrompt component={component} result={result} onResult={onResult} />;
    case 'reward_panel':
      return <RewardPanel component={component} />;
    case 'feed_panel':
      return <FeedPanel component={component} />;
    case 'pet_reaction':
      return <PetReaction component={component} />;
    default:
      return null;
  }
}

export function PageRenderer({ page, results, onResult }: Props) {
  const tone = page.page_type === 'hero' ? 'hero' : page.page_type === 'settlement' || page.page_type === 'feed_pet' ? 'reward' : 'default';

  return (
    <Card tone={tone} className="game-page-card">
      <CardContent className="game-page-card__content">
        <div className="game-page-card__header">
          <div>
            <Pill tone="neutral">{page.page_type}</Pill>
            <CardTitle>{page.title}</CardTitle>
          </div>
          <CardDescription>{page.instruction}</CardDescription>
        </div>
        <div className="game-page-card__body">
          {page.components.map((component) => (
            <div key={component.component_id}>
              {renderComponent(component, results[component.component_id], onResult)}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
