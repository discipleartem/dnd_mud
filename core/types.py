"""Общие типы домена (PEP 695 / PEP 692)."""

from enum import StrEnum
from typing import Any, Literal, TypedDict

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
