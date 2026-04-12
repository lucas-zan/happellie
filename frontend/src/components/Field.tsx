import type { InputHTMLAttributes } from 'react';
import { cn } from '../utils/cn';

export type FieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  hint?: string;
};

export function Field({ label, hint, className, id, ...props }: FieldProps) {
  const inputId = id ?? props.name ?? label;
  return (
    <label className="ui-field" htmlFor={inputId}>
      <span className="ui-field__label">{label}</span>
      <input id={inputId} className={cn('ui-input', className)} {...props} />
      {hint ? <span className="ui-field__hint">{hint}</span> : null}
    </label>
  );
}
