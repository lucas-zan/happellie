import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardTitle,
  PageHeader,
  Pill,
  Section,
  StatusMessage,
} from '../components';

export function HomePage() {
  const [status, setStatus] = useState('checking');

  useEffect(() => {
    apiClient.health().then(() => setStatus('backend connected')).catch(() => setStatus('backend offline'));
  }, []);

  return (
    <Section>
      <PageHeader
        title="Welcome back to HappyEllie"
        description="A local-first prototype where lessons, pet growth, and trial analytics all share the same reusable UI building blocks."
      />
      <StatusMessage tone={status === 'backend connected' ? 'success' : status === 'backend offline' ? 'error' : 'info'}>
        Backend status: <strong>{status}</strong>
      </StatusMessage>
      <Card tone="hero">
        <CardContent>
          <div className="ui-inline-split ui-inline-split--wrap">
            <CardTitle>Experiment-first local prototype</CardTitle>
            <Pill tone="brand">Starter build</Pill>
          </div>
          <CardDescription>
            Generate tiny pet-feeding lessons, complete a session, earn food, then feed Ellie and inspect cost and usage
            metrics in the admin panel.
          </CardDescription>
        </CardContent>
      </Card>
      <div className="ui-grid ui-grid--cards">
        <Card>
          <CardContent>
            <CardTitle>Start a playable story game</CardTitle>
            <CardDescription>Generate a step-based interactive lesson and play it like a mini game.</CardDescription>
          </CardContent>
          <CardFooter>
            <Link to="/play">
              <Button variant="secondary">Go to play</Button>
            </Link>
          </CardFooter>
        </Card>
        <Card>
          <CardContent>
            <CardTitle>Visit Ellie</CardTitle>
            <CardDescription>Check growth, food inventory, and feed the pet.</CardDescription>
          </CardContent>
          <CardFooter>
            <Link to="/pet">
              <Button variant="secondary">Open pet</Button>
            </Link>
          </CardFooter>
        </Card>
        <Card>
          <CardContent>
            <CardTitle>Admin panel</CardTitle>
            <CardDescription>Track trial usage, AI generation counts, and cost statistics.</CardDescription>
          </CardContent>
          <CardFooter>
            <Link to="/admin">
              <Button variant="secondary">View stats</Button>
            </Link>
          </CardFooter>
        </Card>
      </div>
    </Section>
  );
}
