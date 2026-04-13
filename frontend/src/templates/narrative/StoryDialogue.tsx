import { useState } from 'react';
import type { TemplateProps } from '../../engine/types';
import { Pill } from '../../components/primitives/Pill';
import { CharacterStage } from '../common/CharacterStage';
import { resolveCharacterAsset } from '../common/characterRegistry';
import { TypeWriter } from '../common/TypeWriter';

type DialogueLine = { character?: string; mood?: string; line?: string };

export function StoryDialogue({ step, onComplete, audio }: TemplateProps) {
  const background = String(step.slots.background || 'default');
  const dialogues = Array.isArray(step.slots.dialogues) ? (step.slots.dialogues as DialogueLine[]) : [];
  const first = dialogues[0];
  const line = String(first?.line || 'Ready to play?');
  const speaker = String(first?.character || 'narrator');
  const second = dialogues[1];
  const [typeDone, setTypeDone] = useState(false);

  const asset = resolveCharacterAsset(speaker);
  const Svg = asset.SvgComponent;

  return (
    <div className="tpl-story">
      <div className="tpl-story__header">
        <Pill tone="warning">Story</Pill>
      </div>
      <div className="tpl-story__bubble">
        <span className="tpl-story__avatar" aria-hidden="true">
          {Svg ? <Svg mood={String(first?.mood || 'neutral')} size={52} /> : asset.emoji}
        </span>
        <div className="tpl-story__copy">
          <strong className="tpl-story__name">{asset.displayName}</strong>
          <p className="tpl-story__line">
            <TypeWriter text={line} speed={30} onDone={() => setTypeDone(true)} />
          </p>
        </div>
      </div>
      <CharacterStage
        scene={background}
        left={{ id: speaker, mood: String(first?.mood || 'curious'), line }}
        right={{
          id: String(second?.character || 'ellie'),
          mood: String(second?.mood || 'happy'),
          line: String(second?.line || ''),
        }}
      />
      <div className="tpl-story__actions">
        <button
          className="ui-button ui-button--primary ui-button--lg"
          disabled={!typeDone}
          onClick={() => {
            audio.playSfx('tap');
            onComplete({
              step_id: step.step_id,
              template_id: step.template_id,
              correct: null,
              score: 5,
              duration_ms: 1200,
              details: { progressed: true },
            });
          }}
        >
          Continue
        </button>
        <button
          className="ui-button ui-button--ghost ui-button--lg"
          onClick={() => audio.playTts(line)}
        >
          🔊 Listen
        </button>
      </div>
    </div>
  );
}
