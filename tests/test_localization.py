"""Тесты загрузки и получения строк локализации."""

from core.localization import get_string, load_strings


def test_load_strings_ru_and_en_keys():
    """Ключевые строки загружаются для ru и en."""
    strings_en = load_strings("en")
    strings_ru = load_strings("ru")

    assert get_string(strings_en, "menu.new_game") == "New Game"
    assert get_string(strings_en, "stats.strength") == "Strength"
    assert get_string(strings_ru, "menu.new_game") == "Новая игра"
    assert get_string(strings_ru, "settings.caption") == "НАСТРОЙКИ"
    assert get_string(strings_ru, "stats.strength") == "Сила"


def test_get_string_nested_key():
    """get_string находит вложенный ключ через точку."""
    strings = {"menu": {"exit": "Exit"}}

    assert get_string(strings, "menu.exit") == "Exit"


def test_get_string_missing_key_returns_key():
    """Отсутствующий ключ возвращается как есть."""
    strings = {"menu": {"exit": "Exit"}}

    assert get_string(strings, "menu.unknown") == "menu.unknown"


def test_get_string_format_and_key_error_fallback():
    """format подставляет kwargs; при KeyError возвращает шаблон."""
    strings = {"info": {"welcome": "Hello, {name}!"}}

    assert get_string(strings, "info.welcome", name="Tom") == "Hello, Tom!"
    assert get_string(strings, "info.welcome", age=30) == "Hello, {name}!"
