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


def test_feat_id_from_asi_choice() -> None:
    assert feat_id_from_asi_choice("feat:resilient") == "resilient"
    assert feat_id_from_asi_choice("asi") is None


@pytest.mark.parametrize(
    "class_id,level,expected",
    [("fighter", 4, True), ("fighter", 5, False), ("rogue", 10, True)],
)
def test_class_grants_asi_at_level(
    class_id: str, level: int, expected: bool
) -> None:
    assert class_grants_asi_at_level(class_id, level) is expected


def test_apply_asi_and_cap() -> None:
    stats = {"strength": 19, "dexterity": 10}
    assert cap_stats(apply_asi_two_one(stats, "strength"))["strength"] == 20
    updated = apply_asi_one_two(
        {"strength": 14, "dexterity": 12}, "strength", "dexterity"
    )
    assert updated["strength"] == 15
    assert updated["dexterity"] == 13


def test_pending_asi_at_level() -> None:
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
    assert (
        con_hp_bonus_from_asi({"constitution": 14}, {"constitution": 16}, 8)
        == 8
    )
