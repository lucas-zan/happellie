export type CharacterManifestItem = {
  id: string;
  displayName: string;
  emoji: string;
  spritePath?: string;
  aliases?: string[];
};

export const CHARACTER_MANIFEST: CharacterManifestItem[] = [
  { id: 'ellie', displayName: 'Ellie', emoji: '🐰', spritePath: '', aliases: ['rabbit', 'pet_ellie'] },
  { id: 'foxy', displayName: 'Foxy', emoji: '🦊', spritePath: '', aliases: ['fox', 'companion_1'] },
  { id: 'bear', displayName: 'Bear', emoji: '🐻', spritePath: '', aliases: [] },
  { id: 'owl', displayName: 'Owl', emoji: '🦉', spritePath: '', aliases: ['pip'] },
  { id: 'monster', displayName: 'Monster', emoji: '👾', spritePath: '', aliases: ['thief', 'goblin', 'monster_1'] },
  { id: 'narrator', displayName: 'Narrator', emoji: '📖', spritePath: '', aliases: [] },
];
