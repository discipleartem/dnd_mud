"""Общие типы домена (PEP 695 / PEP 692)."""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal, NotRequired, TypedDict

# ============================================================================
# Базовые типы
# ============================================================================

type StatMap = dict[str, int]
type StringsDict = dict[str, Any]
type GameDifficulty = Literal["easy", "normal", "hardcore"]
type LanguageCode = Literal["ru", "en"]


class CharacterClass(StrEnum):
    """Идентификаторы классов из ``database/classes/classes.yaml``."""

    FIGHTER = "fighter"
    ROGUE = "rogue"
    CLERIC = "cleric"
    BARD = "bard"


class RuntimeSettings(TypedDict):
    """Runtime-настройки пользователя."""

    language: LanguageCode


class InventoryItem(TypedDict):
    """Элемент инвентаря персонажа (save JSON)."""

    kind: str
    id: str
    qty: NotRequired[int]


class EquippedState(TypedDict, total=False):
    """Слоты экипировки на персонаже."""

    armor: str | None
    main_hand: str | None
    off_hand: str | None
    shield: bool
    main_hand_grip: Literal["one_handed", "two_handed"]


# ============================================================================
# Параметры создания персонажа
# ============================================================================


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


# ============================================================================
# Типы для владений и компетентности
# ============================================================================


@dataclass
class Proficiencies:
    """Владения персонажа: оружием, доспехами, инструментами."""

    weapons: list[str] = field(default_factory=list)
    armor: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)

    def to_lists(self) -> tuple[list[str], list[str], list[str]]:
        """Преобразовать в кортеж списков для совместимости с API."""
        return self.weapons, self.armor, self.tools

    @classmethod
    def from_lists(
        cls,
        weapons: list[str] | None = None,
        armor: list[str] | None = None,
        tools: list[str] | None = None,
    ) -> "Proficiencies":
        """Создать из списков для совместимости с существующим API."""
        return cls(
            weapons=list(weapons) if weapons else [],
            armor=list(armor) if armor else [],
            tools=list(tools) if tools else [],
        )


@dataclass
class Expertise:
    """Компетентность персонажа: навыки и инструменты."""

    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)

    def to_lists(self) -> tuple[list[str], list[str]]:
        """Преобразовать в кортеж списков для совместимости с API."""
        return self.skills, self.tools

    @classmethod
    def from_lists(
        cls,
        skills: list[str] | None = None,
        tools: list[str] | None = None,
    ) -> "Expertise":
        """Создать из списков для совместимости с существующим API."""
        return cls(
            skills=list(skills) if skills else [],
            tools=list(tools) if tools else [],
        )


__all__ = [
    "CharacterBuildParams",
    "CharacterClass",
    "EquippedState",
    "Expertise",
    "GameDifficulty",
    "InventoryItem",
    "LanguageCode",
    "Proficiencies",
    "RuntimeSettings",
    "StatMap",
    "StringsDict",
]
