"""Dataclass контекста создания персонажа и агрегированных владений.

Тонкий модуль без imports из progression/proficiencies — разрывает циклы.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ResolvedGrants:
    """Агрегированные владения и гранты персонажа."""

    weapon_tokens: tuple[str, ...]
    armor_tokens: tuple[str, ...]
    tool_tokens: tuple[str, ...]
    skill_ids: tuple[str, ...]
    language_ids: tuple[str, ...]
    save_ids: tuple[str, ...]


@dataclass(frozen=True)
class CreationContext:
    """Параметры создания персонажа для единого resolve владений."""

    race_id: str
    subrace_id: str | None
    class_id: str
    background_id: str | None
    subclass_id: str | None
    level: int
    feat_ids: tuple[str, ...] = ()
    feat_choices: dict[str, dict[str, Any]] | None = None
    extra_skills: tuple[str, ...] = ()
    extra_weapon_tokens: tuple[str, ...] = ()
    extra_tool_tokens: tuple[str, ...] = ()
    extra_languages: tuple[str, ...] = ()
