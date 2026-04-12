import { Card, CardContent, CardDescription, CardTitle } from './Card';

export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <Card className="ui-empty-state" tone="soft">
      <CardContent>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardContent>
    </Card>
  );
}
