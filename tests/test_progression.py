"""Тесты прогрессии и потолка уровня."""

from core.levels import MAX_CHARACTER_LEVEL, clamp_level
from core.models import Character
from core.progression import (
    apply_experience,
    apply_level_up,
    grant_experience,
    has_pending_level_up,
    hp_gain_breakdown_for_level_up,
    level_from_xp,
    max_hp_for_level,
    resolve_pending_level_ups,
    roll_hp_gain_for_level_up,
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


def test_grant_experience_does_not_level_up():
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
    updated = grant_experience(char, 900)
    assert updated.experience == 900
    assert updated.level == 1
    assert has_pending_level_up(updated)


def test_apply_level_up_one_step():
    char = Character(
        name="Hero",
        race="human",
        class_name="fighter",
        level=1,
        stats={"constitution": 14},
        current_hp=12,
        max_hp=12,
        experience=900,
    )
    gain, _ = roll_hp_gain_for_level_up(
        char.class_name, char.stats, 2, "normal"
    )
    updated = apply_level_up(char, gain)
    assert updated.level == 2
    assert updated.max_hp == 12 + gain
    assert has_pending_level_up(updated)


def test_resolve_pending_level_ups_matches_apply_experience(monkeypatch):
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

    def patch_rolls(values: list[int]) -> None:
        rolls = iter(values)

        def fake_roll(count: int, sides: int, modifier: int = 0) -> int:
            return next(rolls) + modifier

        monkeypatch.setattr("core.progression.roll", fake_roll)

    patch_rolls([8, 3])
    via_resolve = resolve_pending_level_ups(grant_experience(char, 900))

    patch_rolls([8, 3])
    via_apply = apply_experience(char, 900)

    assert via_resolve.level == via_apply.level == 3
    assert via_resolve.max_hp == via_apply.max_hp == 22
    assert via_resolve.experience == via_apply.experience == 900


def test_hill_dwarf_hp_bonus_per_level():
    """Дварфская выдержка: +1 HP на каждый уровень."""
    stats = {"constitution": 17}
    hp = max_hp_for_level(
        "cleric", stats, 3, "normal", race_id="dwarf", subrace_id="hill_dwarf"
    )
    # normal cleric d8, CON +3: 11 + 8 + 8 = 27; hill dwarf +3 = 30
    assert hp == 30


def test_hill_dwarf_level_up_gain_includes_bonus():
    breakdown = hp_gain_breakdown_for_level_up(
        "cleric",
        {"constitution": 17},
        2,
        "normal",
        race_id="dwarf",
        subrace_id="hill_dwarf",
    )
    assert breakdown.class_part == 8
    assert breakdown.extra_bonus == 1
    assert breakdown.total == 9


def test_hp_gain_breakdown_lists_bonus_sources_by_name():
    breakdown = hp_gain_breakdown_for_level_up(
        "cleric",
        {"constitution": 20},
        2,
        "normal",
        race_id="dwarf",
        subrace_id="hill_dwarf",
        feat_ids=["tough"],
    )
    names = [source.name for source in breakdown.bonus_sources]
    assert names == ["Дварфская выдержка", "Крепкий"]
    assert breakdown.extra_bonus == 3


def test_mountain_dwarf_has_no_hp_bonus():
    stats = {"constitution": 17}
    hp = max_hp_for_level(
        "cleric",
        stats,
        3,
        "normal",
        race_id="dwarf",
        subrace_id="mountain_dwarf",
    )
    assert hp == 27


def test_tough_feat_hp_bonus_per_level():
    stats = {"constitution": 14}
    hp = max_hp_for_level(
        "fighter",
        stats,
        3,
        "normal",
        race_id="human",
        feat_ids=["tough"],
    )
    # fighter d10 CON+2: 12+8+8=28; tough +2×3 = +6 → 34
    assert hp == 34


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


def test_apply_experience_preserves_creation_fields():
    """XP не сбрасывает языки, предысторию и навыки."""
    char = Character(
        name="Hero",
        race="half_orc",
        class_name="fighter",
        level=1,
        stats={"constitution": 14},
        current_hp=12,
        max_hp=12,
        experience=0,
        difficulty="hardcore",
        languages=["common", "orcish", "elvish"],
        background_id="outlander",
        skills=["athletics", "survival", "intimidation", "perception"],
        skill_expertise=["stealth"],
        save_slug="hero",
    )
    updated = apply_experience(char, 900)
    assert updated.languages == char.languages
    assert updated.background_id == char.background_id
    assert updated.skills == char.skills
    assert updated.skill_expertise == char.skill_expertise


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
