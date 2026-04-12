import type { PetSummary } from '../../../api/types';
import { StatCard } from '../../StatCard';

export function PetStatsPanel({ pet }: { pet: PetSummary }) {
  return (
    <div className="ui-grid ui-grid--stats">
      <StatCard label="Species" value={pet.species} />
      <StatCard label="Weight" value={pet.weight} caption="growth unit" />
      <StatCard label="Affection" value={pet.affection} caption="bond" />
      <StatCard label="Growth stage" value={pet.growth_stage} caption="persistent" />
      <StatCard label="Coins" value={pet.coins} caption="reward currency" />
      <StatCard label="Food" value={pet.food_inventory.basic_food ?? 0} caption="basic food" />
    </div>
  );
}
