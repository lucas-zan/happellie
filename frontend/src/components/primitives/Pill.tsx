import type { HTMLAttributes } from 'react';
import { cn } from '../../utils/cn';

export function Pill({
  className,
  children,
  tone = 'neutral',
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: 'neutral' | 'brand' | 'success' | 'warning' }) {
  return (
    <span className={cn('ui-pill', `ui-pill--${tone}`, className)} {...props}>
      {children}
    </span>
  );
}
