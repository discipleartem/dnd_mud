"""Тесты UI меню — создание персонажа."""

from typing import Any

import pytest

from core.models import Character
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
)
from ui.menus._creation_state import _CreationState
from ui.menus._selectors import select_subrace
from ui.menus.stats import stats_methods


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

    monkeypatch.setattr(_creation_steps, "select_subrace", fake_subrace)
    patch_int_input(monkeypatch, [1, 0])

    result = _creation_steps.show_create_character_flow(ru_strings)

    assert result is None
    assert subrace_calls["n"] == 1


def test_hardcore_back_to_race_clears_rolls(
    monkeypatch, ru_strings, patch_int_input
):
    """HardCore: возврат к выбору расы сбрасывает сохранённые броски."""

    monkeypatch.setattr(
        _creation_steps,
        "select_difficulty",
        lambda strings: "hardcore",
    )
    monkeypatch.setattr(
        _deps,
        "get_str_input",
        lambda *args, **kwargs: "Hero",
    )
    monkeypatch.setattr(
        _deps,
        "load_races",
        lambda language="ru": [{"id": "elf", "name": "Эльф"}],
    )
    subrace_calls = {"n": 0}

    def fake_subrace(strings, race_id, language="ru"):
        subrace_calls["n"] += 1
        if subrace_calls["n"] == 1:
            return True, "wood_elf"
        if subrace_calls["n"] == 2:
            return False, None
        return True, "wood_elf"

    monkeypatch.setattr(_creation_steps, "select_subrace", fake_subrace)
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_languages",
        lambda *args, **kwargs: ["common", "elvish"],
    )

    def fake_background(*args, **kwargs):
        return ("soldier", ["athletics", "intimidation"])

    monkeypatch.setattr(
        _creation_steps,
        "select_creation_background",
        fake_background,
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_proficiencies",
        lambda *args, **kwargs: (
            ["simple", "martial"],
            ["light", "medium", "heavy", "shield"],
            ["dice_set"],
        ),
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_class",
        lambda strings, language="ru": {"id": "fighter"},
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_skills",
        lambda *args, **kwargs: ["athletics", "intimidation"],
    )
    monkeypatch.setattr(
        _creation_steps,
        "select_creation_expertise",
        lambda *args, **kwargs: ([], []),
    )
    monkeypatch.setattr(
        _creation_steps,
        "_save_created_character",
        lambda state: Character(name="Hero", race="elf", class_id="fighter"),
    )
    monkeypatch.setattr(
        _creation_steps,
        "_print_success_and_wait",
        lambda strings, message: None,
    )
    roll_sequence = iter([10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11])
    roll_calls = {"count": 0}

    def fake_roll() -> int:
        roll_calls["count"] += 1
        return next(roll_sequence)

    monkeypatch.setattr(_deps, "roll_ability_score", fake_roll)
    monkeypatch.setattr(stats_methods, "_press_enter", lambda strings: None)
    patch_int_input(monkeypatch, [1, 0, 1, 1])

    _creation_steps.show_create_character_flow(ru_strings)

    assert roll_calls["count"] == 12


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
    state = _creation_steps._CreationState(**state_kwargs)
    assert (
        _creation_steps._feats_step_required(state) is expected_feats_required
    )
    assert (
        _creation_steps._step_after_class_choice(state) == expected_after_class
    )
    if expected_back is not None:
        assert _creation_steps._back_step_from_feats(state) == expected_back


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
