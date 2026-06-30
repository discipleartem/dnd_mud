"""Тесты UI: персонаж, подрасы, new game, creation handlers."""

from typing import Any

import pytest

from core.character_storage import LoadCharactersResult
from core.models import Adventure, Character
from core.stats import STAT_NAMES
from ui.menus import (
    _creation_steps,
    _deps,
    characters_menu,
    new_game,
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


def _patch_load_characters(
    monkeypatch: pytest.MonkeyPatch, characters: list[Character]
) -> None:
    monkeypatch.setattr(
        _deps,
        "load_characters",
        lambda: LoadCharactersResult(characters=tuple(characters)),
    )


def _noop_press_enter(monkeypatch: pytest.MonkeyPatch) -> None:
    from ui.menus import _common

    monkeypatch.setattr(_common, "_press_enter", lambda strings: None)


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
    from ui.menus.stats import stats_methods

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


def test_select_character_create_via_enter(monkeypatch, capsys, ru_strings):
    """Enter без ввода на пункте «Создать» возвращает 'create'."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    monkeypatch.setattr(
        _deps,
        "load_characters",
        lambda: LoadCharactersResult(characters=(character,)),
    )

    from ui.input_handler import get_int_input

    monkeypatch.setattr(_deps, "get_int_input", get_int_input)
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    assert new_game._select_character(ru_strings, [character]) == "create"
    output = capsys.readouterr().out
    assert "[Enter]" in output
    assert "Создать нового персонажа" in output
    assert "2. Создать" not in output


def test_select_adventure_filters_by_character_difficulty(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Недоступные приключения показываются отдельным блоком."""
    character = Character(
        name="Normal Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    available = Adventure(
        id="tutorial",
        name={"ru": "Обучение"},
        description="desc",
    )
    blocked = Adventure(
        id="hc_only",
        name={"ru": "HardCore Quest"},
        description="desc",
        hardcore_only=True,
    )

    monkeypatch.setattr(_deps, "load_adventures", lambda: [available, blocked])
    patch_int_input(monkeypatch, [0])

    result = new_game._select_adventure(ru_strings, "ru", character)
    output = capsys.readouterr().out

    assert result is None
    assert "Обучение" in output
    assert "HardCore Quest" in output
    assert "Недоступные приключения" in output
    assert "требуется режим HardCore" in output


def test_select_adventure_choice_returns_adventure(
    monkeypatch, ru_strings, patch_int_input
):
    """Выбор доступного приключения возвращает объект Adventure."""
    character = Character(
        name="Normal Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    tutorial = Adventure(
        id="tutorial",
        name={"ru": "Обучение"},
        description="desc",
    )

    monkeypatch.setattr(_deps, "load_adventures", lambda: [tutorial])
    patch_int_input(monkeypatch, [1])

    result = new_game._select_adventure(ru_strings, "ru", character)

    assert result is not None
    assert result.id == "tutorial"


def test_new_game_corrupt_warning_shown_once_per_visit(
    monkeypatch, capsys, ru_strings
):
    """Предупреждение о битых сейвах — один раз за визит new game."""
    monkeypatch.setattr(
        _deps,
        "load_characters",
        lambda: LoadCharactersResult(
            characters=(), corrupt_save_warnings=("Broken",)
        ),
    )
    monkeypatch.setattr(
        _creation_steps,
        "show_create_character_flow",
        lambda _strings, _language: None,
    )

    new_game.show_new_game_flow(ru_strings, {"language": "ru"})
    output = capsys.readouterr().out

    assert output.count("Не удалось загрузить сохранения") == 1
    assert "Broken" in output


def test_new_game_no_characters_goes_to_create(monkeypatch):
    """Без персонажей — сразу создание."""
    calls = {"select": 0, "create": 0}

    def create_flow(strings, language="ru"):
        calls["create"] += 1

    monkeypatch.setattr(
        _deps, "load_characters", lambda: LoadCharactersResult.empty()
    )
    monkeypatch.setattr(
        _creation_steps, "show_create_character_flow", create_flow
    )

    new_game.show_new_game_flow({}, {"language": "ru"})

    assert calls == {"select": 0, "create": 1}


def test_new_game_back_navigation_and_cached_list(monkeypatch):
    """Назад из приключения; список персонажей не перечитывается."""
    calls = {"load": 0, "character": 0, "adventure": 0}
    character = Character(
        name="Test Hero",
        race="human",
        class_id="fighter",
    )

    def load_characters():
        calls["load"] += 1
        return LoadCharactersResult(characters=(character,))

    def select_character(strings, characters, language="ru"):
        calls["character"] += 1
        return character if calls["character"] == 1 else None

    def select_adventure(strings, language, char):
        calls["adventure"] += 1
        return None

    monkeypatch.setattr(_deps, "load_characters", load_characters)
    monkeypatch.setattr(new_game, "_select_character", select_character)
    monkeypatch.setattr(new_game, "_select_adventure", select_adventure)

    new_game.show_new_game_flow({}, {"language": "ru"})

    assert calls == {"load": 1, "character": 2, "adventure": 1}


def test_characters_menu_shows_hub_options(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Hub «Персонажи» показывает список и пункты создания/удаления."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        save_slug="hero",
    )
    _patch_load_characters(monkeypatch, [character])
    patch_int_input(monkeypatch, [0])

    characters_menu.show_characters_menu(ru_strings)
    output = capsys.readouterr().out

    assert "ПЕРСОНАЖИ" in output
    assert "Hero" in output
    assert "Создать персонажа" in output
    assert "Удалить персонажа" in output
    assert "Удалить всех персонажей" in output


def test_characters_menu_delete_one_confirmed(
    monkeypatch, ru_strings, patch_int_input
):
    """Удаление персонажа вызывает delete_character после подтверждения."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        save_slug="hero",
    )
    deleted: list[str] = []

    def fake_delete(slug: str) -> bool:
        deleted.append(slug)
        return True

    _patch_load_characters(monkeypatch, [character])
    monkeypatch.setattr(_deps, "delete_character", fake_delete)
    patch_int_input(monkeypatch, [2, 1, 1, 0])
    _noop_press_enter(monkeypatch)

    characters_menu.show_characters_menu(ru_strings)

    assert deleted == ["hero"]


def test_characters_menu_delete_all_cancelled(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Отмена удаления всех персонажей не вызывает delete_all_characters."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        save_slug="hero",
    )
    deleted_all_called: list[bool] = []

    def fake_delete_all() -> int:
        deleted_all_called.append(True)
        return 0

    _patch_load_characters(monkeypatch, [character])
    monkeypatch.setattr(_deps, "delete_all_characters", fake_delete_all)
    patch_int_input(monkeypatch, [3, 0, 0])
    _noop_press_enter(monkeypatch)

    characters_menu.show_characters_menu(ru_strings)
    output = capsys.readouterr().out

    assert deleted_all_called == []
    assert "Удаление отменено" in output


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
