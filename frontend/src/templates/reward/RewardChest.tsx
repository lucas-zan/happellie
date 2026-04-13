import { useState } from 'react';
import type { TemplateProps } from '../../engine/types';
import { Pill } from '../../components/primitives/Pill';
import { Button } from '../../components/Button';

export function RewardChest({ step, onComplete, audio }: TemplateProps) {
  const coins = Number(step.slots.total_coins ?? 0);
  const food = step.slots.total_food as Record<string, unknown> | undefined;
  const foods = food ? Object.entries(food).map(([k, v]) => `${k} x${Number(v ?? 0)}`) : [];
  const [opened, setOpened] = useState(false);

  function reveal() {
    if (opened) return;
    setOpened(true);
    audio.playSfx('cheer');
  }

  return (
    <div className="tpl-chest">
      <div className="tpl-chest__header">
        <Pill tone="warning">Rewards</Pill>
      </div>

      <button className={`tpl-chest__box ${opened ? 'is-opened' : ''}`} onClick={reveal} aria-label="Open chest">
        <div className={`tpl-chest__lid ${opened ? 'is-open' : ''}`}>🧰</div>
        {opened && (
          <>
            <div className="tpl-chest__burst" aria-hidden="true">✨</div>
            <div className="tpl-chest__rays" aria-hidden="true" />
          </>
        )}
      </button>

      <div className={`tpl-chest__grid ${opened ? 'is-revealed' : ''}`}>
        <div className="tpl-chest__item">
          <span>Coins</span>
          <strong className={opened ? 'anim-coin-pop' : ''}>💰 {coins}</strong>
        </div>
        <div className="tpl-chest__item">
          <span>Food</span>
          <strong className={opened ? 'anim-coin-pop' : ''}>{foods.length ? foods.join(' · ') : 'basic_food x0'}</strong>
        </div>
      </div>

      <div className="tpl-chest__actions">
        <Button
          size="lg"
          variant="primary"
          disabled={!opened}
          onClick={() => {
            audio.playSfx('whoosh');
            onComplete({
              step_id: step.step_id,
              template_id: step.template_id,
              correct: null,
              score: 10,
              duration_ms: 1300,
              details: { coins, foods },
            });
          }}
        >
          Continue
        </Button>
      </div>
    </div>
  );
}
