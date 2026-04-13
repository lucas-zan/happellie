import { useMemo, useState } from 'react';
import type { GameStep, StepResult } from './types';
import { getTemplate } from './TemplateRegistry';
import { GameHUD } from './GameHUD';
import { useAudio } from './useAudio';

export function GameEngine({
  lessonId,
  studentId,
  steps,
  onFinish,
}: {
  lessonId: string;
  studentId: string;
  steps: GameStep[];
  onFinish: (payload: {
    lesson_id: string;
    session_id: string;
    student_id: string;
    results: StepResult[];
    coins: number;
    events: Array<Record<string, unknown>>;
  }) => void;
}) {
  const [sessionId] = useState(() => `sess-${Math.random().toString(36).slice(2, 10)}`);
  const audio = useAudio();
  const [stepIndex, setStepIndex] = useState(0);
  const [coins, setCoins] = useState(0);
  const [results, setResults] = useState<StepResult[]>([]);
  const [events, setEvents] = useState<Array<Record<string, unknown>>>([]);
  const [transitioning, setTransitioning] = useState(false);
  const [petImpact, setPetImpact] = useState<Record<string, unknown> | null>(null);
  const [coinBounce, setCoinBounce] = useState(false);

  const rawStep = steps[stepIndex] ?? null;
  const step =
    rawStep && rawStep.template_id === 'episode_end' && petImpact
      ? { ...rawStep, slots: { ...rawStep.slots, pet_impact: petImpact } }
      : rawStep;
  const Template = step ? getTemplate(step.template_id) : null;

  const canFinish = stepIndex >= steps.length - 1;

  const sceneClass = useMemo(() => {
    if (!step) return '';
    if (step.template_id === 'reward_chest' || step.template_id === 'episode_end') return 'game-stage--reward';
    if (step.template_id === 'choice_battle') return 'game-stage--battle';
    if (step.template_id === 'feed_pet_step') return 'game-stage--feed';
    return '';
  }, [step]);

  function handleComplete(result: StepResult) {
    const event = {
      event_id: `evt-${Math.random().toString(36).slice(2, 10)}`,
      session_id: sessionId,
      student_id: studentId,
      lesson_id: lessonId,
      step_id: result.step_id,
      template_id: result.template_id,
      event_type: 'step_completed',
      payload: { correct: result.correct, score: result.score, details: result.details },
      timestamp: new Date().toISOString(),
    };
    const nextResults = [...results, result];
    const nextEvents = [...events, event];
    setResults(nextResults);
    setEvents(nextEvents);
    if (result.template_id === 'feed_pet_step') {
      setPetImpact({
        inventory_after: result.details.inventory_after ?? 0,
        pet_hunger: result.details.pet_hunger ?? null,
        pet_affection: result.details.pet_affection ?? null,
        feed_status: result.details.feed_status ?? '',
      });
    }
    const delta = Number(step?.reward_on_complete?.coins ?? 0);
    const nextCoins = delta > 0 && result.correct ? coins + delta : coins;
    if (delta > 0 && result.correct) {
      setCoins((c) => c + delta);
      setCoinBounce(true);
      audio.playSfx('coin');
      setTimeout(() => setCoinBounce(false), 500);
    }

    if (canFinish) {
      onFinish({
        lesson_id: lessonId,
        session_id: sessionId,
        student_id: studentId,
        results: nextResults,
        coins: nextCoins,
        events: nextEvents,
      });
      return;
    }

    setTransitioning(true);
    audio.playSfx('whoosh');
    window.setTimeout(() => {
      setStepIndex((i) => Math.min(steps.length - 1, i + 1));
      setTransitioning(false);
    }, 300);
  }

  if (!step || !Template) {
    return (
      <div className="game-empty">
        <h3>No playable steps</h3>
        <p>Backend did not return template steps yet.</p>
      </div>
    );
  }

  return (
    <div className="game-engine game-immersive">
      <GameHUD stepIndex={stepIndex} totalSteps={steps.length} coins={coins} />
      {coinBounce && <div className="game-coin-fly" aria-hidden="true">💰</div>}
      <div className={`game-stage ${sceneClass} ${transitioning ? 'game-stage--exit' : 'game-stage--enter'}`}>
        <div className="game-stage__content">
          <Template step={step} onComplete={handleComplete} audio={audio} runtime={{ studentId, lessonId }} />
        </div>
        <div className="game-stage__controls">
          <button
            className="ui-button ui-button--ghost ui-button--sm"
            onClick={() =>
              handleComplete({
                step_id: step.step_id,
                template_id: step.template_id,
                correct: null,
                score: 0,
                duration_ms: 800,
                details: { skipped: true },
              })
            }
          >
            Skip →
          </button>
        </div>
      </div>
    </div>
  );
}
