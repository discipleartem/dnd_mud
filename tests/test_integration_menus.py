"""Интеграционные тесты UI-навигации."""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_localization():
    """Тест локализации: загрузка строк и получение по ключу."""
    from core.localization import get_string, load_strings

    strings_en = load_strings("en")
    assert get_string(strings_en, "menu.new_game") == "New Game"
    assert get_string(strings_en, "menu.exit") == "Exit"

    strings_ru = load_strings("ru")
    assert get_string(strings_ru, "menu.new_game") == "Новая игра"
    assert get_string(strings_ru, "settings.caption") == "НАСТРОЙКИ"
    assert get_string(strings_ru, "stats.strength") == "Сила"
    assert get_string(strings_en, "stats.strength") == "Strength"


def test_main_imports():
    """Тест, что main.py можно импортировать без ошибок."""
    import main

    assert main.VERSION == "0.1.0"
    assert callable(main.main)


def test_new_game_back_returns_one_step(monkeypatch):
    """Назад из выбора приключения возвращает к выбору персонажа."""
    from core.models import Adventure, Character
    from ui import menus

    calls = {
        "character": 0,
        "adventure": 0,
    }
    character = Character(
        name="Test Hero",
        race="human",
        class_name="fighter",
    )
    adventure = Adventure(id="test", name="Test Adventure")

    def select_character(strings):
        calls["character"] += 1
        if calls["character"] == 1:
            return character
        return None

    def select_adventure(strings, language, char):
        calls["adventure"] += 1
        return None

    monkeypatch.setattr(
        menus,
        "load_characters",
        lambda: [character],
    )
    monkeypatch.setattr(menus, "_select_character", select_character)
    monkeypatch.setattr(menus, "_select_adventure", select_adventure)

    menus.show_new_game_flow({}, {"language": "ru"})

    assert adventure.get_name() == "Test Adventure"
    assert calls == {
        "character": 2,
        "adventure": 1,
    }


def test_base_race_without_subraces_has_back_option(monkeypatch, capsys):
    """У базовой расы без подрас есть пункт Назад."""
    from ui import menus

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

    monkeypatch.setattr(menus, "load_race_full", lambda race_id: race)
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 0,
    )

    selected, subrace_id = menus._select_subrace(strings, "half_orc")
    output = capsys.readouterr().out

    assert selected is False
    assert subrace_id is None
    assert "0" in output
    assert "Назад" in output


def test_human_has_base_and_variant_choices(monkeypatch, capsys):
    """Человек показывает выбор обычного и вариантного человека."""
    from ui import menus

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

    monkeypatch.setattr(menus, "load_race_full", lambda race_id: race)
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 1,
    )

    selected, subrace_id = menus._select_subrace(strings, "human")
    output = capsys.readouterr().out

    assert selected is True
    assert subrace_id is None
    assert "1" in output
    assert "Человек (обычный)" in output
    assert "2" in output
    assert "Человек (вариант)" in output


def test_languages_menu_order_ru_locale(monkeypatch, capsys):
    """При ru локали первым идёт English, вторым — Русский."""
    from core.localization import load_strings
    from ui import menus

    strings = load_strings("ru")
    settings = {"language": "ru"}

    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 0,
    )

    menus.show_languages_menu(strings, settings)
    output = capsys.readouterr().out

    assert re.search(r"1.*English", output)
    assert re.search(r"2.*Русский", output)


def test_languages_menu_order_en_locale(monkeypatch, capsys):
    """При en локали первым идёт Русский, вторым — English."""
    from core.localization import load_strings
    from ui import menus

    strings = load_strings("en")
    settings = {"language": "en"}

    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 0,
    )

    menus.show_languages_menu(strings, settings)
    output = capsys.readouterr().out

    assert re.search(r"1.*Русский", output)
    assert re.search(r"2.*English", output)


def test_select_character_shows_all_with_difficulty(monkeypatch, capsys):
    """Все персонажи доступны, карточки показывают детали и сложность."""
    from core.localization import load_strings
    from core.models import Character
    from ui import menus

    strings = load_strings("ru")
    normal_char = Character(
        name="Hero Normal",
        race="human",
        class_name="fighter",
        difficulty="normal",
        stats={
            "strength": 16,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8,
        },
        current_hp=12,
        experience=0,
    )
    hardcore_char = Character(
        name="Hero HC",
        race="elf",
        class_name="bard",
        difficulty="hardcore",
        stats={
            "strength": 10,
            "dexterity": 15,
            "constitution": 12,
            "intelligence": 13,
            "wisdom": 11,
            "charisma": 14,
        },
        current_hp=9,
        experience=100,
    )

    monkeypatch.setattr(
        menus,
        "load_characters",
        lambda: [normal_char, hardcore_char],
    )
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 0,
    )

    result = menus._select_character(strings)
    output = capsys.readouterr().out

    assert result is None
    assert "Сохранённые персонажи" in output
    assert "Hero Normal" in output
    assert "Человек" in output
    assert "Воин" in output
    assert "Нормальная" in output
    assert "HP:" in output
    assert re.search(r"HP:\s+.*12", output)
    assert "Hero HC" in output
    assert "Эльф" in output
    assert "Бард" in output
    assert "HardCore" in output
    assert re.search(r"HP:\s+.*9", output)
    assert re.search(r"XP:\s+.*100", output)
    assert re.search(r"Сил.{0,30}16", output)
    assert re.search(r"Лов.{0,30}14", output)
    assert "Создать нового персонажа" in output
    assert "human" not in output
    assert "fighter" not in output
    assert "Персонажи другой сложности" not in output


def test_select_character_shows_subrace_name(monkeypatch, capsys):
    """Подраса отображается читаемым названием, а не ID."""
    from core.localization import load_strings
    from core.models import Character
    from ui import menus

    strings = load_strings("ru")
    character = Character(
        name="Variant Hero",
        race="human",
        class_name="cleric",
        difficulty="hardcore",
        subrace="variant_human",
        stats={"strength": 10, "dexterity": 10, "constitution": 10,
               "intelligence": 10, "wisdom": 10, "charisma": 10},
        current_hp=10,
    )

    monkeypatch.setattr(menus, "load_characters", lambda: [character])
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 0,
    )

    menus._select_character(strings)
    output = capsys.readouterr().out

    assert "Человек (вариант)" in output
    assert "variant_human" not in output


def test_select_character_create_new_option(monkeypatch):
    """Пункт создания нового персонажа возвращает 'create'."""
    from core.localization import load_strings
    from core.models import Character
    from ui import menus

    strings = load_strings("ru")
    character = Character(
        name="Hero",
        race="human",
        class_name="fighter",
        difficulty="normal",
    )

    monkeypatch.setattr(menus, "load_characters", lambda: [character])
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 2,
    )

    result = menus._select_character(strings)

    assert result == "create"


def test_select_adventure_filters_by_character_difficulty(monkeypatch, capsys):
    """Недоступные приключения показываются серым блоком."""
    from core.localization import load_strings
    from core.models import Adventure, Character
    from ui import menus

    strings = load_strings("ru")
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
        difficulty="easy",
    )
    blocked = Adventure(
        id="hc_only",
        name={"ru": "HardCore Quest"},
        description="desc",
        difficulty="normal",
        hardcore_only=True,
    )

    monkeypatch.setattr(
        menus,
        "load_adventures",
        lambda: [available, blocked],
    )
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 0,
    )

    result = menus._select_adventure(strings, "ru", character)
    output = capsys.readouterr().out

    assert result is None
    assert "Обучение" in output
    assert "HardCore Quest" in output
    assert "Недоступны для сложности персонажа" in output


def test_new_game_no_characters_goes_to_create(monkeypatch):
    """Без персонажей — сразу создание."""
    from ui import menus

    calls = {"select": 0, "create": 0}

    def select_character(strings):
        calls["select"] += 1
        return None

    def create_flow(strings, settings):
        calls["create"] += 1
        return None

    monkeypatch.setattr(menus, "load_characters", lambda: [])
    monkeypatch.setattr(menus, "_select_character", select_character)
    monkeypatch.setattr(menus, "show_create_character_flow", create_flow)

    menus.show_new_game_flow({}, {"language": "ru"})

    assert calls["select"] == 0
    assert calls["create"] == 1
