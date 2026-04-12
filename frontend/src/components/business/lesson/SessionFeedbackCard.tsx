import { Card, CardContent, CardTitle } from '../../Card';
import { ProgressBar } from '../../primitives/ProgressBar';

export function SessionFeedbackCard({
  completedCount,
  totalCount,
  message,
}: {
  completedCount: number;
  totalCount: number;
  message?: string;
}) {
  return (
    <Card tone="soft">
      <CardContent>
        <CardTitle>Session progress</CardTitle>
        <ProgressBar label="Completed interactions" value={completedCount} max={Math.max(totalCount, 1)} />
        <p className="ui-helper-text">
          {message || 'Complete the lesson blocks, then save the session to award food and coins.'}
        </p>
      </CardContent>
    </Card>
  );
}
