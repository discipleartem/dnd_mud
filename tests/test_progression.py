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
        class_id="fighter",
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
        class_id="fighter",
        level=1,
        stats={"constitution": 14},
        current_hp=12,
        max_hp=12,
        experience=900,
    )
    gain, _ = roll_hp_gain_for_level_up(char.class_id, char.stats, 2, "normal")
    updated = apply_level_up(char, gain)
    assert updated.level == 2
    assert updated.max_hp == 12 + gain
    assert has_pending_level_up(updated)


def test_resolve_pending_level_ups_matches_apply_experience(monkeypatch):
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
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
    assert names == ["Дварфская выдержка", "Дополнительные хиты"]
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


def test_resolve_pending_level_ups_records_asi_at_level_four():
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        stats={"strength": 16, "constitution": 14},
        current_hp=28,
        max_hp=28,
        experience=2700,
        difficulty="normal",
    )
    updated = resolve_pending_level_ups(char)
    assert updated.level == 4
    assert updated.asi_choices.get("4") == "asi"
    assert updated.stats["strength"] == 18


def test_resolve_pending_level_ups_tough_retroactive_on_stored_feat(
    monkeypatch,
):
    """Сохранённый выбор feat:tough даёт ретроактивный HP при авто-левелапе."""
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        stats={"constitution": 14, "strength": 16},
        current_hp=28,
        max_hp=28,
        experience=2700,
        difficulty="normal",
        asi_choices={"4": "feat:tough"},
    )

    def fake_roll(count: int, sides: int, modifier: int = 0) -> int:
        return 8 + modifier

    monkeypatch.setattr("core.progression.roll", fake_roll)
    updated = resolve_pending_level_ups(char)

    assert updated.level == 4
    assert updated.feat_ids == ["tough"]
    # +8 за ур. 4 (d10+CON) + 8 ретроактивно от Tough
    assert updated.max_hp == 44


def test_resolve_pending_level_ups_ignores_malformed_feat_choice(monkeypatch):
    """Повреждённый выбор feat: без ID не добавляется в feat_ids."""
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        stats={"constitution": 14, "intelligence": 10},
        current_hp=28,
        max_hp=28,
        experience=2700,
        difficulty="normal",
        asi_choices={"4": "feat:"},
    )

    def fake_roll(count: int, sides: int, modifier: int = 0) -> int:
        return 8 + modifier

    monkeypatch.setattr("core.progression.roll", fake_roll)
    updated = resolve_pending_level_ups(char)

    assert updated.level == 4
    assert updated.feat_ids == []
    assert updated.stats["intelligence"] == 10


def test_resolve_pending_level_ups_feat_ability_bonus_not_doubled(
    monkeypatch,
):
    """Черта с +1 к характеристике не удваивает бонус при авто-левелапе."""
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        stats={"constitution": 14, "intelligence": 10},
        current_hp=28,
        max_hp=28,
        experience=2700,
        difficulty="normal",
        asi_choices={
            "4": "feat:observant",
        },
        feat_choices={
            "observant": {"ability": "intelligence"},
        },
    )

    def fake_roll(count: int, sides: int, modifier: int = 0) -> int:
        return 8 + modifier

    monkeypatch.setattr("core.progression.roll", fake_roll)
    updated = resolve_pending_level_ups(char)

    assert updated.level == 4
    assert updated.feat_ids == ["observant"]
    assert updated.stats["intelligence"] == 11


def test_resolve_pending_level_ups_con_hp_from_stored_feat(monkeypatch):
    """CON +1 от черты на ASI-уровне даёт ретроактивный бонус HP."""
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        stats={"constitution": 11, "strength": 16},
        current_hp=28,
        max_hp=28,
        experience=2700,
        difficulty="normal",
        asi_choices={"4": "feat:resilient"},
        feat_choices={"resilient": {"ability": "constitution"}},
    )

    def fake_roll(count: int, sides: int, modifier: int = 0) -> int:
        return 8 + modifier

    monkeypatch.setattr("core.progression.roll", fake_roll)
    updated = resolve_pending_level_ups(char)

    assert updated.level == 4
    assert updated.stats["constitution"] == 12
    assert updated.feat_ids == ["resilient"]
    # d10 avg 6 + CON mod 1 = 7, +4 ретроактивно за CON 11→12 на 4 ур.
    assert updated.max_hp == 39


def test_resolve_pending_level_ups_applies_feat_skill_grants(monkeypatch):
    """Черта Skilled при авто-левелапе добавляет навыки и инструменты."""
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        stats={"constitution": 14},
        current_hp=28,
        max_hp=28,
        experience=2700,
        difficulty="normal",
        asi_choices={"4": "feat:skilled"},
        feat_choices={
            "skilled": {
                "skills_tools": [
                    {"type": "skill", "id": "athletics"},
                    {"type": "skill", "id": "stealth"},
                    {"type": "tool", "id": "thieves_tools"},
                ]
            }
        },
    )

    def fake_roll(count: int, sides: int, modifier: int = 0) -> int:
        return 8 + modifier

    monkeypatch.setattr("core.progression.roll", fake_roll)
    updated = resolve_pending_level_ups(char)

    assert updated.level == 4
    assert "athletics" in updated.skills
    assert "stealth" in updated.skills
    assert "thieves_tools" in updated.tool_proficiencies


def test_apply_experience_levels_up_and_caps_hp():
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
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
        class_id="fighter",
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
        class_id="fighter",
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
        class_id="fighter",
        level=10,
        stats={"constitution": 10},
        current_hp=50,
        max_hp=50,
        experience=64_000,
    )
    updated = apply_experience(char, 50_000)
    assert updated.level == 10
    assert updated.experience == 114_000
