import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../utils/cn';

type CardTone = 'default' | 'hero' | 'reward' | 'soft';

export type CardProps = HTMLAttributes<HTMLDivElement> & {
  tone?: CardTone;
};

export function Card({ className, tone = 'default', children, ...props }: CardProps) {
  return (
    <article className={cn('ui-card', `ui-card--${tone}`, className)} {...props}>
      {children}
    </article>
  );
}

export function CardHeader({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <header className={cn('ui-card__header', className)} {...props}>
      {children}
    </header>
  );
}

export function CardTitle({ className, children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn('ui-card__title', className)} {...props}>
      {children}
    </h3>
  );
}

export function CardDescription({ className, children, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn('ui-card__description', className)} {...props}>
      {children}
    </p>
  );
}

export function CardContent({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('ui-card__content', className)} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <footer className={cn('ui-card__footer', className)} {...props}>
      {children}
    </footer>
  );
}

export function CardMeta({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="ui-card__meta">
      <span className="ui-card__meta-label">{label}</span>
      <strong className="ui-card__meta-value">{value}</strong>
    </div>
  );
}
