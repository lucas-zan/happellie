import { useState } from 'react';
import type { TemplateProps } from '../../engine/types';
import { Pill } from '../../components/primitives/Pill';
import { CharacterStage } from '../common/CharacterStage';

type Choice = { key?: string; text?: string; consequence_tag?: string };

export function StoryChoice({ step, onComplete, audio }: TemplateProps) {
  const scenario = String(step.slots.scenario || 'Choose what to do next.');
  const character = (step.slots.character || {}) as { id?: string; mood?: string; line?: string };
  const choices = Array.isArray(step.slots.choices) ? (step.slots.choices as Choice[]) : [];
  const [picked, setPicked] = useState<string | null>(null);

  return (
    <div className="tpl-story-choice">
      <div className="tpl-story-choice__header">
        <Pill tone="warning">Story choice</Pill>
      </div>
      <CharacterStage
        scene={String(step.slots.background || 'story_branch')}
        left={{ id: character.id || 'foxy', mood: character.mood || 'curious', line: character.line || scenario }}
        right={{ id: 'ellie', mood: 'curious', line: 'What should we do?' }}
      />
      <p className="tpl-story-choice__scenario">{scenario}</p>
      <div className="tpl-story-choice__options">
        {choices.map((choice, index) => {
          const key = String(choice.key || `choice-${index}`);
          return (
            <button
              key={key}
              className={`tpl-story-choice__option ${picked === key ? 'is-picked' : ''}`}
              onClick={() => {
                audio.playSfx('tap');
                setPicked(key);
                window.setTimeout(() => {
                  onComplete({
                    step_id: step.step_id,
                    template_id: step.template_id,
                    correct: true,
                    score: 12,
                    duration_ms: 1800,
                    details: {
                      chosen_key: key,
                      chosen_text: String(choice.text || ''),
                      consequence_tag: String(choice.consequence_tag || 'neutral'),
                    },
                  });
                }, 250);
              }}
            >
              <strong>{choice.text || key}</strong>
              <span>{choice.consequence_tag || 'neutral'}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

