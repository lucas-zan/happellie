import type { HTMLAttributes } from 'react';
import { cn } from '../../utils/cn';

export function Panel({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('ui-panel', className)} {...props}>
      {children}
    </div>
  );
}
