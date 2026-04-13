#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib import request


def post_json(api_base: str, path: str, payload: dict) -> dict:
    req = request.Request(
        f"{api_base.rstrip('/')}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_step_results(steps: list[dict], episode: int) -> list[dict]:
    results: list[dict] = []
    for step in steps:
        template_id = str(step.get("template_id") or "")
        details: dict = {}
        correct: bool | None = True
        score = 10

        if template_id == "story_choice":
            choices = step.get("slots", {}).get("choices", [])
            choice = choices[(episode - 1) % len(choices)] if choices else {"key": "default", "text": "default", "consequence_tag": "neutral"}
            details = {
                "chosen_key": choice.get("key", "default"),
                "chosen_text": choice.get("text", "default"),
                "consequence_tag": choice.get("consequence_tag", "neutral"),
            }
            score = 12
        elif template_id == "listen_pick":
            slots = step.get("slots", {})
            correct_key = str(slots.get("correct_key") or "")
            # Alternate one incorrect attempt to demonstrate weak vocab signals.
            selected = correct_key if episode % 2 == 0 else "wrong_pick"
            correct = selected == correct_key
            details = {
                "audio_text": slots.get("audio_text", ""),
                "correct_key": correct_key,
                "selected_key": selected,
            }
            score = 20 if correct else 0
        elif template_id == "drag_match":
            pairs = step.get("slots", {}).get("pairs", [])
            target_word = pairs[0].get("left", "") if pairs else ""
            details = {"target_word": target_word}
            score = 30
        elif template_id == "choice_battle":
            score = 35
        else:
            score = 8

        results.append(
            {
                "step_id": step.get("step_id", ""),
                "template_id": template_id,
                "correct": correct,
                "score": score,
                "duration_ms": 1200,
                "details": details,
            }
        )
    return results


def to_block_results(step_results: list[dict]) -> list[dict]:
    return [
        {
            "block_id": item["step_id"],
            "block_type": item["template_id"],
            "correct": True if item["correct"] is None else bool(item["correct"]),
            "score": int(item["score"]),
            "duration_ms": int(item["duration_ms"]),
        }
        for item in step_results
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 3-lesson continuous story demo data")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000/api/v1")
    parser.add_argument("--student-id", default="student-story-demo")
    parser.add_argument("--output", default="docs/samples/three_lesson_story_demo.json")
    args = parser.parse_args()

    episodes: list[dict] = []
    requested_vocab: list[str] = ["apple", "milk", "hungry"]

    for episode in (1, 2, 3):
        lesson_resp = post_json(
            args.api_base,
            "/lessons/next",
            {
                "student_id": args.student_id,
                "requested_vocab": requested_vocab,
                "lesson_type": "pet_feeding",
                "level_hint": "starter",
                "force_regenerate": True,
            },
        )
        lesson = lesson_resp["lesson"]
        steps = lesson.get("steps", [])
        step_results = build_step_results(steps, episode)
        block_results = to_block_results(step_results)
        total_score = sum(item["score"] for item in block_results)

        complete_resp = post_json(
            args.api_base,
            "/sessions/complete",
            {
                "student_id": args.student_id,
                "lesson_id": lesson["lesson_id"],
                "duration_seconds": 280,
                "total_score": total_score,
                "earned_food": int(lesson.get("reward_preview", {}).get("food", 1)),
                "earned_coins": int(lesson.get("reward_preview", {}).get("coins", 3)),
                "story_arc_key": lesson["story"]["arc_key"],
                "story_episode_index": lesson["story"]["episode_index"],
                "story_last_scene": lesson["story"]["current_mission"],
                "story_next_hook": lesson["story"]["next_hook"],
                "encountered_characters": [item.get("name", "") for item in lesson["story"].get("characters", [])],
                "block_results": block_results,
                "step_results": step_results,
            },
        )

        next_reco = complete_resp.get("next_recommendation", {})
        requested_vocab = list(next_reco.get("recommended_vocab_keys") or requested_vocab)

        episodes.append(
            {
                "episode_run": episode,
                "lesson_id": lesson["lesson_id"],
                "story": lesson["story"],
                "step_templates": [item.get("template_id") for item in steps],
                "selected_story_choice": next(
                    (
                        item["details"]
                        for item in step_results
                        if item.get("template_id") == "story_choice" and item.get("details")
                    ),
                    {},
                ),
                "next_recommendation": next_reco,
            }
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "student_id": args.student_id,
                "episodes": episodes,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[OK] wrote demo to {output_path}")


if __name__ == "__main__":
    main()

