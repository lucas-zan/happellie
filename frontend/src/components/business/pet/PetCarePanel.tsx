import { Button } from '../../Button';
import { Card, CardContent, CardTitle } from '../../Card';
import { KeyValueGrid } from '../../primitives/KeyValueGrid';

export function PetCarePanel({
  foodCount,
  onFeed,
  feedDisabled,
}: {
  foodCount: number;
  onFeed: () => void;
  feedDisabled?: boolean;
}) {
  return (
    <Card tone="soft">
      <CardContent>
        <CardTitle>Quick care</CardTitle>
        <KeyValueGrid
          items={[
            { key: 'food-type', label: 'Food type', value: 'basic_food' },
            { key: 'food-count', label: 'Inventory', value: foodCount },
            { key: 'effect', label: 'Effect', value: '+hunger, +affection' },
          ]}
        />
        <Button variant="primary" onClick={onFeed} disabled={feedDisabled}>
          Feed basic food
        </Button>
      </CardContent>
    </Card>
  );
}
