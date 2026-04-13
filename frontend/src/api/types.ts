export type PageType = "hero" | "learn" | "quiz" | "repeat" | "settlement" | "feed_pet";

export type ComponentType =
  | "hero_banner"
  | "story_panel"
  | "encounter_card"
  | "word_card"
  | "choice_quiz"
  | "repeat_prompt"
  | "reward_panel"
  | "feed_panel"
  | "pet_reaction";

export type TemplateId =
  | "story_dialogue"
  | "story_choice"
  | "mission_briefing"
  | "word_reveal"
  | "word_in_scene"
  | "listen_pick"
  | "drag_match"
  | "choice_battle"
  | "sentence_puzzle"
  | "speak_repeat"
  | "reward_chest"
  | "feed_pet_step"
  | "episode_end";

export interface GameStep {
  step_id: string;
  template_id: TemplateId;
  title: string;
  slots: Record<string, unknown>;
  is_interactive?: boolean;
  reward_on_complete?: Record<string, unknown>;
}

export interface LessonComponent {
  component_id: string;
  type: ComponentType;
  title: string;
  prompt: string;
  payload: Record<string, unknown>;
}

export interface StoryCharacter {
  character_id: string;
  name: string;
  kind: "pet" | "companion" | "monster" | "animal";
  role: string;
  mood: string;
}

export interface StoryThread {
  arc_key: string;
  chapter_key: string;
  episode_index: number;
  episode_title: string;
  recap: string;
  current_mission: string;
  next_hook: string;
  characters: StoryCharacter[];
}

export interface LessonPage {
  page_id: string;
  page_type: PageType;
  title: string;
  instruction: string;
  completion_label: string;
  components: LessonComponent[];
}

export interface LessonPackage {
  package_version: string;
  lesson_id: string;
  student_id: string;
  pet_id: string;
  title: string;
  theme: string;
  estimated_minutes: number;
  vocab: string[];
  story: StoryThread;
  pages: LessonPage[];
  steps?: GameStep[];
  reward_preview: Record<string, unknown>;
  focus_tags?: string[];
  teacher_note?: string;
  source_model?: string;
  debug_metadata?: Record<string, unknown>;
}

export interface LessonResponse {
  lesson: LessonPackage;
  source: "generated" | "cache";
}

export interface SessionBlockResult {
  block_id: string;
  block_type: string;
  correct: boolean;
  score: number;
  duration_ms: number;
}

export interface StepResult {
  step_id: string;
  template_id: string;
  correct: boolean | null;
  score: number;
  duration_ms: number;
  details: Record<string, unknown>;
}

export interface LearningEvent {
  event_id: string;
  session_id: string;
  student_id: string;
  lesson_id?: string;
  step_id?: string;
  template_id?: string;
  event_type: string;
  payload: Record<string, unknown>;
  timestamp?: string;
}

export interface SessionCompleteResponse {
  status: string;
  next_recommendation: Record<string, unknown>;
  updated_profile: Record<string, unknown>;
}

export interface PetSummary {
  student_id: string;
  pet_id: string;
  pet_name: string;
  species: string;
  hunger: number;
  weight: number;
  affection: number;
  growth_stage: number;
  growth_exp: number;
  emotion_state: string;
  coins: number;
  food_inventory: Record<string, number>;
  equipped_items: string[];
}

export interface PetFeedResponse {
  status: string;
  pet: PetSummary;
  growth_delta: Record<string, number>;
}

export interface ShopPurchaseResponse {
  status: string;
  pet: PetSummary;
  spent_coins: number;
  purchased_food: Record<string, number>;
}

export interface AdminMetricCard {
  key: string;
  label: string;
  value: string | number;
  unit?: string;
}

export interface AdminOverview {
  summary: AdminMetricCard[];
  feature_costs: Array<{ feature: string; count: number; cost_cents: number }>;
  ai_usage: Array<{ provider: string; count: number; cost_cents: number }>;
  students: Array<{ student_id: string; sessions: number; usage_minutes: number }>;
}
