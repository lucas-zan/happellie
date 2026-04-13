import { useMemo, useState } from 'react';
import type { TemplateProps } from '../../engine/types';
import { Button } from '../../components/Button';
import { Pill } from '../../components/primitives/Pill';
import { apiClient } from '../../api/client';
import { SvgEllie } from '../common/svg';

export function FeedPetStep({ step, onComplete, audio, runtime }: TemplateProps) {
  const available = (step.slots.available_food || {}) as Record<string, unknown>;
  const choices = useMemo(() => Object.entries(available).filter(([, v]) => Number(v ?? 0) > 0), [available]);
  const [picked, setPicked] = useState<string | null>(choices[0]?.[0] ?? null);
  const [busy, setBusy] = useState(false);
  const [hint, setHint] = useState('');
  const [petMood, setPetMood] = useState<string>('neutral');
  const [feeding, setFeeding] = useState(false);

  async function runFeed() {
    if (!runtime?.studentId || !picked || busy) return;
    setBusy(true);
    setHint('');
    setFeeding(true);
    const details: Record<string, unknown> = { picked_food: picked, before_slots: available };
    try {
      let pet = await apiClient.getPet(runtime.studentId);
      let beforeCount = Number(pet.food_inventory?.[picked] ?? 0);
      if (beforeCount <= 0) {
        const buy = await apiClient.buyFood({ student_id: runtime.studentId, food_type: picked, quantity: 1 });
        details.shop_status = buy.status;
        details.shop_spent_coins = buy.spent_coins;
        if (buy.status !== 'ok') {
          audio.playSfx('wrong');
          setPetMood('sad');
          setHint('Not enough coins to buy food.');
          onComplete({
            step_id: step.step_id,
            template_id: step.template_id,
            correct: false,
            score: 0,
            duration_ms: 1600,
            details,
          });
          return;
        }
        pet = buy.pet;
        beforeCount = Number(pet.food_inventory?.[picked] ?? 0);
      }
      const fed = await apiClient.feedPet({ student_id: runtime.studentId, food_type: picked, quantity: 1 });
      details.feed_status = fed.status;
      details.inventory_before = beforeCount;
      details.inventory_after = Number(fed.pet.food_inventory?.[picked] ?? 0);
      details.pet_hunger = fed.pet.hunger;
      details.pet_affection = fed.pet.affection;
      if (fed.status !== 'ok') {
        audio.playSfx('wrong');
        setPetMood('sad');
        setHint('No food available to feed.');
        onComplete({
          step_id: step.step_id,
          template_id: step.template_id,
          correct: false,
          score: 0,
          duration_ms: 1600,
          details,
        });
        return;
      }
      audio.playSfx('cheer');
      setPetMood('happy');
      setHint(`Ellie is happy! Hunger ${fed.pet.hunger}, coins ${fed.pet.coins}.`);
      onComplete({
        step_id: step.step_id,
        template_id: step.template_id,
        correct: true,
        score: 20,
        duration_ms: 1600,
        details,
      });
    } catch (error) {
      audio.playSfx('wrong');
      setPetMood('sad');
      setHint((error as Error).message);
      onComplete({
        step_id: step.step_id,
        template_id: step.template_id,
        correct: false,
        score: 0,
        duration_ms: 1600,
        details: { ...details, error: (error as Error).message },
      });
    } finally {
      setBusy(false);
      setTimeout(() => setFeeding(false), 600);
    }
  }

  return (
    <div className="tpl-feed">
      <div className="tpl-feed__header">
        <Pill tone="brand">Feed Ellie</Pill>
      </div>

      <div className={`tpl-feed__pet-visual ${feeding ? 'is-munching' : ''}`}>
        <SvgEllie mood={petMood} size={100} />
      </div>

      <p className="tpl-feed__prompt">Choose food to feed Ellie.</p>

      <div className="tpl-feed__options">
        {choices.length ? (
          choices.map(([foodType, qty]) => (
            <button
              key={foodType}
              className={`tpl-feed__option ${picked === foodType ? 'is-selected' : ''}`}
              onClick={() => {
                audio.playSfx('tap');
                setPicked(foodType);
              }}
            >
              <strong>{foodType}</strong>
              <span>x{Number(qty ?? 0)}</span>
            </button>
          ))
        ) : (
          <div className="tpl-feed__empty">No food yet. You can still continue.</div>
        )}
      </div>

      <div className="tpl-feed__actions">
        <Button size="lg" variant="primary" onClick={runFeed} disabled={!picked || busy}>
          {busy ? 'Feeding...' : 'Feed'}
        </Button>
      </div>
      {hint ? <p className="tpl-feed__hint">{hint}</p> : null}
    </div>
  );
}
