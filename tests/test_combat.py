"""Тесты боевой механики."""

from core.combat import (
    armor_wearing_penalty,
    attack_roll_modifier,
    compute_ac,
)
from core.models import Character


def _fighter_with_weapons() -> Character:
    return Character(
        name="Test",
        race="human",
        class_name="fighter",
        stats={
            "strength": 16,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        },
        weapon_proficiencies=["simple", "martial"],
        armor_proficiencies=["light", "medium", "heavy", "shield"],
    )


def test_attack_with_proficiency_includes_pb():
    """Владение оружием — бонус мастерства в атаке."""
    char = _fighter_with_weapons()
    mod = attack_roll_modifier(char, "longsword")
    assert mod == 5  # +3 str +2 PB


def test_attack_without_proficiency_no_pb():
    """Без владения — нет бонуса мастерства."""
    char = Character(
        name="M",
        race="human",
        class_name="wizard",
        stats={"strength": 10},
        weapon_proficiencies=[],
    )
    mod = attack_roll_modifier(char, "longsword")
    assert mod == 0


def test_armor_penalty_without_proficiency():
    """Доспех без владения — штраф."""
    char = Character(
        name="M",
        race="human",
        class_name="wizard",
        armor_proficiencies=[],
    )
    assert armor_wearing_penalty(char, "plate") is True


def test_armor_penalty_with_proficiency():
    """Доспех с владением — без штрафа."""
    char = _fighter_with_weapons()
    assert armor_wearing_penalty(char, "plate") is False


def test_compute_ac_leather():
    """КД в кожаном доспехе."""
    char = _fighter_with_weapons()
    ac = compute_ac(char, "leather")
    assert ac == 13  # 11 + 2 dex


def test_compute_ac_unarmored():
    """КД без доспеха."""
    char = _fighter_with_weapons()
    ac = compute_ac(char, None)
    assert ac == 12  # 10 + 2 dex
