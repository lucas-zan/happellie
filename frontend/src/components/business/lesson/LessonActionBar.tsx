import { Button } from '../../Button';

export function LessonActionBar({
  onComplete,
  disabled,
  submitting,
}: {
  onComplete: () => void;
  disabled?: boolean;
  submitting?: boolean;
}) {
  return (
    <div className="ui-action-bar">
      <Button variant="primary" size="lg" onClick={onComplete} disabled={disabled || submitting}>
        {submitting ? 'Saving...' : 'Complete lesson'}
      </Button>
    </div>
  );
}
