"""Тесты прогрессии и потолка уровня."""

from collections.abc import Callable
from dataclasses import replace
from typing import Any

import pytest

from core.levels import MAX_CHARACTER_LEVEL, clamp_level
from core.models import Adventure, Character
from core.progression import (
    apply_experience,
    grant_experience,
    level_from_xp,
    max_hp_for_level,
    resolve_pending_level_ups,
)
from ui.menus import level_up as level_up_menu
from ui.menus.scenario_flow import run_scenario


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
    fighter_l1_hardcore: Character,
) -> None:
    char = fighter_l1_hardcore

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


# --- UI smoke ---


def test_run_pending_level_ups_preview_matches_applied_hp(
    monkeypatch: pytest.MonkeyPatch,
    patch_level_up_ui: None,
    fighter_l3: Character,
) -> None:
    """Превью max HP учитывает con_bonus и tough_bonus."""
    char = fighter_l3
    preview_gain: list[int] = []

    def capture_screen(strings, character, new_level, breakdown, extra_hp=0):
        preview_gain.append(breakdown.total + extra_hp)

    def fake_asi(strings, character, new_level, language="ru"):
        stats = character.stats.copy()
        stats["constitution"] = 16
        new_feats = list(character.feat_ids) + ["tough"]
        updated = replace(character, stats=stats, feat_ids=new_feats)
        return updated, stats, new_feats, {}, "feat:tough"

    monkeypatch.setattr(level_up_menu, "select_level_up_feat_or_asi", fake_asi)
    monkeypatch.setattr(
        level_up_menu, "_print_level_up_screen", capture_screen
    )

    result = level_up_menu.run_pending_level_ups({}, char)

    assert preview_gain == [result.max_hp - char.max_hp]


def test_run_scenario_grant_xp_levels_character(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
    patch_int_input: Callable[[pytest.MonkeyPatch, list[int]], None],
) -> None:
    """grant_xp в сценарии открывает экраны повышения уровня."""
    rolls = iter([8, 3])

    def fake_roll(count: int, sides: int, modifier: int = 0) -> int:
        return next(rolls) + modifier

    monkeypatch.setattr("core.progression.roll", fake_roll)

    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=1,
        stats={"constitution": 14},
        current_hp=12,
        max_hp=12,
        save_slug="hero",
        difficulty="hardcore",
    )
    adventure = Adventure(
        id="test",
        name={"ru": "Тест"},
        script_file="adventures/tutorial.yaml",
    )

    saved: list[Character] = []

    def fake_update(char: Character) -> None:
        saved.append(char)

    monkeypatch.setattr("ui.menus.scenario_flow.update_character", fake_update)
    monkeypatch.setattr(
        "ui.menus.scenario_flow.assign_subclass_from_menu",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "ui.menus.level_up._press_enter",
        lambda strings: None,
    )
    patch_int_input(monkeypatch, [1, 1])

    result = run_scenario(adventure, character, ru_strings, "ru")

    assert result.level == 3
    assert result.experience == 900
    assert result.max_hp == 27
