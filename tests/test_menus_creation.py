"""Тесты UI меню — создание персонажа."""

from typing import Any

import pytest

import ui.menus._creation_handlers as creation_handlers
from core.stats import STAT_NAMES
from ui.menus import (
    _creation_steps,
    _deps,
)
from ui.menus._creation_handlers import (
    _handle_feats,
    _handle_skills,
)
from ui.menus._creation_navigation import (
    back_step_from_feats,
    back_step_from_proficiencies,
    back_step_from_skills,
    feats_step_required,
    step_after_class_choice,
)
from ui.menus._creation_state import _CreationState
from ui.menus._selectors import select_subrace


def _flat_stats(value: int = 10) -> dict[str, int]:
    return dict.fromkeys(STAT_NAMES, value)


@pytest.mark.parametrize(
    "race_id,race_data,subrace_strings_fixture,input_values,expected_subrace,"
    "output_contains",
    [
        (
            "half_orc",
            {
                "name": "Полуорк",
                "description": "Полуорки — сильные и выносливые воины",
                "subraces": {
                    "half_orc": {
                        "name": "Полуорк",
                        "description": "Полуорки — сильные и выносливые воины",
                        "ability_bonuses": {"strength": 2},
                    }
                },
            },
            None,
            None,
            "half_orc",
            None,
        ),
        (
            "human",
            None,
            "human_race_with_subraces",
            [1],
            "standard",
            ["Человек (стандарт)", "Человек (вариант)"],
        ),
    ],
)
def test_select_subrace(
    monkeypatch,
    capsys,
    patch_int_input,
    subrace_strings,
    human_race_with_subraces,
    race_id,
    race_data,
    subrace_strings_fixture,
    input_values,
    expected_subrace,
    output_contains,
):
    """Выбор подрасы: авто при одной или меню при нескольких."""
    strings = (
        subrace_strings
        if race_id == "human"
        else {
            "character": {"subrace_caption": "ОПИСАНИЕ РАСЫ И ВЫБОР ПОДРАСЫ"}
        }
    )
    race = race_data or human_race_with_subraces
    monkeypatch.setattr(
        _deps, "load_race_full", lambda _race_id, language="ru": race
    )
    if input_values is not None:
        patch_int_input(monkeypatch, input_values)

    selected, subrace_id = select_subrace(strings, race_id)
    output = capsys.readouterr().out

    assert selected is True
    assert subrace_id == expected_subrace
    if output_contains:
        for fragment in output_contains:
            assert fragment in output


def test_create_character_back_from_subrace_exits(
    monkeypatch, ru_strings, patch_int_input
):
    """Назад с подрасы — к расе; повторный назад выходит из flow."""
    monkeypatch.setattr(
        _creation_steps,
        "select_difficulty",
        lambda strings: "normal",
    )
    monkeypatch.setattr(
        _deps,
        "get_str_input",
        lambda *args, **kwargs: "Hero",
    )
    monkeypatch.setattr(
        _deps,
        "load_races",
        lambda language="ru": [{"id": "human", "name": "Человек"}],
    )
    subrace_calls = {"n": 0}

    def fake_subrace(strings, race_id, language="ru"):
        subrace_calls["n"] += 1
        return False, None

    monkeypatch.setattr(creation_handlers, "select_subrace", fake_subrace)
    patch_int_input(monkeypatch, [1, 0])

    result = _creation_steps.show_create_character_flow(ru_strings)

    assert result is None
    assert subrace_calls["n"] == 1


def test_hardcore_back_from_subrace_clears_rolls(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
) -> None:
    """HardCore: возврат с подрасы к расе сбрасывает сохранённые броски."""
    from ui.menus._creation_handlers import _handle_subrace

    state = _CreationState(name="Hero", difficulty="hardcore", race_id="elf")
    state.hardcore_rolls.extend([10, 10, 10, 10])

    monkeypatch.setattr(
        creation_handlers,
        "select_subrace",
        lambda *args, **kwargs: (False, None),
    )

    result = _handle_subrace(ru_strings, state, "ru")

    assert result.next_step == "race"
    assert state.hardcore_rolls == []


@pytest.mark.parametrize(
    "state_kwargs,expected_feats_required,expected_after_class,expected_back",
    [
        (
            {
                "name": "Hero",
                "difficulty": "normal",
                "race_id": "human",
                "subrace_id": "variant_human",
                "class_id": "fighter",
            },
            True,
            "feats",
            "subclass",
        ),
        (
            {
                "name": "Hero",
                "difficulty": "normal",
                "race_id": "elf",
                "subrace_id": "wood_elf",
                "class_id": "fighter",
            },
            False,
            "proficiencies",
            None,
        ),
    ],
)
def test_creation_feat_step_routing(
    state_kwargs: dict[str, Any],
    expected_feats_required: bool,
    expected_after_class: str,
    expected_back: str | None,
) -> None:
    """Маршрутизация шага черт для variant human vs elf."""
    state = _CreationState(**state_kwargs)
    assert feats_step_required(state) is expected_feats_required
    assert step_after_class_choice(state) == expected_after_class
    if expected_back is not None:
        assert back_step_from_feats(state) == expected_back


def test_back_step_from_skills_and_feats_without_class() -> None:
    state = _CreationState(name="Test", difficulty="normal")
    assert back_step_from_skills(state) == "proficiencies"
    assert back_step_from_feats(state) == "class"


def test_back_step_from_feats_with_subclass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _CreationState(
        name="Test",
        difficulty="normal",
        class_id="fighter",
    )
    monkeypatch.setattr(
        "ui.menus._creation_navigation.subclass_offered_at_creation",
        lambda _difficulty, _class_id: True,
    )
    assert back_step_from_feats(state) == "subclass"


def test_handlers_without_class_id() -> None:
    state = _CreationState(
        name="Test",
        difficulty="normal",
        race_id="human",
        stats=_flat_stats(),
    )
    assert _handle_feats({}, state, "ru").next_step == "class"
    assert _handle_skills({}, state, "ru").next_step == "proficiencies"


def test_back_step_from_proficiencies_via_feats(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _CreationState(
        name="Test",
        difficulty="normal",
        race_id="human",
        subrace_id="variant_human",
        class_id="fighter",
    )
    monkeypatch.setattr(
        "ui.menus._creation_navigation.feats_step_required",
        lambda _state: True,
    )
    assert back_step_from_proficiencies(state) == "feats"
