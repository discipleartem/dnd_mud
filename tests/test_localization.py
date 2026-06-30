"""Тесты загрузки и получения строк локализации."""

from typing import Any

from core.localization import get_string, load_strings, resolve_localized_text


def _flatten_keys(data: dict[str, Any], prefix: str = "") -> set[str]:
    keys: set[str] = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            keys.update(_flatten_keys(value, full_key))
        else:
            keys.add(full_key)
    return keys


def test_en_ru_yaml_keys_match() -> None:
    assert _flatten_keys(load_strings("ru")) == _flatten_keys(
        load_strings("en")
    )


def test_get_string_and_resolve_localized_text() -> None:
    strings_en = load_strings("en")
    strings_ru = load_strings("ru")
    assert get_string(strings_en, "menu.new_game") == "New Game"
    assert get_string(strings_ru, "menu.new_game") == "Новая игра"
    assert (
        get_string({"menu": {"exit": "Exit"}}, "menu.unknown")
        == "menu.unknown"
    )
    assert (
        get_string(
            {"menu": {"exit": "Exit"}}, "menu.unknown", default="fallback"
        )
        == "fallback"
    )
    value = {"ru": "Человек", "en": "Human"}
    assert resolve_localized_text(value, "en") == "Human"
