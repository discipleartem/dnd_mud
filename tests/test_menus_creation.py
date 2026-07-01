"""Тесты UI меню — создание персонажа."""

import ui.menus._creation_handlers as creation_handlers
from core.stats import STAT_NAMES
from ui.menus import _creation_steps, _deps
from ui.menus._creation_handlers import _handle_feats, _handle_skills
from ui.menus._creation_navigation import (
    back_step_from_feats,
    feats_step_required,
    step_after_class_choice,
)
from ui.menus._creation_state import _CreationState
from ui.menus._selectors import select_subrace


def _flat_stats(value: int = 10) -> dict[str, int]:
    return dict.fromkeys(STAT_NAMES, value)


def test_select_subrace_human_menu(
    monkeypatch,
    capsys,
    patch_int_input,
    subrace_strings,
    human_race_with_subraces,
):
    """Выбор подрасы человека — меню standard/variant."""
    monkeypatch.setattr(
        _deps,
        "load_race_full",
        lambda _race_id, language="ru": human_race_with_subraces,
    )
    patch_int_input(monkeypatch, [1])
    selected, subrace_id = select_subrace(subrace_strings, "human")
    output = capsys.readouterr().out
    assert selected is True
    assert subrace_id == "standard"
    assert "Человек (вариант)" in output


def test_create_character_back_from_subrace_exits(
    monkeypatch, ru_strings, patch_int_input
):
    monkeypatch.setattr(
        _creation_steps, "select_difficulty", lambda strings: "normal"
    )
    monkeypatch.setattr(_deps, "get_str_input", lambda *args, **kwargs: "Hero")
    monkeypatch.setattr(
        _deps,
        "load_races",
        lambda language="ru": [{"id": "human", "name": "Человек"}],
    )
    monkeypatch.setattr(
        creation_handlers,
        "select_subrace",
        lambda *args, **kwargs: (False, None),
    )
    patch_int_input(monkeypatch, [1, 0])
    assert _creation_steps.show_create_character_flow(ru_strings) is None


def test_creation_feat_step_routing_variant_human() -> None:
    state = _CreationState(
        name="Hero",
        difficulty="normal",
        race_id="human",
        subrace_id="variant_human",
        class_id="fighter",
    )
    assert feats_step_required(state) is True
    assert step_after_class_choice(state) == "feats"
    assert back_step_from_feats(state) == "subclass"


def test_creation_feat_step_routing_elf_skips_feats() -> None:
    state = _CreationState(
        name="Hero",
        difficulty="normal",
        race_id="elf",
        subrace_id="wood_elf",
        class_id="fighter",
    )
    assert feats_step_required(state) is False
    assert step_after_class_choice(state) == "proficiencies"


def test_handlers_without_class_id() -> None:
    state = _CreationState(
        name="Test",
        difficulty="normal",
        race_id="human",
        stats=_flat_stats(),
    )
    assert _handle_feats({}, state, "ru").next_step == "class"
    assert _handle_skills({}, state, "ru").next_step == "proficiencies"
