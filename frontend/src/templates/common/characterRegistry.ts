import type { ComponentType } from 'react';
import { CHARACTER_MANIFEST } from './characterManifest';
import { SvgEllie, SvgFoxy, SvgMonster } from './svg';

export type CharacterAsset = {
  id: string;
  displayName: string;
  emoji: string;
  sprite?: string;
  SvgComponent?: ComponentType<{ mood?: string; size?: number }>;
};

const SVG_MAP: Record<string, ComponentType<{ mood?: string; size?: number }>> = {
  ellie: SvgEllie,
  foxy: SvgFoxy,
  monster: SvgMonster,
};

const REGISTRY: Record<string, CharacterAsset> = CHARACTER_MANIFEST.reduce<Record<string, CharacterAsset>>((acc, item) => {
  const asset: CharacterAsset = {
    id: item.id,
    displayName: item.displayName,
    emoji: item.emoji,
    sprite: item.spritePath || undefined,
    SvgComponent: SVG_MAP[item.id],
  };
  acc[item.id.toLowerCase()] = asset;
  for (const alias of item.aliases || []) {
    acc[alias.toLowerCase()] = asset;
  }
  return acc;
}, {});

function inferKey(id: string): string {
  const key = id.toLowerCase();
  const entries = Object.keys(REGISTRY);
  const found = entries.find((entry) => key.includes(entry));
  return found || 'narrator';
}

export function resolveCharacterAsset(id: string): CharacterAsset {
  return REGISTRY[inferKey(id)] || { id: 'unknown', displayName: 'Unknown', emoji: '✨' };
}
