import { Card, CardContent, CardTitle } from './Card';

export function MetricList({
  title,
  items,
}: {
  title: string;
  items: Array<{ key: string; primary: string; secondary?: string }>;
}) {
  return (
    <Card>
      <CardContent>
        <CardTitle>{title}</CardTitle>
        <ul className="ui-metric-list">
          {items.map((item) => (
            <li className="ui-metric-list__item" key={item.key}>
              <span className="ui-metric-list__primary">{item.primary}</span>
              {item.secondary ? <span className="ui-metric-list__secondary">{item.secondary}</span> : null}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
