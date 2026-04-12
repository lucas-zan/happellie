import type { AdminOverview } from '../../../api/types';
import { MetricList } from '../../MetricList';

export function AdminBreakdownPanel({ overview }: { overview: AdminOverview }) {
  return (
    <>
      <div className="ui-grid ui-grid--two-col">
        <MetricList
          title="Feature costs"
          items={overview.feature_costs.map((row) => ({
            key: row.feature,
            primary: `${row.feature}: ${row.count} calls`,
            secondary: `${row.cost_cents} cents`,
          }))}
        />
        <MetricList
          title="AI usage"
          items={overview.ai_usage.map((row) => ({
            key: row.provider,
            primary: `${row.provider}: ${row.count} calls`,
            secondary: `${row.cost_cents} cents`,
          }))}
        />
      </div>
      <MetricList
        title="Students"
        items={overview.students.map((row) => ({
          key: row.student_id,
          primary: `${row.student_id}: ${row.sessions} sessions`,
          secondary: `${row.usage_minutes} min`,
        }))}
      />
    </>
  );
}
