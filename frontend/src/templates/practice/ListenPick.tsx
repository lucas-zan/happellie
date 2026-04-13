import { useMemo, useState } from 'react';
import type { TemplateProps } from '../../engine/types';
import { Button } from '../../components/Button';
import { Pill } from '../../components/primitives/Pill';

type Option = { key?: string; image_hint?: string };

function optionEmoji(key: string) {
  const k = (key || '').toLowerCase();
  if (k.includes('apple')) return '🍎';
  if (k.includes('banana')) return '🍌';
  if (k.includes('carrot')) return '🥕';
  if (k.includes('milk')) return '🥛';
  if (k.includes('bread')) return '🍞';
  if (k.includes('juice')) return '🧃';
  if (k.includes('ball')) return '⚽️';
  return '⭐️';
}

export function ListenPick({ step, onComplete, audio }: TemplateProps) {
  const audioText = String(step.slots.audio_text || '');
  const correctKey = String(step.slots.correct_key || '');
  const character = (step.slots.character || {}) as Record<string, unknown>;
  const line = String(character.line || 'Listen and pick!');
  const options = useMemo(() => (Array.isArray(step.slots.options) ? (step.slots.options as Option[]) : []), [step]);

  const [selected, setSelected] = useState<string | null>(null);
  const [locked, setLocked] = useState(false);

  function finish(picked: string) {
    const correct = picked === correctKey;
    if (correct) audio.playSfx('correct');
    else audio.playSfx('wrong');
    window.setTimeout(() => {
      onComplete({
        step_id: step.step_id,
        template_id: step.template_id,
        correct,
        score: correct ? 25 : 0,
        duration_ms: 2200,
        details: { selected_key: picked, correct_key: correctKey, audio_text: audioText },
      });
    }, 650);
  }

  return (
    <div className="tpl-listen-pick">
      <div className="tpl-listen-pick__header">
        <Pill tone="warning">Listen</Pill>
        <span className="tpl-listen-pick__line">{line}</span>
      </div>

      <div className="tpl-listen-pick__listen">
        <Button
          size="lg"
          variant="secondary"
          onClick={() => {
            audio.playSfx('tap');
            audio.playTts(audioText);
          }}
        >
          🔊 Play
        </Button>
        <Pill tone="neutral">Pick the right one</Pill>
      </div>

      <div className="tpl-listen-pick__grid">
        {options.map((opt, index) => {
          const key = String(opt.key || '');
          const isSelected = selected === key;
          const isCorrect = locked && key === correctKey;
          const isWrong = locked && isSelected && key !== correctKey;
          return (
            <button
              key={`${step.step_id}-${key}-${index}`}
              className={`tpl-listen-pick__option ${isSelected ? 'is-selected' : ''} ${isCorrect ? 'is-correct' : ''} ${isWrong ? 'is-wrong' : ''}`}
              disabled={locked}
              onClick={() => {
                if (locked) return;
                audio.playSfx('tap');
                setSelected(key);
                setLocked(true);
                finish(key);
              }}
              style={{ ['--i' as never]: index } as never}
            >
              <span className="tpl-listen-pick__emoji" aria-hidden="true">
                {optionEmoji(key)}
              </span>
              <span className="tpl-listen-pick__label">{key}</span>
            </button>
          );
        })}
      </div>

      {locked ? (
        <p className={`tpl-listen-pick__feedback ${selected === correctKey ? 'ok' : 'no'}`}>
          {selected === correctKey ? String(step.slots.success_line || 'Great job!') : String(step.slots.fail_line || 'Try again!')}
        </p>
      ) : null}
    </div>
  );
}

