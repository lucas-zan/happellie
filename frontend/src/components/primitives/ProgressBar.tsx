import { cn } from '../../utils/cn';

export function ProgressBar({
  label,
  value,
  max = 100,
  tone = 'brand',
}: {
  label?: string;
  value: number;
  max?: number;
  tone?: 'brand' | 'success' | 'warning';
}) {
  const clamped = Math.max(0, Math.min(100, Math.round((value / Math.max(max, 1)) * 100)));
  return (
    <div className="ui-progress">
      {label ? (
        <div className="ui-progress__header">
          <span>{label}</span>
          <strong>{clamped}%</strong>
        </div>
      ) : null}
      <div className="ui-progress__track" aria-hidden="true">
        <div className={cn('ui-progress__fill', `ui-progress__fill--${tone}`)} style={{ width: `${clamped}%` }} />
      </div>
    </div>
  );
}
