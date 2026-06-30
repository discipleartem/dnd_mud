"""Тесты увеличения характеристик (ASI)."""

import pytest

from core.asi import (
    apply_asi_one_two,
    apply_asi_two_one,
    cap_stats,
    class_grants_asi_at_level,
    con_hp_bonus_from_asi,
    feat_id_from_asi_choice,
    pending_asi_at_level,
)
from core.models import Character


def test_feat_id_from_asi_choice():
    assert feat_id_from_asi_choice("feat:resilient") == "resilient"
    assert feat_id_from_asi_choice("feat:tough") == "tough"
    assert feat_id_from_asi_choice("feat:") is None
    assert feat_id_from_asi_choice("asi") is None


@pytest.mark.parametrize(
    "class_id,level,expected",
    [
        ("fighter", 4, True),
        ("fighter", 6, True),
        ("fighter", 5, False),
        ("rogue", 10, True),
        ("rogue", 9, False),
    ],
)
def test_class_grants_asi_at_level(
    class_id: str, level: int, expected: bool
) -> None:
    assert class_grants_asi_at_level(class_id, level) is expected


def test_apply_asi_two_one_and_cap():
    stats = {"strength": 19, "dexterity": 10}
    updated = cap_stats(apply_asi_two_one(stats, "strength"))
    assert updated["strength"] == 20


def test_apply_asi_one_two():
    stats = {"strength": 14, "dexterity": 12}
    updated = apply_asi_one_two(stats, "strength", "dexterity")
    assert updated["strength"] == 15
    assert updated["dexterity"] == 13


@pytest.mark.parametrize(
    "old_con,new_con,level,expected_bonus",
    [
        (14, 16, 8, 8),
        (13, 14, 7, 7),
        (13, 14, 8, 8),
    ],
)
def test_con_hp_bonus_from_asi(
    old_con: int, new_con: int, level: int, expected_bonus: int
) -> None:
    old = {"constitution": old_con}
    new = {"constitution": new_con}
    assert con_hp_bonus_from_asi(old, new, level) == expected_bonus


def test_pending_asi_at_level():
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        stats={"strength": 16},
        current_hp=20,
        max_hp=20,
    )
    assert pending_asi_at_level(char, 4)
    char_done = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=4,
        stats={"strength": 18},
        current_hp=28,
        max_hp=28,
        asi_choices={"4": "asi"},
    )
    assert not pending_asi_at_level(char_done, 4)
