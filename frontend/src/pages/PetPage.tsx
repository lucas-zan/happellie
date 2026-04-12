import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import type { PetSummary } from '../api/types';
import {
  Button,
  Card,
  CardContent,
  EmptyState,
  Field,
  PageHeader,
  PetAvatarCard,
  PetCarePanel,
  PetStatsPanel,
  Section,
  StatusMessage,
} from '../components';

const DEFAULT_STUDENT_ID = 'student-demo';

export function PetPage() {
  const [studentId, setStudentId] = useState(DEFAULT_STUDENT_ID);
  const [pet, setPet] = useState<PetSummary | null>(null);
  const [message, setMessage] = useState('');

  async function load() {
    try {
      const result = await apiClient.getPet(studentId);
      setPet(result);
      setMessage('');
    } catch (error) {
      setMessage((error as Error).message);
    }
  }

  async function feed() {
    try {
      const result = await apiClient.feedPet({ student_id: studentId, food_type: 'basic_food', quantity: 1 });
      setPet(result.pet);
      setMessage(result.status === 'ok' ? 'Ellie enjoyed the food.' : 'Not enough food in inventory yet.');
    } catch (error) {
      setMessage((error as Error).message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <Section>
      <PageHeader
        title={pet?.pet_name ?? 'Pet'}
        description="Pet identity stays stable. Shared business components handle avatar, stats, and care actions."
        actions={<Button onClick={load}>Refresh</Button>}
      />
      <Card>
        <CardContent className="ui-form-grid">
          <Field label="Student ID" value={studentId} onChange={(e) => setStudentId(e.target.value)} />
          <div className="ui-form-grid__actions">
            <Button onClick={load}>Load pet</Button>
          </div>
        </CardContent>
      </Card>
      {message ? <StatusMessage tone="info">{message}</StatusMessage> : null}

      {!pet ? (
        <EmptyState title="No pet loaded" description="Load a student first to see the pet summary." />
      ) : (
        <>
          <PetAvatarCard pet={pet} />
          <PetStatsPanel pet={pet} />
          <PetCarePanel foodCount={pet.food_inventory.basic_food ?? 0} onFeed={feed} feedDisabled={(pet.food_inventory.basic_food ?? 0) <= 0} />
        </>
      )}
    </Section>
  );
}
