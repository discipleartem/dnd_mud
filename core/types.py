"""Общие типы домена (PEP 695 / PEP 692)."""

from enum import StrEnum
from typing import Any, Literal, NotRequired, TypedDict

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
