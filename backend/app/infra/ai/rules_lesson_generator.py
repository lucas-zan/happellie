from __future__ import annotations

from uuid import uuid4

from app.domain.interfaces.lesson import LessonGenerator
from app.schemas.lesson import GameStep, LessonBlueprint, LessonComponent, LessonPackage, LessonPage


class RulesLessonGenerator(LessonGenerator):
    def generate(self, blueprint: LessonBlueprint) -> LessonPackage:
        vocab = blueprint.target_vocab
        primary = vocab[0].text if vocab else "apple"
        options = [item.text for item in vocab[:3]] or [primary, "milk", "banana"]
        companion = next((character for character in blueprint.story.characters if character.kind in {"animal", "companion"}), None)
        monster = next((character for character in blueprint.story.characters if character.kind == "monster"), None)
        branch_tag = blueprint.story.last_choice_tag or ""
        chapter_key = blueprint.story.chapter_key or "chapter_1"
        branch_route = "default"
        if branch_tag == "adventure":
            branch_route = "adventure_route"
        elif branch_tag == "safe_food":
            branch_route = "safe_route"
        # v3 steps: template-engine friendly flow (kept in addition to legacy pages).
        steps: list[GameStep] = [
            GameStep(
                step_id="s1",
                template_id="story_dialogue",
                title="Story time",
                slots={
                    "background": "moon_bridge" if blueprint.story.arc_key == "moon_garden" else "sea_coast" if blueprint.story.arc_key == "ocean_picnic" else "forest_path",
                    "dialogues": [
                        {"character": "foxy", "mood": "excited", "line": blueprint.story.recap or "A tiny adventure begins."},
                        {"character": "ellie", "mood": "curious", "line": blueprint.story.current_mission or "Let's help Ellie!"},
                    ],
                },
                is_interactive=False,
            ),
            GameStep(
                step_id="s2",
                template_id="story_choice",
                title="Choose the path",
                slots={
                    "background": "forest_split_road",
                    "character": {
                        "id": "foxy" if blueprint.story.arc_key == "snack_scouts" else "owl" if blueprint.story.arc_key == "moon_garden" else "bear",
                        "mood": "curious",
                        "line": "Which path should we take?",
                    },
                    "scenario": (
                        "Last time you chose an adventure path. Do we keep exploring deeper?"
                        if branch_route == "adventure_route"
                        else "Last time you chose the fruit path. Do we protect snacks or explore a shortcut?"
                        if branch_route == "safe_route"
                        else "Ellie and Foxy found two paths. One path has fruit trees, one has a tiny cave."
                    ),
                    "choices": [
                        {"key": "fruit_path", "text": "Go to the fruit trees", "consequence_tag": "safe_food"},
                        {"key": "cave_path", "text": "Explore the tiny cave", "consequence_tag": "adventure"},
                        {"key": "both", "text": "Check both quickly", "consequence_tag": "balanced"},
                    ],
                },
                is_interactive=True,
                reward_on_complete={"coins": 2},
            ),
            GameStep(
                step_id="s3",
                template_id="word_reveal",
                title="New word",
                slots={
                    "word": primary,
                    "meaning": next((item.meaning for item in vocab if item.text == primary), ""),
                    "image_hint": primary,
                    "audio_text": primary,
                    "sentence": f"Ellie likes {primary}.",
                    "character": {"id": "ellie", "mood": "happy", "line": f"Say: {primary}!"},
                },
                is_interactive=False,
            ),
        ]
        if branch_route == "adventure_route":
            steps.append(
                GameStep(
                    step_id="s3b",
                    template_id="word_in_scene",
                    title="Find clues in scene",
                    slots={
                        "scene_hint": "cave_gate",
                        "hidden_words": [
                            {"word": primary, "meaning": next((item.meaning for item in vocab if item.text == primary), ""), "position_hint": "left_rock"},
                        ],
                    },
                    is_interactive=False,
                )
            )
        elif branch_route == "safe_route":
            steps.append(
                GameStep(
                    step_id="s3b",
                    template_id="mission_briefing",
                    title="Protect the orchard",
                    slots={
                        "companion": {"id": "foxy", "mood": "determined", "line": "Let's protect the snacks."},
                        "objectives": [f"Find {primary}", "Avoid the snack thief", "Feed Ellie safely"],
                    },
                    is_interactive=False,
                )
            )

        steps.extend(
            [
            GameStep(
                step_id="s4",
                template_id="listen_pick",
                title="Listen and pick",
                slots={
                    "character": {"id": "foxy", "mood": "determined", "line": "Listen! Pick the right one."},
                    "audio_text": primary,
                    "options": [{"key": opt, "image_hint": opt} for opt in options],
                    "correct_key": primary,
                    "success_line": "Yes! Great ears!",
                    "fail_line": f"Oops. It's {primary}.",
                },
                is_interactive=True,
                reward_on_complete={"coins": 3},
            ),
            GameStep(
                step_id="s5",
                template_id="drag_match",
                title="Match challenge",
                slots={
                    "character": {"id": "foxy", "mood": "curious", "line": "Drag and match the pairs."},
                    "pairs": [
                        {"left": item.text, "right": item.meaning}
                        for item in vocab[: min(3, len(vocab))]
                    ],
                    "match_type": "text_to_text",
                },
                is_interactive=True,
                reward_on_complete={"coins": 5},
            ),
            GameStep(
                step_id="s6",
                template_id="choice_battle",
                title="Boss battle",
                slots={
                    "monster": {"id": "snack_thief", "name": monster.name if monster else "Crumb Goblin", "hp": 3},
                    "companion": {"id": "foxy", "mood": "determined", "line": "Answer to attack!"},
                    "rounds": [
                        {"question": f"Tap {primary}", "options": options, "answer": primary, "round_type": "text"},
                        {"question": f"What does '{primary}' mean?", "options": [blueprint.target_vocab[0].meaning if vocab else "苹果", "牛奶", "球"], "answer": blueprint.target_vocab[0].meaning if vocab else "苹果", "round_type": "text"},
                    ],
                    "victory_line": "You win!",
                    "defeat_line": "Nice try!",
                },
                is_interactive=True,
                reward_on_complete={"coins": int(blueprint.rewards.get("coins") or 4)},
            ),
            GameStep(
                step_id="s7",
                template_id="reward_chest",
                title="Rewards",
                slots={
                    "total_coins": int(blueprint.rewards.get("coins") or 4),
                    "total_food": {"basic_food": int(blueprint.rewards.get("food") or 1)},
                    "bonus_item": None,
                    "chapter_key": chapter_key,
                },
                is_interactive=False,
            ),
            GameStep(
                step_id="s8",
                template_id="feed_pet_step",
                title="Feed Ellie",
                slots={"available_food": {"basic_food": int(blueprint.rewards.get("food") or 1)}, "pet_current_mood": "hungry"},
                is_interactive=True,
            ),
            GameStep(
                step_id="s9",
                template_id="episode_end",
                title="The end",
                slots={
                    "episode_summary": f"You learned {primary} and helped Ellie!",
                    "next_hook": blueprint.story.next_hook or "A new friend may appear next time.",
                    "next_episode_hint": f"{chapter_key} · Episode {blueprint.story.episode_index + 1}",
                    "chapter_key": chapter_key,
                    "companion_farewell": {"id": "foxy", "mood": "winking", "line": "See you next time!"},
                },
                is_interactive=False,
            ),
            ]
        )
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
            steps=steps,
            debug_metadata={
                "blueprint_id": blueprint.blueprint_id,
                "planner": "rules",
                "generator": "rules",
                "branch_route": branch_route,
                "branch_tag": branch_tag,
                "chapter_key": chapter_key,
            },
        )
