"""Состояние и типы flow создания персонажа."""

from dataclasses import dataclass, field
from typing import Any, Literal

from core.class_features import class_features_applied_at_creation
from core.subclasses import start_level_for_difficulty
from core.types import GameDifficulty, StatMap

CreationStep = Literal[
    "race",
    "subrace",
    "languages",
    "stats",
    "background",
    "feats",
    "class",
    "subclass",
    "proficiencies",
    "skills",
    "expertise",
    "equipment",
]


@dataclass
class _CreationState:
    """Состояние пошагового создания персонажа."""

    name: str
    difficulty: GameDifficulty
    race_id: str | None = None
    subrace_id: str | None = None
    languages: list[str] | None = None
    stats: StatMap | None = None
    background_id: str | None = None
    background_skills: list[str] = field(default_factory=list)
    class_id: str | None = None
    subclass_id: str | None = None
    skills: list[str] | None = None
    skill_expertise: list[str] | None = None
    tool_expertise: list[str] | None = None
    weapon_proficiencies: list[str] | None = None
    armor_proficiencies: list[str] | None = None
    tool_proficiencies: list[str] | None = None
    background_tool_picks: list[str] = field(default_factory=list)
    equipment_choices: dict[str, str] = field(default_factory=dict)
    feat_ids: list[str] = field(default_factory=list)
    feat_choices: dict[str, dict[str, Any]] = field(default_factory=dict)
    hardcore_rolls: list[int] = field(default_factory=list)

    @property
    def start_level(self) -> int:
        """Стартовый уровень по сложности (вычисляется один раз на чтение)."""
        return start_level_for_difficulty(self.difficulty)

    def save_kwargs(self) -> dict[str, Any]:
        """Аргументы для save_character из состояния создания."""
        if self.race_id is None or self.stats is None or self.class_id is None:
            return {}
        start_level = self.start_level
        features_applied = class_features_applied_at_creation(
            self.class_id, self.subclass_id, start_level
        )
        return {
            "name": self.name,
            "race_id": str(self.race_id),
            "class_id": str(self.class_id),
            "difficulty": self.difficulty,
            "subrace_id": str(self.subrace_id) if self.subrace_id else None,
            "stats": self.stats,
            "subclass_id": self.subclass_id,
            "languages": self.languages,
            "background_id": self.background_id,
            "skills": self.skills,
            "skill_expertise": self.skill_expertise,
            "tool_expertise": self.tool_expertise,
            "weapon_proficiencies": self.weapon_proficiencies,
            "armor_proficiencies": self.armor_proficiencies,
            "tool_proficiencies": self.tool_proficiencies,
            "background_tool_picks": self.background_tool_picks or None,
            "equipment_choices": self.equipment_choices or None,
            "feat_ids": self.feat_ids or None,
            "feat_choices": self.feat_choices or None,
            "class_features_applied": features_applied,
            "apply_feat_stat_bonuses": False,
        }
