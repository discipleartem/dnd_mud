"""Общие типы домена (PEP 695 / PEP 692)."""

from typing import Any, Literal, TypedDict

type StatMap = dict[str, int]
type StringsDict = dict[str, Any]
type GameDifficulty = Literal["normal", "hardcore"]
type LanguageCode = Literal["ru", "en"]


class RuntimeSettings(TypedDict):
    """Runtime-настройки пользователя."""

    language: LanguageCode
