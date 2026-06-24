"""Тесты главного меню и выбора сложности."""

from typing import Any

import pytest

from ui.menus import main_menu
from ui.menus import settings as settings_menu


def test_select_difficulty_returns_none_on_back(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
    patch_int_input: Any,
) -> None:
    patch_int_input(monkeypatch, [0])
    assert settings_menu.select_difficulty(ru_strings) is None


def test_select_difficulty_returns_hardcore(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
    patch_int_input: Any,
) -> None:
    patch_int_input(monkeypatch, [2])
    assert settings_menu.select_difficulty(ru_strings) == "hardcore"


def test_show_main_menu_returns_choice(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
    patch_int_input: Any,
) -> None:
    patch_int_input(monkeypatch, [3])
    assert main_menu.show_main_menu(ru_strings) == 3
