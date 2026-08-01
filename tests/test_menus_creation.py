"""Тесты UI меню — создание персонажа."""

from collections.abc import Callable
from typing import Any

import pytest

import ui.menus.creation.handlers as creation_handlers
from core.types import CharacterClass
from tests.creation_helpers import flat_stats
from ui.menus.creation import steps as _creation_steps
from ui.menus.creation.handlers import (
    _handle_equipment,
    _handle_feats,
    _handle_skills,
)
from ui.menus.creation.navigation import (
    back_step_from_feats,
    feats_step_required,
    step_after_class_choice,
)
from ui.menus.creation.selectors import select_subrace
from ui.menus.creation.state import _CreationState


def test_select_subrace_half_orc_shows_menu_with_back(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    patch_int_input: Callable[[pytest.MonkeyPatch, list[int]], None],
    ru_strings: dict[str, Any],
) -> None:
    """Полуорк — экран расы с одной подрасой и пунктом «Назад»."""
    patch_int_input(monkeypatch, [1])
    selected, subrace_id = select_subrace(ru_strings, "half_orc")
    output = capsys.readouterr().out
    assert selected is True
    assert subrace_id == "half_orc"
    assert "ОПИСАНИЕ РАСЫ И ВЫБОР ПОДРАСЫ" in output
    assert "Полуорк" in output
    assert "Подрасы:" in output
    assert "Тёмное зрение" in output
    assert "Назад" in output


def test_select_subrace_half_orc_back_returns_false(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    patch_int_input: Callable[[pytest.MonkeyPatch, list[int]], None],
    ru_strings: dict[str, Any],
) -> None:
    """Полуорк — 0 возвращает на выбор расы."""
    patch_int_input(monkeypatch, [0])
    selected, subrace_id = select_subrace(ru_strings, "half_orc")
    assert selected is False
    assert subrace_id is None


def test_select_subrace_human_menu(
    monkeypatch,
    capsys,
    patch_int_input,
    subrace_strings,
    human_race_with_subraces,
):
    """Выбор подрасы человека — меню standard/variant."""
    monkeypatch.setattr(
        "ui.menus.creation.selectors.load_race_full",
        lambda _race_id, language="ru": human_race_with_subraces,
    )
    patch_int_input(monkeypatch, [1])
    selected, subrace_id = select_subrace(subrace_strings, "human")
    output = capsys.readouterr().out
    assert selected is True
    assert subrace_id == "standard"
    assert "Человек (вариант)" in output


def test_select_subrace_shows_base_race_grants(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    patch_int_input: Callable[[pytest.MonkeyPatch, list[int]], None],
    ru_strings: dict[str, Any],
) -> None:
    """На экране подрасы выводятся особенности базовой расы."""
    patch_int_input(monkeypatch, [1])
    _selected, _subrace_id = select_subrace(ru_strings, "dwarf")
    output = capsys.readouterr().out
    assert "Тёмное зрение" in output
    assert "Дварфская боевая подготовка" in output


def test_select_subrace_human_shows_race_language_on_base_block(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    patch_int_input: Callable[[pytest.MonkeyPatch, list[int]], None],
    ru_strings: dict[str, Any],
) -> None:
    """Дополнительный язык — в строке «Языки» расы, без дублей у подрас."""
    patch_int_input(monkeypatch, [0])
    select_subrace(ru_strings, "human")
    output = capsys.readouterr().out
    base_block, subrace_section = output.split("Подрасы:", 1)
    assert "Языки:" in base_block
    assert "Общий" in base_block
    assert "на выбор из" in base_block
    assert "Дополнительный язык" not in base_block
    assert "Особенности:" not in base_block.split("Подрасы:")[0]
    assert "Дополнительный язык" not in subrace_section
    assert "(раса)" not in output


def test_select_subrace_elf_drow_shows_only_subrace_grants(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    patch_int_input: Callable[[pytest.MonkeyPatch, list[int]], None],
    ru_strings: dict[str, Any],
) -> None:
    """Подраса показывает только свои особенности; общие — в блоке расы."""
    patch_int_input(monkeypatch, [3])
    _selected, subrace_id = select_subrace(ru_strings, "elf")
    output = capsys.readouterr().out
    assert subrace_id == "dark_elf_drow"
    base_block, subrace_section = output.split("Подрасы:", 1)
    assert "Обострённые чувства" in base_block
    assert "Наследие фей" in base_block
    drow_idx = subrace_section.find("Дроу")
    assert drow_idx >= 0
    drow_block = subrace_section[drow_idx:]
    assert "Магия дроу" in drow_block
    assert "Пляшущие огоньки" in drow_block
    assert "Обострённые чувства" not in drow_block
    assert "Наследие фей" not in drow_block
    assert "(раса)" not in drow_block


def test_select_subrace_dwarf_hill_no_parent_grant_duplication(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    patch_int_input: Callable[[pytest.MonkeyPatch, list[int]], None],
    ru_strings: dict[str, Any],
) -> None:
    """Холмовой дварф не дублирует черты базовой расы."""
    patch_int_input(monkeypatch, [1])
    select_subrace(ru_strings, "dwarf")
    output = capsys.readouterr().out
    base_block, subrace_section = output.split("Подрасы:", 1)
    assert "Тёмное зрение" in base_block
    hill_block = subrace_section.split("2.", 1)[0]
    assert "Дварфская выдержка" in hill_block
    assert "Тёмное зрение" not in hill_block
    assert "Дварфская боевая подготовка" not in hill_block


def test_create_character_back_from_subrace_exits(
    monkeypatch, ru_strings, patch_int_input
):
    monkeypatch.setattr(
        _creation_steps, "select_difficulty", lambda strings: "normal"
    )
    monkeypatch.setattr(
        _creation_steps, "get_str_input", lambda *args, **kwargs: "Hero"
    )
    monkeypatch.setattr(
        creation_handlers,
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
        stats=flat_stats(10),
    )
    assert _handle_feats({}, state, "ru").next_step == "class"
    assert _handle_skills({}, state, "ru").next_step == "proficiencies"


def test_handle_skills_routes_to_equipment(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
) -> None:
    """После навыков (без expertise) flow переходит на шаг снаряжения."""
    state = _CreationState(
        name="Hero",
        difficulty="normal",
        race_id="human",
        subrace_id="standard",
        class_id="fighter",
        stats=flat_stats(10),
    )
    monkeypatch.setattr(
        creation_handlers,
        "select_creation_skills",
        lambda *args, **kwargs: ["athletics", "perception"],
    )
    result = _handle_skills(ru_strings, state, "ru")
    assert result.next_step == "equipment"
    assert state.skills == ["athletics", "perception"]


def test_handle_equipment_stores_choices_and_finalizes(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
) -> None:
    """Шаг equipment сохраняет выборы и завершает создание."""
    from core.character.models import Character

    state = _CreationState(
        name="Hero",
        difficulty="normal",
        race_id="human",
        class_id="fighter",
        stats=flat_stats(10),
        weapon_proficiencies=["simple", "martial"],
        armor_proficiencies=["light", "medium", "heavy", "shield"],
    )
    choices = {"armor": "chain_mail", "weapon_primary": "martial_shield"}
    monkeypatch.setattr(
        creation_handlers,
        "select_creation_equipment",
        lambda *args, **kwargs: choices,
    )
    fake_char = Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
        equipment_choices=choices,
    )
    monkeypatch.setattr(
        creation_handlers,
        "finalize_creation",
        lambda strings, st: fake_char,
    )
    result = _handle_equipment(ru_strings, state, "ru")
    assert state.equipment_choices == choices
    assert result.character is fake_char
