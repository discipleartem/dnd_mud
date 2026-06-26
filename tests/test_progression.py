"""Тесты прогрессии и потолка уровня."""

from core.levels import MAX_CHARACTER_LEVEL, clamp_level
from core.models import Character
from core.progression import (
    apply_experience,
    level_from_xp,
    max_hp_for_level,
)


def test_max_character_level_is_ten():
    assert MAX_CHARACTER_LEVEL == 10


def test_clamp_level_caps_at_ten():
    assert clamp_level(15) == 10
    assert clamp_level(0) == 1


def test_level_from_xp_level_three():
    assert level_from_xp(900) == 3


def test_level_from_xp_does_not_exceed_cap():
    assert level_from_xp(999_999) == 10


def test_max_hp_level_three_fighter_average():
    """Normal: макс. кость на 1 ур., среднее на 2+."""
    stats = {"constitution": 14}
    hp = max_hp_for_level("fighter", stats, 3, "normal")
    assert hp == 28


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
        difficulty="normal",
    )
    updated = apply_experience(char, 900)
    assert updated.level == 3
    assert updated.experience == 900
    assert updated.max_hp == 28
    assert updated.current_hp == 28


def test_apply_experience_hardcore_adds_rolls_not_average(monkeypatch):
    """HardCore: прирост HP за каждый новый уровень — бросок кости."""
    rolls = iter([8, 3])

    def fake_roll(count: int, sides: int, modifier: int = 0) -> int:
        return next(rolls) + modifier

    monkeypatch.setattr("core.progression.roll", fake_roll)

    char = Character(
        name="Hero",
        race="human",
        class_name="fighter",
        level=1,
        stats={"constitution": 14},
        current_hp=7,
        max_hp=7,
        experience=0,
        difficulty="hardcore",
    )
    updated = apply_experience(char, 900)
    assert updated.level == 3
    assert updated.max_hp == 22
    assert updated.current_hp == 22


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
