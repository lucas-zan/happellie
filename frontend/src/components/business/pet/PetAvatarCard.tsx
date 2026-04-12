import type { PetSummary } from '../../../api/types';
import { Card, CardContent, CardDescription, CardTitle } from '../../Card';
import { Pill } from '../../primitives/Pill';
import { ProgressBar } from '../../primitives/ProgressBar';

function getPetEmoji(species: string) {
  if (species.toLowerCase().includes('rabbit')) return '🐰';
  if (species.toLowerCase().includes('dog')) return '🐶';
  return '🐱';
}

export function PetAvatarCard({ pet }: { pet: PetSummary }) {
  return (
    <Card tone="hero" className="pet-hero-card">
      <CardContent className="pet-hero-card__content">
        <div className="pet-avatar" aria-hidden="true">
          <span className="pet-avatar__emoji">{getPetEmoji(pet.species)}</span>
          <span className="pet-avatar__stage">Lv.{pet.growth_stage}</span>
        </div>
        <div className="ui-stack-sm">
          <div className="ui-inline-split ui-inline-split--wrap">
            <CardTitle>{pet.pet_name}</CardTitle>
            <Pill tone="brand">{pet.species}</Pill>
          </div>
          <CardDescription>
            Ellie stays visually consistent. Feeding only updates growth signals and stats, never the base pet identity.
          </CardDescription>
          <ProgressBar label="Hunger" value={pet.hunger} />
          <ProgressBar label="Affection" value={pet.affection} tone="success" />
        </div>
      </CardContent>
    </Card>
  );
}
