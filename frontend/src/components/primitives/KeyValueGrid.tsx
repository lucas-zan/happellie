import type { ReactNode } from 'react';

export function KeyValueGrid({
  items,
}: {
  items: Array<{ key: string; label: string; value: ReactNode }>;
}) {
  return (
    <dl className="ui-key-value-grid">
      {items.map((item) => (
        <div key={item.key} className="ui-key-value-grid__item">
          <dt>{item.label}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}
