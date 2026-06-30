"""Тесты прогрессии и потолка уровня."""

from collections.abc import Callable
from typing import Any

import pytest

from core.levels import MAX_CHARACTER_LEVEL, clamp_level
from core.models import Character
from core.progression import (
    apply_experience,
    grant_experience,
    level_from_xp,
    max_hp_for_level,
    resolve_pending_level_ups,
)


def test_character_level_cap_and_xp() -> None:
    assert MAX_CHARACTER_LEVEL == 10
    assert clamp_level(15) == 10
    assert level_from_xp(900) == 3
    assert level_from_xp(999_999) == 10


@pytest.mark.parametrize(
    "race_id,subrace_id,feat_ids,expected_hp",
    [
        ("dwarf", "hill_dwarf", [], 30),
        ("human", None, ["tough"], 34),
    ],
)
def test_max_hp_for_level_with_bonuses(
    race_id: str,
    subrace_id: str | None,
    feat_ids: list[str],
    expected_hp: int,
) -> None:
    stats = {"constitution": 17 if race_id == "dwarf" else 14}
    class_id = "cleric" if race_id == "dwarf" else "fighter"
    hp = max_hp_for_level(
        class_id,
        stats,
        3,
        "normal",
        race_id=race_id,
        subrace_id=subrace_id,
        feat_ids=feat_ids or None,
    )
    assert hp == expected_hp


def test_resolve_pending_level_ups_matches_apply_experience(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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


def test_resolve_pending_level_ups_records_asi_at_level_four() -> None:
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


@pytest.mark.parametrize(
    "asi_choice,feat_choices,expected_feat_ids,extra_assert",
    [
        (
            "feat:tough",
            {},
            ["tough"],
            lambda c: c.max_hp == 44,
        ),
        (
            "feat:skilled",
            {
                "skilled": {
                    "skills_tools": [
                        {"type": "skill", "id": "athletics"},
                        {"type": "skill", "id": "stealth"},
                        {"type": "tool", "id": "thieves_tools"},
                    ]
                }
            },
            ["skilled"],
            lambda c: "athletics" in c.skills
            and "thieves_tools" in c.tool_proficiencies,
        ),
    ],
)
def test_resolve_pending_level_ups_applies_stored_feat(
    monkeypatch: pytest.MonkeyPatch,
    asi_choice: str,
    feat_choices: dict[str, dict[str, Any]],
    expected_feat_ids: list[str],
    extra_assert: Callable[[Character], bool],
) -> None:
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
        asi_choices={"4": asi_choice},
        feat_choices=feat_choices,
    )

    def fake_roll(count: int, sides: int, modifier: int = 0) -> int:
        return 8 + modifier

    monkeypatch.setattr("core.progression.roll", fake_roll)
    updated = resolve_pending_level_ups(char)
    assert updated.level == 4
    assert updated.feat_ids == expected_feat_ids
    assert extra_assert(updated)


def test_apply_experience_levels_up_and_caps_hp() -> None:
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
    assert updated.max_hp == 28
    assert updated.current_hp == 28


def test_apply_experience_hardcore_uses_rolls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rolls = iter([8, 3])
    monkeypatch.setattr(
        "core.progression.roll",
        lambda count, sides, modifier=0: next(rolls) + modifier,
    )
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


def test_apply_experience_does_not_exceed_level_ten() -> None:
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
