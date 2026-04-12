from __future__ import annotations

from collections import Counter
from uuid import uuid4

from app.domain.interfaces.planning import LessonPlanner
from app.schemas.lesson import LessonBlueprint, LessonBlueprintPage, LessonRequest, StoryCharacter, StoryThread, VocabItem
from app.schemas.profile import ProfileSnapshot


class RulesLessonPlanner(LessonPlanner):
    def plan(
        self,
        request: LessonRequest,
        profile: ProfileSnapshot | None,
        available_vocab: list[VocabItem],
    ) -> LessonBlueprint:
        target_vocab = self._select_vocab(request, profile, available_vocab)
        focus_tags = self._focus_tags(profile, target_vocab)
        theme = (profile.preferred_themes[0] if profile and profile.preferred_themes else "feed_rabbit")
        title = self._build_title(theme, target_vocab)
        rewards = {"coins": max(3, len(target_vocab) + 1), "food": max(1, len(target_vocab) // 2 or 1)}
        story = self._build_story(profile, target_vocab)
        pages = [
            LessonBlueprintPage(
                page_id="p1",
                page_type="hero",
                title="Ellie needs your help",
                goal="Start the lesson with a short pet mission.",
                component_types=["hero_banner", "story_panel", "pet_reaction"],
                payload_hints={"emotion": "hungry", "mission": story.current_mission},
            ),
            LessonBlueprintPage(
                page_id="p2",
                page_type="learn",
                title="Meet today's words",
                goal="Introduce the target words clearly and briefly.",
                component_types=["word_card"],
                payload_hints={"items": [item.text for item in target_vocab]},
            ),
            LessonBlueprintPage(
                page_id="p3",
                page_type="quiz",
                title="Help Ellie choose",
                goal="Play one quick choice task using the target words.",
                component_types=["encounter_card", "choice_quiz", "pet_reaction"],
                payload_hints={
                    "answer": target_vocab[0].text,
                    "options": [item.text for item in target_vocab[:3]],
                    "monster_name": next((character.name for character in story.characters if character.kind == "monster"), "Crumb Goblin"),
                },
            ),
            LessonBlueprintPage(
                page_id="p4",
                page_type="repeat",
                title="Say it with Ellie",
                goal="Let the child repeat a short sentence using one target word.",
                component_types=["repeat_prompt"],
                payload_hints={"focus_word": target_vocab[0].text},
            ),
            LessonBlueprintPage(
                page_id="p5",
                page_type="settlement",
                title="Great job",
                goal="Summarize rewards in cheerful child-friendly language.",
                component_types=["reward_panel"],
                payload_hints=rewards,
            ),
            LessonBlueprintPage(
                page_id="p6",
                page_type="feed_pet",
                title="Feed Ellie now",
                goal="Turn the lesson reward into pet care.",
                component_types=["feed_panel", "pet_reaction"],
                payload_hints={"food_type": "basic_food", "quantity": 1, "emotion": "excited"},
            ),
        ]
        return LessonBlueprint(
            blueprint_id=f"blueprint-{uuid4().hex[:8]}",
            student_id=request.student_id,
            lesson_type=request.lesson_type,
            theme=theme,
            level_hint=request.level_hint,
            title=title,
            target_vocab=target_vocab,
            focus_tags=focus_tags,
            rewards=rewards,
            pages=pages,
            story=story,
            teacher_note="Keep each interaction short and cheerful.",
        )

    def _select_vocab(
        self,
        request: LessonRequest,
        profile: ProfileSnapshot | None,
        available_vocab: list[VocabItem],
    ) -> list[VocabItem]:
        if request.requested_vocab:
            requested = {item.strip().lower() for item in request.requested_vocab if item.strip()}
            selected = [item for item in available_vocab if item.key.lower() in requested or item.text.lower() in requested]
            return selected[:4] or available_vocab[:4]

        if not available_vocab:
            return [
                VocabItem(key="apple", text="apple", meaning="苹果", category="food"),
                VocabItem(key="milk", text="milk", meaning="牛奶", category="food"),
                VocabItem(key="hungry", text="hungry", meaning="饿的", category="feeling"),
            ]

        preferred_categories = list(profile.weak_vocab_tags if profile else [])
        if not preferred_categories and profile and profile.latest_focus:
            preferred_categories = profile.latest_focus
        pool = [item for item in available_vocab if item.category in preferred_categories or preferred_categories and bool(set(item.tags) & set(preferred_categories))]
        if len(pool) < 3:
            pool = available_vocab
        return pool[:4]

    def _focus_tags(self, profile: ProfileSnapshot | None, selected: list[VocabItem]) -> list[str]:
        counter = Counter(item.category for item in selected)
        focus = [name for name, _ in counter.most_common(2)]
        if profile:
            for tag in profile.weak_vocab_tags[:2]:
                if tag not in focus:
                    focus.append(tag)
        return focus[:3] or ["food"]

    def _build_title(self, theme: str, selected: list[VocabItem]) -> str:
        lead = selected[0].text if selected else "food"
        mapping = {
            "feed_rabbit": f"Feed Ellie with {lead}",
            "pet_play": f"Play with Ellie and {lead}",
            "pet_bedtime": f"Bedtime words with {lead}",
        }
        return mapping.get(theme, f"HappyEllie lesson: {lead}")

    def _build_story(self, profile: ProfileSnapshot | None, selected: list[VocabItem]) -> StoryThread:
        arc_key = profile.story_arc_key if profile and profile.story_arc_key else "snack_scouts"
        episode_index = (profile.story_episode_index + 1) if profile and profile.story_episode_index else 1
        lead = selected[0].text if selected else "apple"
        companion_name = "Momo Fox" if arc_key == "snack_scouts" else "Pip Owl"
        monster_name = "Crumb Goblin" if arc_key == "snack_scouts" else "Misty Pollen Bug"
        recap = profile.story_next_hook or profile.story_last_scene or "Ellie started a tiny snack adventure."
        current_mission = f"Find the {lead} snack before {monster_name} reaches the garden."
        next_hook = f"Next time, Ellie and {companion_name} will cross the moon bridge to find a new snack."
        return StoryThread(
            arc_key=arc_key,
            episode_index=episode_index,
            episode_title=f"Episode {episode_index}: The {lead.title()} Snack Rescue",
            recap=recap,
            current_mission=current_mission,
            next_hook=next_hook,
            characters=[
                StoryCharacter(character_id="pet_ellie", name="Ellie", kind="pet", role="hero pet", mood="brave"),
                StoryCharacter(character_id="companion_1", name=companion_name, kind="animal", role="forest helper", mood="cheerful"),
                StoryCharacter(character_id="monster_1", name=monster_name, kind="monster", role="snack thief", mood="sneaky"),
            ],
        )
