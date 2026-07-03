"""Параметры создания персонажа для упрощения сигнатур функций.

Используется вместо длинного списка параметров в build_new_character.
"""

from collections.abc import Callable
from dataclasses import dataclass
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
    unique_save_slug: Callable[[str], str] = lambda name: name

    def to_kwargs(self) -> dict[str, Any]:
        """Преобразовать в kwargs для совместимости с существующим API.

        Создает копии mutable объектов для предотвращения случайной мутации.
        """
        return {
            "name": self.name,
            "race_id": self.race_id,
            "class_id": self.class_id,
            "difficulty": self.difficulty,
            "subrace_id": self.subrace_id,
            "stats": dict(self.stats) if self.stats else None,
            "subclass_id": self.subclass_id,
            "languages": list(self.languages) if self.languages else None,
            "background_id": self.background_id,
            "skills": list(self.skills) if self.skills else None,
            "skill_expertise": (
                list(self.skill_expertise) if self.skill_expertise else None
            ),
            "tool_expertise": (
                list(self.tool_expertise) if self.tool_expertise else None
            ),
            "weapon_proficiencies": (
                list(self.weapon_proficiencies)
                if self.weapon_proficiencies
                else None
            ),
            "armor_proficiencies": (
                list(self.armor_proficiencies)
                if self.armor_proficiencies
                else None
            ),
            "tool_proficiencies": (
                list(self.tool_proficiencies)
                if self.tool_proficiencies
                else None
            ),
            "background_tool_picks": (
                list(self.background_tool_picks)
                if self.background_tool_picks
                else None
            ),
            "feat_ids": list(self.feat_ids) if self.feat_ids else None,
            "feat_choices": (
                {k: dict(v) for k, v in self.feat_choices.items()}
                if self.feat_choices
                else None
            ),
            "asi_choices": (
                dict(self.asi_choices) if self.asi_choices else None
            ),
            "save_proficiencies": (
                list(self.save_proficiencies)
                if self.save_proficiencies
                else None
            ),
            "inventory": (list(self.inventory) if self.inventory else None),
            "equipment_choices": (
                dict(self.equipment_choices)
                if self.equipment_choices
                else None
            ),
            "level": self.level,
            "class_features_applied": self.class_features_applied,
            "apply_feat_stat_bonuses": self.apply_feat_stat_bonuses,
            "unique_save_slug": self.unique_save_slug,
        }
