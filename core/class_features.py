"""Отложенные особенности класса и подкласса при активации архетипа."""

from dataclasses import replace

from core.models import Character
from core.skills import subclass_skills_active
from core.subclasses import subclass_is_active


def class_features_applied_at_creation(
    class_id: str, subclass_id: str | None, start_level: int
) -> bool:
    """Особенности подкласса выбраны при создании (старт >= ур. архетипа)."""
    return subclass_skills_active(class_id, subclass_id, start_level)


def needs_class_feature_picks(character: Character) -> bool:
    """Нужен выбор особенностей класса/подкласса (наставник, сценарий)."""
    if not subclass_is_active(character):
        return False
    return not character.class_features_applied


def subclass_skill_picks_pending(character: Character) -> bool:
    """Ещё не выбраны навыки подкласса."""
    from core.skills import get_subclass_skill_choices

    if not character.subclass_id:
        return False
    return bool(
        get_subclass_skill_choices(
            character.class_id,
            character.subclass_id,
            character.level,
        )
    )


def mark_class_features_applied(character: Character) -> Character:
    """Пометить особенности класса/подкласса как применённые."""
    return replace(character, class_features_applied=True)
