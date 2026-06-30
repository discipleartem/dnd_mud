"""Тесты подклассов и правил выбора по сложности."""

from typing import Literal

import pytest

from core.classes import get_subclass_choice_level, load_class_full
from core.models import Character
from core.subclasses import (
    features_up_to_level,
    needs_subclass_npc,
    start_level_for_difficulty,
    subclass_is_active,
    subclass_offered_at_creation,
)


@pytest.mark.parametrize(
    "class_id,expected",
    [("cleric", 1), ("fighter", 3)],
)
def test_subclass_choice_level(class_id: str, expected: int) -> None:
    assert get_subclass_choice_level(class_id) == expected


@pytest.mark.parametrize(
    "difficulty,expected",
    [("easy", 3), ("normal", 1)],
)
def test_start_level_for_difficulty(
    difficulty: Literal["easy", "normal", "hardcore"], expected: int
) -> None:
    assert start_level_for_difficulty(difficulty) == expected


@pytest.mark.parametrize(
    "difficulty,class_id,level,offered",
    [
        ("normal", "fighter", 1, True),
        ("hardcore", "fighter", 1, False),
        ("hardcore", "cleric", 1, True),
    ],
)
def test_subclass_offered_at_creation(
    difficulty: Literal["easy", "normal", "hardcore"],
    class_id: str,
    level: int,
    offered: bool,
) -> None:
    assert subclass_offered_at_creation(difficulty, class_id, level) is offered


def test_subclass_pending_until_level_three() -> None:
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=1,
        subclass_id="champion",
        difficulty="normal",
    )
    assert subclass_is_active(char) is False
    char.level = 3
    assert subclass_is_active(char) is True


@pytest.mark.parametrize(
    "class_id,level,needs_npc",
    [("fighter", 3, True), ("cleric", 1, False)],
)
def test_needs_subclass_npc_hardcore(
    class_id: str, level: int, needs_npc: bool
) -> None:
    char = Character(
        name="Hero",
        race="human",
        class_id=class_id,
        level=level,
        difficulty="hardcore",
    )
    assert needs_subclass_npc(char) is needs_npc


def test_features_up_to_level_filters_high_levels() -> None:
    features = [
        {"id": "a", "level": 3, "name": "A"},
        {"id": "b", "level": 11, "name": "B"},
    ]
    filtered = features_up_to_level(features)
    assert len(filtered) == 1
    assert filtered[0]["id"] == "a"


def test_class_features_exclude_subclass_abilities() -> None:
    fighter = load_class_full("fighter", "ru")
    assert "Улучшенная критическая атака" not in {
        f.get("name") for f in fighter.get("features", [])
    }
    bard = load_class_full("bard", "ru")
    bard_names = {f.get("name") for f in bard.get("features", [])}
    assert "Вдохновляющая защитная мантия" not in bard_names
    assert "Мастер на все руки" in bard_names
