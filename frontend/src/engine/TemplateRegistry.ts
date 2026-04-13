import type { TemplateId, TemplateProps } from './types';

import { ChoiceBattle } from '../templates/practice/ChoiceBattle';
import { ListenPick } from '../templates/practice/ListenPick';
import { DragMatch } from '../templates/practice/DragMatch';
import { RewardChest } from '../templates/reward/RewardChest';
import { FeedPetStep } from '../templates/reward/FeedPetStep';
import { EpisodeEnd } from '../templates/reward/EpisodeEnd';
import { StoryDialogue } from '../templates/narrative/StoryDialogue';
import { StoryChoice } from '../templates/narrative/StoryChoice';
import { WordReveal } from '../templates/learn/WordReveal';

type TemplateComponent = (props: TemplateProps) => JSX.Element;

const registry: Record<TemplateId, TemplateComponent> = {
  story_dialogue: StoryDialogue,
  story_choice: StoryChoice,
  mission_briefing: StoryDialogue, // placeholder until implemented
  word_reveal: WordReveal,
  word_in_scene: WordReveal, // placeholder
  listen_pick: ListenPick,
  drag_match: DragMatch,
  choice_battle: ChoiceBattle,
  sentence_puzzle: WordReveal, // placeholder
  speak_repeat: WordReveal, // placeholder
  reward_chest: RewardChest,
  feed_pet_step: FeedPetStep,
  episode_end: EpisodeEnd,
};

export function getTemplate(templateId: TemplateId) {
  return registry[templateId] ?? null;
}

