import type { AdminOverview } from '../../../api/types';
import { StatCard } from '../../StatCard';

export function AdminSummaryGrid({ overview }: { overview: AdminOverview }) {
  return (
    <div className="ui-grid ui-grid--stats">
      {overview.summary.map((item) => (
        <StatCard key={item.key} label={item.label} value={`${item.value}${item.unit ? ` ${item.unit}` : ''}`} />
      ))}
    </div>
  );
}
