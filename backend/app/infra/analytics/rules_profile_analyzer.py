from __future__ import annotations

from collections import Counter

from app.domain.interfaces.analytics import ProfileAnalyzer
from app.schemas.profile import ProfileSnapshot, RecentSessionSummary, SessionSignals


class RulesProfileAnalyzer(ProfileAnalyzer):
    def recompute(
        self,
        student_id: str,
        signals: SessionSignals,
        previous_profile: ProfileSnapshot | None = None,
        recent_sessions: list[RecentSessionSummary] | None = None,
    ) -> ProfileSnapshot:
        recent_sessions = recent_sessions or []
        block_counter = Counter(signals.preferred_block_types)
        for session in recent_sessions:
            block_counter.update(session.preferred_block_types)
        weak_vocab = list(previous_profile.weak_vocab_tags if previous_profile else [])
        if signals.wrong_count > 0 and "food" not in weak_vocab:
            weak_vocab.append("food")
        weak_skill = []
        if signals.speaking_attempts == 0:
            weak_skill.append("speaking")
        if signals.wrong_count >= max(1, signals.correct_count):
            weak_skill.append("listening")
        motivation = "high" if signals.duration_seconds >= 300 and signals.score >= 20 else "medium"
        frustration = "medium" if signals.wrong_count >= 2 else "low"
        preferred_theme = "feed_rabbit"
        if "repeat_prompt" in block_counter:
            preferred_theme = "pet_play"
        latest_focus = weak_vocab[:2] or list(previous_profile.latest_focus if previous_profile else [])[:2] or ["food"]
        story_arc_key = signals.story_arc_key or (previous_profile.story_arc_key if previous_profile else "snack_scouts")
        story_episode_index = max(signals.story_episode_index, previous_profile.story_episode_index if previous_profile else 0)
        story_last_scene = signals.story_last_scene or previous_profile.story_last_scene if previous_profile else signals.story_last_scene
        story_next_hook = signals.story_next_hook or previous_profile.story_next_hook if previous_profile else signals.story_next_hook
        story_characters = list(dict.fromkeys((signals.encountered_characters or []) + (previous_profile.story_characters if previous_profile else [])))[:5]
        return ProfileSnapshot(
            student_id=student_id,
            weak_vocab_tags=weak_vocab[:3],
            weak_skill_tags=weak_skill[:3],
            interest_tags=[name for name, _ in block_counter.most_common(3)] or ["pet_feeding"],
            preferred_themes=[preferred_theme],
            recommended_session_minutes=8 if motivation == "high" else 5,
            motivation_level=motivation,
            frustration_risk=frustration,
            current_level=previous_profile.current_level if previous_profile else "starter",
            latest_focus=latest_focus,
            recommended_vocab_keys=list(previous_profile.recommended_vocab_keys if previous_profile else [])[:4],
            summary_note="Rules-based profile update.",
            story_arc_key=story_arc_key,
            story_episode_index=story_episode_index,
            story_last_scene=story_last_scene or "Ellie finished a tiny snack mission.",
            story_next_hook=story_next_hook or "Ellie hears a new helper calling from the next garden.",
            story_characters=story_characters or ["Ellie", "Momo Fox", "Crumb Goblin"],
        )
