"""Параметры создания персонажа для упрощения сигнатур функций.

Используется вместо длинного списка параметров в build_new_character.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from core.types import (
    CharacterClass,
    GameDifficulty,
    InventoryItem,
    StatMap,
)


@dataclass
class CharacterBuildParams:
    """Параметры для сборки нового персонажа.

    Заменяет длинный список параметров в build_new_character.
    Все параметры опциональны и имеют разумные значения по умолчанию.
    """

    name: str
    race_id: str
    class_id: str | CharacterClass
    difficulty: GameDifficulty = "normal"
    subrace_id: str | None = None
    stats: StatMap | None = None
    subclass_id: str | None = None
    languages: list[str] | None = None
    background_id: str | None = None
    skills: list[str] | None = None
    skill_expertise: list[str] | None = None
    tool_expertise: list[str] | None = None
    weapon_proficiencies: list[str] | None = None
    armor_proficiencies: list[str] | None = None
    tool_proficiencies: list[str] | None = None
    background_tool_picks: list[str] | None = None
    feat_ids: list[str] | None = None
    feat_choices: dict[str, dict[str, Any]] | None = None
    asi_choices: dict[str, str] | None = None
    save_proficiencies: list[str] | None = None
    inventory: list[InventoryItem] | None = None
    equipment_choices: dict[str, str] | None = None
    level: int | None = None
    class_features_applied: bool = False
    apply_feat_stat_bonuses: bool = True
    unique_save_slug: Callable[[str], str] = field(default=lambda name: name)

    def to_kwargs(self) -> dict[str, Any]:
        """Преобразовать в kwargs для совместимости с существующим API."""
        return {
            "name": self.name,
            "race_id": self.race_id,
            "class_id": self.class_id,
            "difficulty": self.difficulty,
            "subrace_id": self.subrace_id,
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
            "background_tool_picks": self.background_tool_picks,
            "feat_ids": self.feat_ids,
            "feat_choices": self.feat_choices,
            "asi_choices": self.asi_choices,
            "save_proficiencies": self.save_proficiencies,
            "inventory": self.inventory,
            "equipment_choices": self.equipment_choices,
            "level": self.level,
            "class_features_applied": self.class_features_applied,
            "apply_feat_stat_bonuses": self.apply_feat_stat_bonuses,
            "unique_save_slug": self.unique_save_slug,
        }
