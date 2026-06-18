"""Интеграционные тесты для модулей игры."""

import sys
from pathlib import Path

# Добавляем корень проекта в sys.path для импорта main.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_localization():
    """Тест локализации: загрузка строк и получение по ключу."""
    from core.localization import get_string, load_strings

    # Загружаем английский
    strings_en = load_strings("en")
    assert get_string(strings_en, "menu.new_game") == "New Game"
    assert get_string(strings_en, "menu.exit") == "Exit"

    # Загружаем русский
    strings_ru = load_strings("ru")
    assert get_string(strings_ru, "menu.new_game") == "Новая игра"
    assert get_string(strings_ru, "settings.caption") == "НАСТРОЙКИ"

    print("✓ Локализация: все ключи загружены")


def test_settings():
    """Тест сохранения и загрузки настроек."""
    from core.settings import load_settings, save_settings

    # Сохраняем тестовые настройки
    save_settings("en", hardcore=True)

    loaded = load_settings()
    assert loaded["language"] == "en"
    assert loaded["hardcore"] is True

    # Проверяем дефолтные
    save_settings("ru", hardcore=False)

    loaded = load_settings()
    assert loaded["language"] == "ru"
    assert loaded["hardcore"] is False

    print("✓ Настройки: сохранение/загрузка OK")


def test_main_imports():
    """Тест, что main.py можно импортировать без ошибок."""
    import main

    assert main.VERSION == "0.1.0"
    assert callable(main.main)

    print(f"✓ main.py: импорты OK (версия {main.VERSION})")


def test_new_game_back_returns_one_step(monkeypatch):
    """Назад из выбора приключения возвращает к выбору персонажа."""
    from core.models import Adventure
    from ui import menus

    calls = {
        "difficulty": 0,
        "character": 0,
        "adventure": 0,
    }
    character = {"name": "Test Hero", "race": "Human", "class": "Fighter"}
    adventure = Adventure(id="test", name="Test Adventure")

    def select_difficulty(strings, settings):
        calls["difficulty"] += 1
        if calls["difficulty"] == 1:
            return "normal"
        return None

    def select_character(strings):
        calls["character"] += 1
        if calls["character"] == 1:
            return character
        return None

    def select_adventure(strings):
        calls["adventure"] += 1
        return None

    monkeypatch.setattr(menus, "select_difficulty", select_difficulty)
    monkeypatch.setattr(menus, "load_characters", lambda: [character])
    monkeypatch.setattr(menus, "_select_character", select_character)
    monkeypatch.setattr(menus, "_select_adventure", select_adventure)

    menus.show_new_game_flow({}, {"difficulty": "normal"})

    assert adventure.get_name() == "Test Adventure"
    assert calls == {
        "difficulty": 2,
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

    monkeypatch.setattr(menus, "_clear_screen", lambda: None)
    monkeypatch.setattr(menus, "load_race_full", lambda race_id: race)
    monkeypatch.setattr(menus, "get_int_input", lambda prompt, min_v, max_v: 0)

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

    monkeypatch.setattr(menus, "_clear_screen", lambda: None)
    monkeypatch.setattr(menus, "load_race_full", lambda race_id: race)
    monkeypatch.setattr(menus, "get_int_input", lambda prompt, min_v, max_v: 1)

    selected, subrace_id = menus._select_subrace(strings, "human")
    output = capsys.readouterr().out

    assert selected is True
    assert subrace_id is None
    assert "1" in output
    assert "Человек (обычный)" in output
    assert "2" in output
    assert "Человек (вариант)" in output


def test_variant_human_does_not_inherit_base_bonuses():
    """Человек (вариант) не получает +1 ко всем характеристикам."""
    from core.character import _get_race_bonuses

    base_bonuses = _get_race_bonuses("human")
    variant_bonuses = _get_race_bonuses("human", "variant_human")

    assert base_bonuses == {
        "strength": 1,
        "dexterity": 1,
        "constitution": 1,
        "intelligence": 1,
        "wisdom": 1,
        "charisma": 1,
    }
    assert variant_bonuses == {}


if __name__ == "__main__":
    tests = [
        test_localization,
        test_settings,
        test_main_imports,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()  # type: ignore[no-untyped-call]
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {type(e).__name__}: {e}")
            failed += 1

    total = passed + failed
    print()
    print("=" * 50)
    print(f"  Результат: {passed}/{total} тестов пройдено")
    print("=" * 50)

    if failed > 0:
        exit(1)
