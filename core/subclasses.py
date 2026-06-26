"""Подклассы: правила выбора по режиму сложности и уровню."""

from typing import Any

from core.classes import get_subclass_choice_level
from core.levels import MAX_CHARACTER_LEVEL
from core.models import Character
from core.types import GameDifficulty

EASY_START_LEVEL = 3


def features_up_to_level(
    features: list[Any], max_level: int = MAX_CHARACTER_LEVEL
) -> list[dict[str, Any]]:
    """Отфильтровать умения с level <= max_level."""
    result: list[dict[str, Any]] = []
    for feat in features:
        if not isinstance(feat, dict):
            continue
        level = feat.get("level")
        if isinstance(level, int) and level > max_level:
            continue
        result.append(feat)
    return result


def start_level_for_difficulty(difficulty: GameDifficulty) -> int:
    """Стартовый уровень персонажа при создании."""
    if difficulty == "easy":
        return EASY_START_LEVEL
    return 1


def subclass_offered_at_creation(
    difficulty: GameDifficulty,
    class_id: str,
    start_level: int | None = None,
) -> bool:
    """Нужен ли экран выбора подкласса при создании персонажа."""
    if start_level is None:
        start_level = start_level_for_difficulty(difficulty)
    choice_level = get_subclass_choice_level(class_id)

    match difficulty:
        case "easy":
            return start_level >= choice_level
        case "normal":
            return True
        case "hardcore":
            return choice_level <= start_level


def subclass_is_active(character: Character) -> bool:
    """Подкласс механически активен на текущем уровне."""
    if character.subclass_id is None:
        return False
    return character.level >= get_subclass_choice_level(character.class_name)


def needs_subclass_npc(character: Character) -> bool:
    """HardCore-персонажу нужен NPC-наставник для выбора подкласса."""
    if character.difficulty != "hardcore":
        return False
    if character.subclass_id is not None:
        return False
    choice_level = get_subclass_choice_level(character.class_name)
    if choice_level <= 1:
        return False
    return character.level >= choice_level
