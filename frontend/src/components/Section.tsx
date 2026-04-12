import type { HTMLAttributes } from 'react';
import { cn } from '../utils/cn';

export function Section({ className, children, ...props }: HTMLAttributes<HTMLElement>) {
  return (
    <section className={cn('ui-section', className)} {...props}>
      {children}
    </section>
  );
}
