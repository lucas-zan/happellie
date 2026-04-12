import type { ReactNode } from 'react';
import { Card, CardContent } from './Card';

export function StatCard({ label, value, caption }: { label: string; value: ReactNode; caption?: ReactNode }) {
  return (
    <Card className="ui-stat-card" tone="soft">
      <CardContent>
        <span className="ui-stat-card__label">{label}</span>
        <strong className="ui-stat-card__value">{value}</strong>
        {caption ? <span className="ui-stat-card__caption">{caption}</span> : null}
      </CardContent>
    </Card>
  );
}
