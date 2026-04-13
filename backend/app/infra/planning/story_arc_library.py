from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArcSpec:
    arc_key: str
    arc_title: str
    companion_name: str
    monster_name: str
    intro_recap: str
    chapters: tuple[str, str, str]


ARC_LIBRARY: dict[str, ArcSpec] = {
    "snack_scouts": ArcSpec(
        arc_key="snack_scouts",
        arc_title="Snack Scouts",
        companion_name="Momo Fox",
        monster_name="Crumb Goblin",
        intro_recap="Ellie started a tiny snack adventure.",
        chapters=("chapter_1", "chapter_2", "chapter_3"),
    ),
    "moon_garden": ArcSpec(
        arc_key="moon_garden",
        arc_title="Moon Garden",
        companion_name="Pip Owl",
        monster_name="Night Moth",
        intro_recap="Ellie entered the moon garden to collect glowing snacks.",
        chapters=("chapter_1", "chapter_2", "chapter_3"),
    ),
    "ocean_picnic": ArcSpec(
        arc_key="ocean_picnic",
        arc_title="Ocean Picnic",
        companion_name="Bobo Seal",
        monster_name="Wave Bandit",
        intro_recap="Ellie is preparing a seaside picnic adventure.",
        chapters=("chapter_1", "chapter_2", "chapter_3"),
    ),
}


def resolve_arc(arc_key: str | None) -> ArcSpec:
    if arc_key and arc_key in ARC_LIBRARY:
        return ARC_LIBRARY[arc_key]
    return ARC_LIBRARY["snack_scouts"]


def chapter_by_episode(spec: ArcSpec, episode_index: int) -> str:
    if episode_index <= 2:
        return spec.chapters[0]
    if episode_index <= 4:
        return spec.chapters[1]
    return spec.chapters[2]
