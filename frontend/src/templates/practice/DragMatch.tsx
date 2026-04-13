import { useMemo, useState } from 'react';
import { DndContext, DragEndEvent, DragStartEvent, closestCenter, useDraggable, useDroppable } from '@dnd-kit/core';
import type { TemplateProps } from '../../engine/types';
import { Button } from '../../components/Button';
import { Pill } from '../../components/primitives/Pill';

type Pair = { left?: string; right?: string };

function DraggableWord({ id, text }: { id: string; text: string }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({ id });
  const style = transform
    ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
      }
    : undefined;
  return (
    <button
      ref={setNodeRef}
      style={style}
      className={`tpl-drag__word ${isDragging ? 'is-dragging' : ''}`}
      {...listeners}
      {...attributes}
    >
      {text}
    </button>
  );
}

function DropSlot({ id, label, matched }: { id: string; label: string; matched: string | null }) {
  const { setNodeRef, isOver } = useDroppable({ id });
  return (
    <div ref={setNodeRef} className={`tpl-drag__slot ${isOver ? 'is-over' : ''} ${matched ? 'is-matched' : ''}`}>
      <span className="tpl-drag__slot-label">{label}</span>
      <strong className="tpl-drag__slot-value">{matched || 'Drop here'}</strong>
    </div>
  );
}

export function DragMatch({ step, onComplete, audio }: TemplateProps) {
  const pairs = useMemo(() => (Array.isArray(step.slots.pairs) ? (step.slots.pairs as Pair[]) : []), [step]);
  const [active, setActive] = useState<string | null>(null);
  const [matches, setMatches] = useState<Record<string, string>>({});
  const [attempts, setAttempts] = useState(0);

  const rights = pairs.map((item, index) => ({ id: `right-${index}`, label: String(item.right || '') }));
  const lefts = pairs.map((item, index) => ({ id: `left-${index}`, text: String(item.left || '') }));

  function handleDragStart(event: DragStartEvent) {
    setActive(String(event.active.id));
    audio.playSfx('tap');
  }

  function handleDragEnd(event: DragEndEvent) {
    setActive(null);
    const activeId = String(event.active.id || '');
    const overId = event.over?.id ? String(event.over.id) : '';
    if (!activeId || !overId || !overId.startsWith('right-') || !activeId.startsWith('left-')) return;
    setAttempts((n) => n + 1);
    setMatches((current) => {
      const next = { ...current, [overId]: activeId };
      return next;
    });
    audio.playSfx('whoosh');
  }

  const complete = rights.every((slot) => matches[slot.id]);

  function submit() {
    let correct = 0;
    rights.forEach((slot) => {
      const rightIndex = Number(slot.id.replace('right-', ''));
      const leftId = matches[slot.id];
      const leftIndex = Number((leftId || '').replace('left-', ''));
      if (!Number.isNaN(rightIndex) && !Number.isNaN(leftIndex) && rightIndex === leftIndex) correct += 1;
    });
    const ok = correct === rights.length && rights.length > 0;
    audio.playSfx(ok ? 'correct' : 'wrong');
    onComplete({
      step_id: step.step_id,
      template_id: step.template_id,
      correct: ok,
      score: ok ? 30 : Math.max(0, correct * 8),
      duration_ms: Math.max(2500, attempts * 700),
      details: { attempts, matches, correct_pairs: correct, total_pairs: rights.length },
    });
  }

  return (
    <div className="tpl-drag">
      <div className="tpl-drag__header">
        <Pill tone="warning">Drag Match</Pill>
        <span className="tpl-drag__meta">Attempts: {attempts}</span>
      </div>

      <DndContext collisionDetection={closestCenter} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
        <div className="tpl-drag__board">
          <div className="tpl-drag__left">
            <h4>Words</h4>
            <div className="tpl-drag__word-list">
              {lefts.map((item) => (
                <DraggableWord key={item.id} id={item.id} text={item.text} />
              ))}
            </div>
          </div>
          <div className="tpl-drag__right">
            <h4>Meaning</h4>
            <div className="tpl-drag__slot-list">
              {rights.map((slot) => (
                <DropSlot
                  key={slot.id}
                  id={slot.id}
                  label={slot.label}
                  matched={matches[slot.id] ? lefts.find((l) => l.id === matches[slot.id])?.text ?? null : null}
                />
              ))}
            </div>
          </div>
        </div>
      </DndContext>

      {active ? <p className="tpl-drag__hint">Dragging {active.replace('left-', 'word ')}</p> : null}

      <div className="tpl-drag__actions">
        <Button size="lg" variant="primary" onClick={submit} disabled={!complete}>
          Check match
        </Button>
      </div>
    </div>
  );
}

