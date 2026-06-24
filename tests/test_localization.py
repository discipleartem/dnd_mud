"""Тесты загрузки и получения строк локализации."""

from typing import Any

from core.localization import get_string, load_strings


def _flatten_keys(data: dict[str, Any], prefix: str = "") -> set[str]:
    """Собрать плоский набор ключей локализации (section.subkey)."""
    keys: set[str] = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            keys.update(_flatten_keys(value, full_key))
        else:
            keys.add(full_key)
    return keys


def test_en_ru_yaml_keys_match():
    """ru.yaml и en.yaml содержат одинаковый набор ключей."""
    ru_keys = _flatten_keys(load_strings("ru"))
    en_keys = _flatten_keys(load_strings("en"))

    assert ru_keys == en_keys


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


def test_get_string_missing_key_returns_default():
    """При отсутствии ключа возвращается default, если задан."""
    strings = {"menu": {"exit": "Exit"}}

    assert (
        get_string(strings, "menu.unknown", default="fallback") == "fallback"
    )


def test_resolve_localized_text_from_dict() -> None:
    """resolve_localized_text возвращает строку для языка."""
    from core.localization import resolve_localized_text

    value = {"ru": "Человек", "en": "Human"}
    assert resolve_localized_text(value, "en") == "Human"
    assert resolve_localized_text(value, "ru") == "Человек"


def test_get_string_format_and_key_error_fallback():
    """format подставляет kwargs; при KeyError возвращает шаблон."""
    strings = {"info": {"welcome": "Hello, {name}!"}}

    assert get_string(strings, "info.welcome", name="Tom") == "Hello, Tom!"
    assert get_string(strings, "info.welcome", age=30) == "Hello, {name}!"
