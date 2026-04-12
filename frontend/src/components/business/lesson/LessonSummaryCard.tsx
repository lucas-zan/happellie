import type { LessonResponse } from '../../../api/types';
import { Card, CardContent, CardMeta, CardTitle } from '../../Card';
import { Pill } from '../../primitives/Pill';

export function LessonSummaryCard({ data }: { data: LessonResponse }) {
  return (
    <Card>
      <CardContent>
        <div className="ui-inline-split ui-inline-split--wrap">
          <div className="ui-stack-md">
            <CardTitle>{data.lesson.title}</CardTitle>
            <span className="ui-helper-text">{data.lesson.story.episode_title}</span>
          </div>
          <Pill tone={data.source === 'generated' ? 'brand' : 'success'}>
            {data.source === 'generated' ? 'AI generated' : 'Cache reused'}
          </Pill>
        </div>
        <div className="ui-meta-row">
          <CardMeta label="Lesson ID" value={data.lesson.lesson_id} />
          <CardMeta label="Pages" value={data.lesson.pages.length} />
          <CardMeta label="Minutes" value={data.lesson.estimated_minutes} />
          <CardMeta label="Vocabulary" value={data.lesson.vocab.join(', ')} />
        </div>
      </CardContent>
    </Card>
  );
}
