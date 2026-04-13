import type { TemplateProps } from '../../engine/types';
import { Pill } from '../../components/primitives/Pill';
import { Button } from '../../components/Button';
import { CharacterStage } from '../common/CharacterStage';

export function WordReveal({ step, onComplete, audio }: TemplateProps) {
  const word = String(step.slots.word || '');
  const meaning = String(step.slots.meaning || '');
  const sentence = String(step.slots.sentence || '');
  const audioText = String(step.slots.audio_text || word);
  const character = (step.slots.character || {}) as { id?: string; mood?: string; line?: string };

  return (
    <div className="tpl-word-reveal">
      <div className="tpl-word-reveal__header">
        <Pill tone="brand">New word</Pill>
        <div className="tpl-word-reveal__chips">
          <Pill tone="neutral">English</Pill>
          <Pill tone="neutral">中文</Pill>
        </div>
      </div>

      <div className="tpl-word-reveal__card">
        <div className="tpl-word-reveal__word">
          <strong>{word || '...'}</strong>
          <button className="ui-link-button" onClick={() => audio.playTts(audioText)}>
            🔊
          </button>
        </div>
        <div className="tpl-word-reveal__meaning">{meaning}</div>
        {sentence ? <div className="tpl-word-reveal__sentence">{sentence}</div> : null}
      </div>
      <CharacterStage
        scene={String(step.slots.scene || 'learn_zone')}
        left={{ id: character.id || 'ellie', mood: character.mood || 'happy', line: character.line || sentence }}
        right={{ id: 'foxy', mood: 'curious', line: `Can you say "${word}"?` }}
      />

      <div className="tpl-word-reveal__actions">
        <Button
          size="lg"
          variant="secondary"
          onClick={() => {
            audio.playSfx('tap');
            audio.playTts(audioText);
          }}
        >
          Listen
        </Button>
        <Button
          size="lg"
          variant="primary"
          onClick={() => {
            audio.playSfx('whoosh');
            onComplete({
              step_id: step.step_id,
              template_id: step.template_id,
              correct: null,
              score: 10,
              duration_ms: 1500,
              details: { word, meaning },
            });
          }}
        >
          Got it
        </Button>
      </div>
    </div>
  );
}

