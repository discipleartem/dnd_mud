"""Общие типы домена (PEP 695 / PEP 692)."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal, NotRequired, TypedDict

# ============================================================================
# Базовые типы
# ============================================================================

type StatMap = dict[str, int]
type StringsDict = dict[str, Any]
type GameDifficulty = Literal["easy", "normal", "hardcore"]
type LanguageCode = Literal["ru", "en"]


def parse_game_difficulty(raw: object) -> GameDifficulty:
    """Режим сложности из JSON или другого сырого значения."""
    if raw == "hardcore":
        return "hardcore"
    if raw == "easy":
        return "easy"
    return "normal"


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

    Опциональные поля имеют значения по умолчанию.
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


__all__ = [
    "CharacterBuildParams",
    "CharacterClass",
    "EquippedState",
    "GameDifficulty",
    "InventoryItem",
    "parse_game_difficulty",
    "LanguageCode",
    "RuntimeSettings",
    "StatMap",
    "StringsDict",
]
