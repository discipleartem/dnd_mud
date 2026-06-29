"""Тесты scenario runner."""

from core.models import Adventure, Character
from core.scenario_actions import apply_scenario_action
from ui.menus.scenario_flow import run_scenario


def test_apply_scenario_action_grant_xp():
    """grant_xp начисляет XP; повышение уровня — через UI."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=1,
        stats={"constitution": 14},
        current_hp=12,
        max_hp=12,
        difficulty="hardcore",
    )
    result = apply_scenario_action("grant_xp", {"amount": 900}, character)
    assert result.character.level == 1
    assert result.character.experience == 900
    assert result.level_up_pending is True
    assert result.pick_subclass is False


def test_run_scenario_grant_xp_levels_character(
    monkeypatch, ru_strings, patch_int_input
):
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
