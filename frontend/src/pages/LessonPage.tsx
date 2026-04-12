import { useMemo, useState } from 'react';
import { apiClient } from '../api/client';
import type { LessonComponent, LessonPage as LessonGamePage, LessonResponse, SessionBlockResult } from '../api/types';
import {
  EmptyState,
  LessonRequestForm,
  LessonSummaryCard,
  PageHeader,
  Section,
  SessionFeedbackCard,
  StatusMessage,
} from '../components';
import { Button } from '../components/Button';
import { PageRenderer } from '../renderers/PageRenderer';

const DEFAULT_STUDENT_ID = 'student-demo';
const INTERACTIVE_TYPES = new Set(['choice_quiz', 'repeat_prompt']);

function defaultResultFor(component: LessonComponent): SessionBlockResult {
  const isInteractive = INTERACTIVE_TYPES.has(component.type);
  return {
    block_id: component.component_id,
    block_type: component.type,
    correct: !isInteractive,
    score: component.type === 'reward_panel' || component.type === 'feed_panel' ? 0 : isInteractive ? 0 : 5,
    duration_ms: 1500,
  };
}

export function LessonPage() {
  const [studentId, setStudentId] = useState(DEFAULT_STUDENT_ID);
  const [vocabInput, setVocabInput] = useState('apple,milk,hungry');
  const [data, setData] = useState<LessonResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState<Record<string, SessionBlockResult>>({});
  const [message, setMessage] = useState('');
  const [currentPageIndex, setCurrentPageIndex] = useState(0);

  const requestedVocab = useMemo(
    () => vocabInput.split(',').map((item) => item.trim()).filter(Boolean),
    [vocabInput],
  );

  const currentPage = data?.lesson.pages[currentPageIndex] ?? null;
  const totalCount = data?.lesson.pages.length ?? 0;
  const completedCount = data
    ? data.lesson.pages.filter((page) =>
        page.components.every((component) => !INTERACTIVE_TYPES.has(component.type) || Boolean(results[component.component_id])),
      ).length
    : 0;

  const pageReady = !currentPage
    ? false
    : currentPage.components
        .filter((component) => INTERACTIVE_TYPES.has(component.type))
        .every((component) => Boolean(results[component.component_id]));

  async function generate() {
    setLoading(true);
    setMessage('');
    setResults({});
    setCurrentPageIndex(0);
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

  function onComponentResult(result: SessionBlockResult) {
    setResults((current) => ({ ...current, [result.block_id]: result }));
  }

  function goNextPage() {
    if (!data || !currentPage) return;
    if (currentPageIndex >= data.lesson.pages.length - 1) return;
    setCurrentPageIndex((value) => value + 1);
  }

  async function complete() {
    if (!data) return;
    setSubmitting(true);
    setMessage('');
    try {
      const allComponents = data.lesson.pages.flatMap((page) => page.components);
      const finalResults = allComponents.map((component) => results[component.component_id] || defaultResultFor(component));
      const totalScore = finalResults.reduce((sum, item) => sum + item.score, 0);
      const earnedCoins = Number(data.lesson.reward_preview.coins ?? 3);
      const earnedFood = Number(data.lesson.reward_preview.food ?? 2);
      const sessionResponse = await apiClient.completeSession({
        student_id: studentId,
        lesson_id: data.lesson.lesson_id,
        duration_seconds: Math.max(180, data.lesson.pages.length * 40),
        total_score: totalScore,
        earned_food: earnedFood,
        earned_coins: earnedCoins,
        story_arc_key: data.lesson.story.arc_key,
        story_episode_index: data.lesson.story.episode_index,
        story_last_scene: data.lesson.story.current_mission,
        story_next_hook: data.lesson.story.next_hook,
        encountered_characters: data.lesson.story.characters.map((character) => character.name),
        block_results: finalResults,
      });

      const feedComponent = data.lesson.pages
        .flatMap((page) => page.components)
        .find((component) => component.type === 'feed_panel');
      let feedMessage = '';
      if (feedComponent && earnedFood > 0) {
        const quantity = Math.max(1, Math.min(Number(feedComponent.payload.quantity ?? 1), earnedFood));
        const feedResponse = await apiClient.feedPet({
          student_id: studentId,
          food_type: String(feedComponent.payload.food_type || 'basic_food'),
          quantity,
        });
        if (feedResponse.status === 'ok') {
          feedMessage = ` Ellie ate ${quantity} meal and reached Lv.${feedResponse.pet.growth_stage}.`;
        }
      }

      setMessage(
        `Lesson saved. Next focus: ${String(sessionResponse.next_recommendation.focus ?? 'food')}. Story continues with ${String(sessionResponse.next_recommendation.story_next_hook ?? data.lesson.story.next_hook)}.${feedMessage}`.trim(),
      );
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Section>
      <PageHeader
        title="Lesson"
        description="Generate a page-based mini game, move through one action per screen, then save rewards and feed Ellie."
      />

      <LessonRequestForm
        studentId={studentId}
        vocabInput={vocabInput}
        onStudentIdChange={setStudentId}
        onVocabInputChange={setVocabInput}
        onSubmit={generate}
        loading={loading}
      />

      {message ? <StatusMessage tone="info">{message}</StatusMessage> : null}

      {!data || !currentPage ? (
        <EmptyState title="No lesson loaded" description="Generate a lesson package to play through the game pages." />
      ) : (
        <>
          <LessonSummaryCard data={data} />
          <SessionFeedbackCard
            completedCount={completedCount}
            totalCount={totalCount}
            message="Each page has one clear action. Finish all pages to save rewards and feed Ellie."
          />
          <PageRenderer page={currentPage} results={results} onResult={onComponentResult} />
          <div className="game-player-bar">
            <span className="game-player-bar__status">
              Page {currentPageIndex + 1} / {data.lesson.pages.length}
            </span>
            {currentPageIndex < data.lesson.pages.length - 1 ? (
              <Button size="lg" variant="primary" onClick={goNextPage} disabled={!pageReady}>
                {currentPage.completion_label || 'Next'}
              </Button>
            ) : (
              <Button size="lg" variant="primary" onClick={complete} disabled={submitting || !pageReady}>
                {submitting ? 'Saving...' : currentPage.completion_label || 'Finish lesson'}
              </Button>
            )}
          </div>
        </>
      )}
    </Section>
  );
}
