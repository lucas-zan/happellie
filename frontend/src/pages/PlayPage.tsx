import { useMemo, useState } from 'react';
import { apiClient } from '../api/client';
import type { LearningEvent, LessonResponse, SessionBlockResult, StepResult } from '../api/types';
import { StatusMessage } from '../components';
import { Field } from '../components/Field';
import { GameEngine } from '../engine/GameEngine';
import type { GameStep } from '../engine/types';
import { SvgEllie } from '../templates/common/svg';

const DEFAULT_STUDENT_ID = 'student-demo';

function asBlockResults(stepResults: StepResult[]): SessionBlockResult[] {
  return stepResults.map((item) => ({
    block_id: item.step_id,
    block_type: item.template_id,
    correct: item.correct ?? true,
    score: item.score,
    duration_ms: item.duration_ms,
  }));
}

function asLearningEvents(items: Array<Record<string, unknown>>): LearningEvent[] {
  return items
    .map((item) => ({
      event_id: String(item.event_id || ''),
      session_id: String(item.session_id || ''),
      student_id: String(item.student_id || ''),
      lesson_id: String(item.lesson_id || ''),
      step_id: String(item.step_id || ''),
      template_id: String(item.template_id || ''),
      event_type: String(item.event_type || ''),
      payload: (item.payload || {}) as Record<string, unknown>,
      timestamp: String(item.timestamp || ''),
    }))
    .filter((item) => Boolean(item.event_id && item.session_id && item.student_id && item.event_type));
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item || '')).filter(Boolean);
}

function adaptPagesToSteps(data: LessonResponse | null): GameStep[] {
  if (!data) return [];
  const lesson = data.lesson;
  const story = lesson.story;
  const vocabItems = Array.isArray((lesson as { target_vocab_items?: unknown[] }).target_vocab_items)
    ? ((lesson as { target_vocab_items?: unknown[] }).target_vocab_items as Array<Record<string, unknown>>)
    : [];
  const words = asStringArray(lesson.vocab);
  const pages = Array.isArray(lesson.pages) ? lesson.pages : [];
  const steps = Array.isArray(lesson.steps) ? lesson.steps : [];
  if (steps.length > 0) return steps as unknown as GameStep[];

  const fallbackSteps: GameStep[] = [];
  const meaningByWord = new Map<string, string>();
  vocabItems.forEach((item: Record<string, unknown>) => {
    const key = String(item?.key || item?.text || '');
    const meaning = String(item?.meaning || '');
    if (key) meaningByWord.set(key, meaning);
  });

  pages.forEach((page, index) => {
    const pageType = String(page.page_type || '');
    const stepId = String(page.page_id || `page-${index + 1}`);
    if (pageType === 'hero') {
      fallbackSteps.push({
        step_id: stepId,
        template_id: 'story_dialogue',
        title: String(page.title || 'Story'),
        slots: {
          background: 'forest_path',
          dialogues: [
            { character: 'foxy', mood: 'happy', line: story.recap || page.instruction || 'Adventure starts now!' },
            { character: 'ellie', mood: 'excited', line: story.current_mission || 'Let us begin!' },
          ],
        },
      });
      return;
    }
    if (pageType === 'learn') {
      const first = vocabItems[0] || {};
      const word = String(first?.text || first?.key || words[0] || 'apple');
      const meaning = String(first?.meaning || meaningByWord.get(word) || '...');
      const sentence = String(first?.sample_sentence || `I can say ${word}.`);
      fallbackSteps.push({
        step_id: stepId,
        template_id: 'word_reveal',
        title: String(page.title || 'New word'),
        slots: {
          scene: 'learn_zone',
          word,
          meaning,
          sentence,
          audio_text: word,
          character: { id: 'ellie', mood: 'happy', line: sentence },
        },
      });
      return;
    }
    if (pageType === 'quiz') {
      const options = words.slice(0, 4);
      const correctKey = options[0] || 'apple';
      fallbackSteps.push({
        step_id: stepId,
        template_id: 'listen_pick',
        title: String(page.title || 'Quiz'),
        slots: {
          audio_text: correctKey,
          correct_key: correctKey,
          options: options.map((word) => ({ key: word })),
          success_line: 'Great job!',
          fail_line: `Try again, answer is ${correctKey}.`,
          character: { line: page.instruction || 'Listen and pick!' },
        },
        is_interactive: true,
        reward_on_complete: { coins: 3 },
      });
      return;
    }
    if (pageType === 'repeat') {
      const pairs = words.slice(0, 3).map((word) => ({
        left: word,
        right: meaningByWord.get(word) || word,
      }));
      fallbackSteps.push({
        step_id: stepId,
        template_id: 'drag_match',
        title: String(page.title || 'Match'),
        slots: { pairs },
        is_interactive: true,
      });
      return;
    }
    if (pageType === 'settlement') {
      fallbackSteps.push({
        step_id: stepId,
        template_id: 'reward_chest',
        title: String(page.title || 'Rewards'),
        slots: {
          total_coins: Number(lesson.reward_preview?.coins ?? 3),
          total_food: { basic_food: Number(lesson.reward_preview?.food ?? 1) },
        },
      });
      return;
    }
    if (pageType === 'feed_pet') {
      fallbackSteps.push({
        step_id: stepId,
        template_id: 'feed_pet_step',
        title: String(page.title || 'Feed'),
        slots: {
          available_food: { basic_food: Number(lesson.reward_preview?.food ?? 1) },
        },
      });
    }
  });

  fallbackSteps.push({
    step_id: `episode-end-${lesson.lesson_id}`,
    template_id: 'episode_end',
    title: 'Episode end',
    slots: {
      episode_summary: story.current_mission || 'Great learning today!',
      next_hook: story.next_hook || '',
      chapter_key: story.chapter_key || '',
    },
  });
  return fallbackSteps;
}

export function PlayPage() {
  const [studentId, setStudentId] = useState(DEFAULT_STUDENT_ID);
  const [vocabInput, setVocabInput] = useState('apple,milk,hungry');
  const [data, setData] = useState<LessonResponse | null>(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const requestedVocab = useMemo(
    () => vocabInput.split(',').map((item) => item.trim()).filter(Boolean),
    [vocabInput],
  );

  async function generate() {
    setLoading(true);
    setMessage('');
    try {
      const result = await apiClient.nextLesson({
        student_id: studentId,
        requested_vocab: requestedVocab,
        lesson_type: 'pet_feeding',
        level_hint: 'starter',
      });
      setData(result);
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function saveSession(payload: {
    lesson_id: string;
    session_id: string;
    student_id: string;
    results: StepResult[];
    coins: number;
    events: Array<Record<string, unknown>>;
  }) {
    if (!data) return;
    setSaving(true);
    setMessage('');
    try {
      await apiClient.recordEvents({
        student_id: payload.student_id,
        session_id: payload.session_id,
        events: asLearningEvents(payload.events),
      });
      const blockResults = asBlockResults(payload.results);
      const totalScore = blockResults.reduce((sum, item) => sum + item.score, 0);
      const earnedCoins = Number(data.lesson.reward_preview.coins ?? 3);
      const earnedFood = Number(data.lesson.reward_preview.food ?? 1);
      const sessionResponse = await apiClient.completeSession({
        student_id: studentId,
        lesson_id: payload.lesson_id,
        duration_seconds: Math.max(200, payload.results.length * 40),
        total_score: totalScore,
        earned_food: earnedFood,
        earned_coins: Math.max(earnedCoins, payload.coins),
        story_arc_key: data.lesson.story.arc_key,
        story_episode_index: data.lesson.story.episode_index,
        story_last_scene: data.lesson.story.current_mission,
        story_next_hook: data.lesson.story.next_hook,
        encountered_characters: data.lesson.story.characters.map((character) => character.name),
        block_results: blockResults,
        step_results: payload.results,
      });
      setMessage(
        `Saved! Next focus: ${String(sessionResponse.next_recommendation.focus ?? 'food')}. Next hook: ${String(sessionResponse.next_recommendation.story_next_hook ?? '')}`,
      );
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setSaving(false);
    }
  }

  const steps = useMemo(() => adaptPagesToSteps(data), [data]);

  if (steps.length > 0) {
    return (
      <div className="play-game-mode">
        <GameEngine lessonId={data!.lesson.lesson_id} studentId={studentId} steps={steps} onFinish={saveSession} />
        {message ? <StatusMessage tone="info">{message}</StatusMessage> : null}
        {saving ? <StatusMessage tone="warning">Saving session...</StatusMessage> : null}
      </div>
    );
  }

  return (
    <div className="play-lobby">
      <div className="play-lobby__hero">
        <div className="play-lobby__pet">
          <SvgEllie mood="happy" size={120} />
        </div>
        <h1 className="play-lobby__title">Ready for an adventure?</h1>
        <p className="play-lobby__subtitle">Learn English words while exploring with Ellie!</p>
        <button
          className="ui-button ui-button--primary ui-button--lg play-lobby__cta"
          onClick={generate}
          disabled={loading}
        >
          {loading ? 'Loading...' : '🚀 Start Adventure'}
        </button>
      </div>

      <button className="play-lobby__toggle" onClick={() => setShowSettings(!showSettings)}>
        {showSettings ? 'Hide settings' : '⚙️ Settings'}
      </button>

      {showSettings && (
        <div className="play-lobby__settings">
          <Field label="Student ID" value={studentId} onChange={(e) => setStudentId(e.target.value)} />
          <Field label="Vocab keys (comma-separated)" value={vocabInput} onChange={(e) => setVocabInput(e.target.value)} />
        </div>
      )}

      {message ? <StatusMessage tone="info">{message}</StatusMessage> : null}
    </div>
  );
}
