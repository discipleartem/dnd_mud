"""Тесты scenario runner UI."""

from collections.abc import Callable
from typing import Any

import pytest

from core.models import Adventure, Character
from ui.menus.scenario_flow import run_scenario


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
