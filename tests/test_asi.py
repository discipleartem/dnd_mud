"""Тесты увеличения характеристик (ASI)."""

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


def test_class_grants_asi_at_level_fighter():
    assert class_grants_asi_at_level("fighter", 4)
    assert class_grants_asi_at_level("fighter", 6)
    assert not class_grants_asi_at_level("fighter", 5)


def test_class_grants_asi_at_level_rogue():
    assert class_grants_asi_at_level("rogue", 10)
    assert not class_grants_asi_at_level("rogue", 9)


def test_apply_asi_two_one_and_cap():
    stats = {"strength": 19, "dexterity": 10}
    updated = cap_stats(apply_asi_two_one(stats, "strength"))
    assert updated["strength"] == 20


def test_apply_asi_one_two():
    stats = {"strength": 14, "dexterity": 12}
    updated = apply_asi_one_two(stats, "strength", "dexterity")
    assert updated["strength"] == 15
    assert updated["dexterity"] == 13


def test_con_hp_bonus_from_asi():
    old = {"constitution": 14}
    new = {"constitution": 16}
    assert con_hp_bonus_from_asi(old, new, 8) == 8


def test_con_hp_bonus_from_asi_uses_reached_level():
    """При левелапе 7→8 передаётся new_level=8, не текущий char.level=7."""
    old = {"constitution": 13}
    new = {"constitution": 14}
    assert con_hp_bonus_from_asi(old, new, 7) == 7
    assert con_hp_bonus_from_asi(old, new, 8) == 8


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
