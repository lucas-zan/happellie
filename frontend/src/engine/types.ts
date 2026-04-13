export type TemplateId =
  | 'story_dialogue'
  | 'story_choice'
  | 'mission_briefing'
  | 'word_reveal'
  | 'word_in_scene'
  | 'listen_pick'
  | 'drag_match'
  | 'choice_battle'
  | 'sentence_puzzle'
  | 'speak_repeat'
  | 'reward_chest'
  | 'feed_pet_step'
  | 'episode_end';

export interface GameStep {
  step_id: string;
  template_id: TemplateId;
  title?: string;
  slots: Record<string, unknown>;
  is_interactive?: boolean;
  reward_on_complete?: Record<string, unknown>;
}

export interface StepResult {
  step_id: string;
  template_id: string;
  correct: boolean | null;
  score: number;
  duration_ms: number;
  details: Record<string, unknown>;
}

export type SfxKey = 'correct' | 'wrong' | 'coin' | 'tap' | 'whoosh' | 'cheer';

export type AudioController = {
  playSfx: (key: SfxKey) => void;
  playTts: (text: string) => void;
};

export type TemplateProps = {
  step: GameStep;
  onComplete: (result: StepResult) => void;
  audio: AudioController;
  runtime?: {
    studentId: string;
    lessonId: string;
  };
};
