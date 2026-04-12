from __future__ import annotations

from uuid import uuid4

from app.domain.interfaces.lesson import LessonGenerator
from app.schemas.lesson import LessonBlueprint, LessonComponent, LessonPackage, LessonPage


class RulesLessonGenerator(LessonGenerator):
    def generate(self, blueprint: LessonBlueprint) -> LessonPackage:
        vocab = blueprint.target_vocab
        primary = vocab[0].text if vocab else "apple"
        options = [item.text for item in vocab[:3]] or [primary, "milk", "banana"]
        companion = next((character for character in blueprint.story.characters if character.kind in {"animal", "companion"}), None)
        monster = next((character for character in blueprint.story.characters if character.kind == "monster"), None)
        pages = [
            LessonPage(
                page_id="p1",
                page_type="hero",
                title="Ellie is ready to play",
                instruction="Start a tiny mission and help Ellie get a snack.",
                completion_label="Start",
                components=[
                    LessonComponent(
                        component_id="hero_1",
                        type="hero_banner",
                        title="Tiny mission",
                        prompt=blueprint.story.current_mission or f"Learn {', '.join(item.text for item in vocab[:3])} and feed Ellie.",
                        payload={"pet_name": "Ellie", "theme": blueprint.theme},
                    ),
                    LessonComponent(
                        component_id="story_1",
                        type="story_panel",
                        title=blueprint.story.episode_title or "Story so far",
                        prompt=blueprint.story.recap or "Ellie began a tiny snack adventure.",
                        payload={
                            "recap": blueprint.story.recap,
                            "mission": blueprint.story.current_mission,
                            "companion_name": companion.name if companion else "Momo Fox",
                        },
                    ),
                    LessonComponent(
                        component_id="pet_reaction_1",
                        type="pet_reaction",
                        title="Ellie says",
                        prompt="I'm hungry. Can you help me?",
                        payload={"emotion": "hungry"},
                    ),
                ],
            ),
            LessonPage(
                page_id="p2",
                page_type="learn",
                title="Meet today's words",
                instruction="Tap next after reading the cards together.",
                completion_label="I know them",
                components=[
                    LessonComponent(
                        component_id="words_1",
                        type="word_card",
                        title="Word cards",
                        prompt="Look at the words and meanings.",
                        payload={"items": [{"word": item.text, "meaning": item.meaning} for item in vocab]},
                    )
                ],
            ),
            LessonPage(
                page_id="p3",
                page_type="quiz",
                title="Pick the right snack",
                instruction="Choose the correct answer for Ellie.",
                completion_label="Next page",
                components=[
                    LessonComponent(
                        component_id="encounter_1",
                        type="encounter_card",
                        title=f"Watch out for {monster.name if monster else 'Crumb Goblin'}",
                        prompt=f"{monster.name if monster else 'Crumb Goblin'} is trying to grab the snack first.",
                        payload={
                            "monster_name": monster.name if monster else "Crumb Goblin",
                            "companion_name": companion.name if companion else "Momo Fox",
                            "challenge": f"Choose {primary} so Ellie can win this round.",
                        },
                    ),
                    LessonComponent(
                        component_id="quiz_1",
                        type="choice_quiz",
                        title="Which word matches?",
                        prompt=f"Tap {primary}",
                        payload={"question": f"Tap {primary}", "options": options, "answer": primary},
                    ),
                    LessonComponent(
                        component_id="pet_reaction_2",
                        type="pet_reaction",
                        title="Ellie watches",
                        prompt="Ellie is waiting for your answer.",
                        payload={"emotion": "curious"},
                    ),
                ],
            ),
            LessonPage(
                page_id="p4",
                page_type="repeat",
                title="Say it with Ellie",
                instruction="Read the short sentence aloud, then continue.",
                completion_label="I said it",
                components=[
                    LessonComponent(
                        component_id="repeat_1",
                        type="repeat_prompt",
                        title="Repeat",
                        prompt=f"Ellie likes {primary}.",
                        payload={"text": f"Ellie likes {primary}."},
                    )
                ],
            ),
            LessonPage(
                page_id="p5",
                page_type="settlement",
                title="Reward time",
                instruction="See what you earned in this tiny game.",
                completion_label="See feeding page",
                components=[
                    LessonComponent(
                        component_id="reward_1",
                        type="reward_panel",
                        title="Rewards",
                        prompt="You helped Ellie.",
                        payload=blueprint.rewards,
                    )
                ],
            ),
            LessonPage(
                page_id="p6",
                page_type="feed_pet",
                title="Feed Ellie",
                instruction="Finish the lesson to save rewards, then Ellie can eat.",
                completion_label="Finish lesson",
                components=[
                    LessonComponent(
                        component_id="feed_1",
                        type="feed_panel",
                        title="Meal plan",
                        prompt="One basic meal is ready for Ellie.",
                        payload={"food_type": "basic_food", "quantity": 1},
                    ),
                    LessonComponent(
                        component_id="pet_reaction_3",
                        type="pet_reaction",
                        title="Ellie smiles",
                        prompt="Yay. Snack time soon.",
                        payload={"emotion": "excited"},
                    ),
                ],
            ),
        ]
        return LessonPackage(
            lesson_id=f"lesson-{uuid4().hex[:8]}",
            student_id=blueprint.student_id,
            title=blueprint.title,
            theme=blueprint.theme,
            estimated_minutes=max(4, min(8, len(pages))),
            vocab=[item.text for item in vocab],
            target_vocab_items=vocab,
            focus_tags=blueprint.focus_tags,
            teacher_note=blueprint.teacher_note,
            source_model="rules",
            reward_preview=blueprint.rewards,
            story=blueprint.story,
            pages=pages,
            debug_metadata={"blueprint_id": blueprint.blueprint_id, "planner": "rules", "generator": "rules"},
        )
