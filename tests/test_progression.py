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

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_character_level_cap_and_xp() -> None:
    assert MAX_CHARACTER_LEVEL == 10
    assert clamp_level(15) == 10
    assert level_from_xp(900) == 3
    assert level_from_xp(999_999) == 10


def test_max_hp_for_level_with_bonuses() -> None:
    dwarf_hp = max_hp_for_level(
        "cleric",
        {"constitution": 17},
        3,
        "normal",
        race_id="dwarf",
        subrace_id="hill_dwarf",
    )
    assert dwarf_hp == 30
    tough_hp = max_hp_for_level(
        "fighter",
        {"constitution": 14},
        3,
        "normal",
        race_id="human",
        subrace_id=None,
        feat_ids=["tough"],
    )
    assert tough_hp == 34


def test_resolve_pending_level_ups_matches_apply_experience(
    monkeypatch: pytest.MonkeyPatch,
    fighter_l1_hardcore: Character,
) -> None:
    char = fighter_l1_hardcore

    def patch_rolls(values: list[int]) -> None:
        rolls = iter(values)
        monkeypatch.setattr(
            "core.progression.roll",
            lambda count, sides, modifier=0: next(rolls) + modifier,
        )

    patch_rolls([8, 3])
    via_resolve = resolve_pending_level_ups(grant_experience(char, 900))
    patch_rolls([8, 3])
    via_apply = apply_experience(char, 900)
    assert via_resolve.level == via_apply.level == 3
    assert via_resolve.max_hp == via_apply.max_hp == 22


def test_resolve_pending_level_ups_records_asi_and_feat(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
        asi_choices={"4": "feat:tough"},
        feat_choices={},
    )
    monkeypatch.setattr(
        "core.progression.roll", lambda count, sides, modifier=0: 8 + modifier
    )
    updated = resolve_pending_level_ups(char)
    assert updated.level == 4
    assert updated.feat_ids == ["tough"]


def test_run_pending_level_ups_preview_matches_applied_hp(
    monkeypatch: pytest.MonkeyPatch,
    patch_level_up_ui: None,
    fighter_l3: Character,
) -> None:
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
    rolls = iter([8, 3])
    monkeypatch.setattr(
        "core.progression.roll",
        lambda count, sides, modifier=0: next(rolls) + modifier,
    )
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
    monkeypatch.setattr(
        "ui.menus._deps.update_character", lambda char: saved.append(char)
    )
    monkeypatch.setattr(
        "ui.menus.scenario_flow.assign_subclass_from_menu",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr("ui.menus.level_up._press_enter", lambda strings: None)
    patch_int_input(monkeypatch, [1, 1])
    result = run_scenario(adventure, character, ru_strings, "ru")
    assert result.level == 3
    assert result.experience == 900
