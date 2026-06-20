"""Тесты UI: выбор персонажа, подрасы, new game, приключения."""

import re

from core.models import Adventure, Character
from ui import menus
from ui.menus import _deps, character_flow, new_game
from ui.menus import settings as settings_menu


def test_base_race_without_subraces_has_back_option(
    monkeypatch, capsys, patch_int_input
):
    """У базовой расы без подрас есть пункт Назад."""
    strings = {
        "character": {
            "subrace_caption": "ОПИСАНИЕ РАСЫ И ВЫБОР ПОДРАСЫ",
            "race_description": "  {desc}",
            "features_label": "  Особенности:",
            "feature_line": "    • {name}: {desc}",
            "no_subraces": (
                "У этой расы нет подрас. Будет выбрана основная раса."
            ),
            "subrace_prompt": "Выберите подрасу: ",
            "back": "Назад",
        }
    }
    race = {
        "name": "Полуорк",
        "description": "Полуорки — сильные и выносливые воины",
        "allow_base_race_choice": True,
    }

    monkeypatch.setattr(_deps, "load_race_full", lambda race_id: race)
    patch_int_input(monkeypatch, menus, [0])

    selected, subrace_id = character_flow._select_subrace(strings, "half_orc")
    output = capsys.readouterr().out

    assert selected is False
    assert subrace_id is None
    assert "Назад" in output


def test_human_has_base_and_variant_choices(
    monkeypatch, capsys, patch_int_input
):
    """Человек показывает выбор обычного и вариантного человека."""
    strings = {
        "character": {
            "subrace_caption": "ОПИСАНИЕ РАСЫ И ВЫБОР ПОДРАСЫ",
            "race_description": "  {desc}",
            "features_label": "  Особенности:",
            "feature_line": "    • {name}: {desc}",
            "subraces_label": "  Подрасы:",
            "subrace_prompt": "Выберите подрасу: ",
            "back": "Назад",
        }
    }
    race = {
        "name": "Человек",
        "base_choice_name": "Человек (обычный)",
        "description": "Описание человека",
        "allow_base_race_choice": True,
        "ability_bonuses": {"strength": 1},
        "subraces": {
            "variant_human": {
                "name": "Человек (вариант)",
                "description": "Вариант человека",
                "inherit_base_bonuses": False,
                "ability_bonuses": {},
                "features": [],
            }
        },
    }

    monkeypatch.setattr(_deps, "load_race_full", lambda race_id: race)
    patch_int_input(monkeypatch, menus, [1])

    selected, subrace_id = character_flow._select_subrace(strings, "human")
    output = capsys.readouterr().out

    assert selected is True
    assert subrace_id is None
    assert "Человек (обычный)" in output
    assert "Человек (вариант)" in output


def test_select_character_shows_cards_with_difficulty(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Список персонажей показывает имя, расу, класс и сложность."""
    normal_char = Character(
        name="Hero Normal",
        race="human",
        class_name="fighter",
        difficulty="normal",
        stats={"strength": 16, "dexterity": 14},
        current_hp=12,
    )
    hardcore_char = Character(
        name="Hero HC",
        race="elf",
        class_name="bard",
        difficulty="hardcore",
        current_hp=9,
    )

    monkeypatch.setattr(
        _deps, "load_characters", lambda: [normal_char, hardcore_char]
    )
    patch_int_input(monkeypatch, menus, [0])

    result = new_game._select_character(ru_strings)
    output = capsys.readouterr().out

    assert result is None
    assert "Hero Normal" in output
    assert "Hero HC" in output
    assert "Человек" in output
    assert "Эльф" in output
    assert "Сложность:" in output
    assert "HardCore" in output
    assert "Создать нового персонажа" in output


def test_select_character_shows_subrace_name(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Подраса отображается читаемым названием, а не ID."""
    character = Character(
        name="Variant Hero",
        race="human",
        class_name="cleric",
        difficulty="hardcore",
        subrace="variant_human",
        stats=dict.fromkeys(
            [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ],
            10,
        ),
        current_hp=10,
    )

    monkeypatch.setattr(_deps, "load_characters", lambda: [character])
    patch_int_input(monkeypatch, menus, [0])

    new_game._select_character(ru_strings)
    output = capsys.readouterr().out

    assert "подраса:" in output
    assert "вариант" in output
    assert "variant_human" not in output


def test_select_character_create_via_menu_or_enter(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Пункт «Создать» и Enter без ввода возвращают 'create'."""
    character = Character(
        name="Hero",
        race="human",
        class_name="fighter",
        difficulty="normal",
    )
    monkeypatch.setattr(_deps, "load_characters", lambda: [character])

    patch_int_input(monkeypatch, menus, [2])
    assert new_game._select_character(ru_strings) == "create"

    from ui.input_handler import get_int_input

    monkeypatch.setattr(_deps, "get_int_input", get_int_input)
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    assert new_game._select_character(ru_strings) == "create"
    assert "[Enter]" in capsys.readouterr().out


def test_select_adventure_filters_by_character_difficulty(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Недоступные приключения показываются отдельным блоком."""
    character = Character(
        name="Normal Hero",
        race="human",
        class_name="fighter",
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
    patch_int_input(monkeypatch, menus, [0])

    result = new_game._select_adventure(ru_strings, "ru", character)
    output = capsys.readouterr().out

    assert result is None
    assert "Обучение" in output
    assert "HardCore Quest" in output
    assert "Недоступны для сложности персонажа" in output


def test_new_game_no_characters_goes_to_create(monkeypatch):
    """Без персонажей — сразу создание."""
    calls = {"select": 0, "create": 0}

    def select_character(strings):
        calls["select"] += 1

    def create_flow(strings):
        calls["create"] += 1

    monkeypatch.setattr(_deps, "load_characters", lambda: [])
    monkeypatch.setattr(
        character_flow, "show_create_character_flow", create_flow
    )

    new_game.show_new_game_flow({}, {"language": "ru"})

    assert calls == {"select": 0, "create": 1}


def test_new_game_back_returns_one_step(monkeypatch):
    """Назад из выбора приключения возвращает к выбору персонажа."""
    calls = {"character": 0, "adventure": 0}
    character = Character(
        name="Test Hero",
        race="human",
        class_name="fighter",
    )

    def select_character(strings):
        calls["character"] += 1
        return character if calls["character"] == 1 else None

    def select_adventure(strings, language, char):
        calls["adventure"] += 1
        return None

    monkeypatch.setattr(_deps, "load_characters", lambda: [character])
    monkeypatch.setattr(new_game, "_select_character", select_character)
    monkeypatch.setattr(new_game, "_select_adventure", select_adventure)

    new_game.show_new_game_flow({}, {"language": "ru"})

    assert calls == {"character": 2, "adventure": 1}


def test_languages_menu_order_depends_on_locale(
    monkeypatch, capsys, patch_int_input
):
    """Порядок языков в меню зависит от текущей локали."""
    from core.localization import load_strings

    patch_int_input(monkeypatch, menus, [0, 0])

    settings_menu.show_languages_menu(load_strings("ru"), {"language": "ru"})
    ru_output = capsys.readouterr().out
    assert re.search(r"1.*English", ru_output)
    assert re.search(r"2.*Русский", ru_output)

    settings_menu.show_languages_menu(load_strings("en"), {"language": "en"})
    en_output = capsys.readouterr().out
    assert re.search(r"1.*Русский", en_output)
    assert re.search(r"2.*English", en_output)
