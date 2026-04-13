import type { TemplateProps } from '../../engine/types';
import { Button } from '../../components/Button';
import { Pill } from '../../components/primitives/Pill';
import { SvgEllie } from '../common/svg';

export function EpisodeEnd({ step, onComplete, audio }: TemplateProps) {
  const summary = String(step.slots.episode_summary || 'Great job today!');
  const nextHook = String(step.slots.next_hook || '');
  const nextHint = String(step.slots.next_episode_hint || '');
  const chapterKey = String(step.slots.chapter_key || '');
  const petImpact = (step.slots.pet_impact || {}) as Record<string, unknown>;

  return (
    <div className="tpl-end">
      <div className="tpl-end__header">
        <Pill tone="warning">Episode Complete</Pill>
        <div className="tpl-end__stars-row" aria-hidden="true">
          <span className="anim-star-spin">⭐️</span>
          <span className="anim-star-spin" style={{ animationDelay: '0.15s' }}>⭐️</span>
          <span className="anim-star-spin" style={{ animationDelay: '0.3s' }}>⭐️</span>
        </div>
      </div>

      <div className="tpl-end__hero">
        <SvgEllie mood="happy" size={80} />
      </div>

      <div className="tpl-end__panel">
        <h3 className="tpl-end__title">You did it!</h3>
        <p className="tpl-end__summary">{summary}</p>
        {nextHook ? (
          <p className="tpl-end__hook">
            <strong>Next time:</strong> {nextHook}
          </p>
        ) : null}
        {nextHint ? <p className="tpl-end__hint">{nextHint}</p> : null}
        {chapterKey ? <p className="tpl-end__hint">Chapter: {chapterKey}</p> : null}
        {petImpact && Object.keys(petImpact).length ? (
          <div className="tpl-end__pet-impact">
            <strong>Pet update</strong>
            <span>
              Hunger {String(petImpact.pet_hunger ?? '-')} · Affection{' '}
              {String(petImpact.pet_affection ?? '-')} · Food left{' '}
              {String(petImpact.inventory_after ?? '-')}
            </span>
          </div>
        ) : null}
      </div>

      <div className="tpl-end__actions">
        <Button
          size="lg"
          variant="primary"
          onClick={() => {
            audio.playSfx('cheer');
            onComplete({
              step_id: step.step_id,
              template_id: step.template_id,
              correct: null,
              score: 15,
              duration_ms: 1400,
              details: { summary, nextHook, nextHint },
            });
          }}
        >
          Finish
        </Button>
      </div>
    </div>
  );
}
