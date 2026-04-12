import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import type { AdminOverview } from '../api/types';
import {
  AdminBreakdownPanel,
  AdminSummaryGrid,
  Button,
  EmptyState,
  PageHeader,
  Section,
  StatusMessage,
} from '../components';

export function AdminPage() {
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [error, setError] = useState('');

  async function load() {
    try {
      const data = await apiClient.adminOverview();
      setOverview(data);
      setError('');
    } catch (err) {
      setError((err as Error).message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <Section>
      <PageHeader
        title="Admin panel"
        description="Inspect trial usage, AI calls, feature consumption, and cost patterns through shared reporting widgets."
        actions={<Button onClick={load}>Refresh</Button>}
      />

      {error ? <StatusMessage tone="error">{error}</StatusMessage> : null}
      {!overview && !error ? <EmptyState title="Loading stats" description="Fetching usage and cost aggregates." /> : null}

      {overview ? (
        <>
          <AdminSummaryGrid overview={overview} />
          <AdminBreakdownPanel overview={overview} />
        </>
      ) : null}
    </Section>
  );
}
