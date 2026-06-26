"""Тесты прогрессии и потолка уровня."""

from core.levels import MAX_CHARACTER_LEVEL, clamp_level
from core.models import Character
from core.progression import apply_experience, level_from_xp


def test_max_character_level_is_ten():
    assert MAX_CHARACTER_LEVEL == 10


def test_clamp_level_caps_at_ten():
    assert clamp_level(15) == 10
    assert clamp_level(0) == 1


def test_level_from_xp_level_three():
    assert level_from_xp(900) == 3


def test_level_from_xp_does_not_exceed_cap():
    assert level_from_xp(999_999) == 10


def test_apply_experience_levels_up_and_caps_hp():
    char = Character(
        name="Hero",
        race="human",
        class_name="fighter",
        level=1,
        stats={"constitution": 14},
        current_hp=12,
        max_hp=12,
        experience=0,
    )
    updated = apply_experience(char, 900)
    assert updated.level == 3
    assert updated.experience == 900
    assert updated.max_hp > char.max_hp


def test_apply_experience_does_not_exceed_level_ten():
    char = Character(
        name="Hero",
        race="human",
        class_name="fighter",
        level=10,
        stats={"constitution": 10},
        current_hp=50,
        max_hp=50,
        experience=64_000,
    )
    updated = apply_experience(char, 50_000)
    assert updated.level == 10
    assert updated.experience == 114_000
