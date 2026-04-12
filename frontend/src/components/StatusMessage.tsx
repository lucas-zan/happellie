import type { HTMLAttributes } from 'react';
import { cn } from '../utils/cn';

type Tone = 'info' | 'success' | 'warning' | 'error';

export function StatusMessage({
  children,
  tone = 'info',
  className,
  ...props
}: HTMLAttributes<HTMLParagraphElement> & { tone?: Tone }) {
  return (
    <p className={cn('ui-status-message', `ui-status-message--${tone}`, className)} {...props}>
      {children}
    </p>
  );
}
