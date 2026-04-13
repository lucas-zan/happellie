import { useMemo, useState } from 'react';
import type { TemplateProps } from '../../engine/types';
import { Button } from '../../components/Button';
import { Pill } from '../../components/primitives/Pill';
import { resolveCharacterAsset } from '../common/characterRegistry';

type Round = { question?: string; options?: string[]; answer?: string; round_type?: string };

export function ChoiceBattle({ step, onComplete, audio }: TemplateProps) {
  const monster = (step.slots.monster || {}) as Record<string, unknown>;
  const name = String(monster.name || 'Monster');
  const hpTotal = Math.max(1, Math.min(5, Number(monster.hp ?? 3)));

  const rounds = useMemo(() => (Array.isArray(step.slots.rounds) ? (step.slots.rounds as Round[]) : []), [step]);
  const [roundIndex, setRoundIndex] = useState(0);
  const [hp, setHp] = useState(hpTotal);
  const [correctCount, setCorrectCount] = useState(0);
  const [locked, setLocked] = useState(false);
  const [feedback, setFeedback] = useState<string>('');
  const [hitAnim, setHitAnim] = useState(false);
  const [showStars, setShowStars] = useState(false);

  const round = rounds[roundIndex] ?? { question: 'Pick the right answer!', options: [], answer: '' };
  const options = Array.isArray(round.options) ? round.options : [];
  const answer = String(round.answer || '');

  const monsterAsset = resolveCharacterAsset(name);
  const MonsterSvg = monsterAsset.SvgComponent;

  function finish() {
    const victory = hp <= 0;
    audio.playSfx(victory ? 'cheer' : 'wrong');
    window.setTimeout(() => {
      onComplete({
        step_id: step.step_id,
        template_id: step.template_id,
        correct: victory,
        score: victory ? 60 : Math.max(0, correctCount * 10),
        duration_ms: 4200,
        details: { rounds_correct: correctCount, rounds_total: rounds.length, victory },
      });
    }, 700);
  }

  function onPick(option: string) {
    if (locked) return;
    setLocked(true);
    const isCorrect = option === answer;
    if (isCorrect) {
      audio.playSfx('correct');
      setCorrectCount((c) => c + 1);
      setHp((h) => Math.max(0, h - 1));
      setFeedback(String(step.slots.victory_line || 'Nice hit!'));
      setHitAnim(true);
      setShowStars(true);
      setTimeout(() => { setHitAnim(false); setShowStars(false); }, 600);
    } else {
      audio.playSfx('wrong');
      setFeedback(String(step.slots.defeat_line || `Oops. Answer: ${answer}`));
    }

    window.setTimeout(() => {
      const nextIndex = roundIndex + 1;
      const nextHp = isCorrect ? Math.max(0, hp - 1) : hp;
      if (nextHp <= 0 || nextIndex >= Math.max(1, rounds.length)) {
        finish();
        return;
      }
      setRoundIndex(nextIndex);
      setFeedback('');
      setLocked(false);
    }, 850);
  }

  return (
    <div className="tpl-battle">
      <div className="tpl-battle__header">
        <Pill tone="brand">Boss Battle</Pill>
        <div className="tpl-battle__hp" aria-label="Monster HP">
          {Array.from({ length: hpTotal }).map((_, i) => (
            <span key={i} className={`tpl-battle__heart ${i < hp ? 'on' : 'off'}`} aria-hidden="true">
              ❤️
            </span>
          ))}
        </div>
      </div>

      <div className="tpl-battle__monster">
        <div className={`tpl-battle__monster-avatar ${hitAnim ? 'is-hit' : ''}`} aria-hidden="true">
          {MonsterSvg ? <MonsterSvg mood={hp <= 1 ? 'sad' : 'strong'} size={80} /> : monsterAsset.emoji}
        </div>
        {showStars && <div className="anim-stars" aria-hidden="true">⭐️✨⭐️</div>}
        <strong className="tpl-battle__monster-name">{name}</strong>
      </div>

      <div className="tpl-battle__card">
        <p className="tpl-battle__question">{String(round.question || 'Pick one')}</p>
        <div className="tpl-battle__options">
          {options.map((opt) => (
            <Button key={opt} size="lg" variant="secondary" onClick={() => onPick(opt)} disabled={locked}>
              {opt}
            </Button>
          ))}
        </div>
        {feedback ? (
          <p className={`tpl-battle__feedback ${feedback.includes('Nice') || feedback.includes('hit') ? 'ok' : ''}`}>
            {feedback}
          </p>
        ) : null}
        <p className="tpl-battle__meta">
          Round {roundIndex + 1} / {Math.max(1, rounds.length)}
        </p>
      </div>
    </div>
  );
}
