"""Тесты главного меню, настроек и ввода."""

import json
from typing import Any

import pytest

import core.settings as settings_mod
from ui.input_handler import get_int_input, get_str_input
from ui.menus import main_menu
from ui.menus import settings as settings_menu


def test_show_main_menu_and_load_game_stub(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
    patch_int_input: Any,
    capsys: pytest.CaptureFixture[str],
) -> None:
    patch_int_input(monkeypatch, [3])
    assert main_menu.show_main_menu(ru_strings) == 3
    monkeypatch.setattr(main_menu, "_press_enter", lambda strings: None)
    main_menu.show_load_game_flow(ru_strings)
    assert "ещё не реализована" in capsys.readouterr().out


def test_select_difficulty_back_and_hardcore(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
    patch_int_input: Any,
) -> None:
    patch_int_input(monkeypatch, [0])
    assert settings_menu.select_difficulty(ru_strings) is None
    patch_int_input(monkeypatch, [3])
    assert settings_menu.select_difficulty(ru_strings) == "hardcore"


def test_settings_save_and_load(settings_file: Any) -> None:
    settings_mod.save_settings("en")
    assert settings_mod.load_settings()["language"] == "en"
    settings_mod.save_settings("ru")
    with open(settings_file, encoding="utf-8") as f:
        saved = json.load(f)
    assert saved["schema_version"] == 1
    assert "difficulty" not in saved


def test_input_handler_validation(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    int_inputs = iter(["99", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(int_inputs))
    assert get_int_input("test: ", 0, 5) == 2
    assert "Ошибка" in capsys.readouterr().out

    str_inputs = iter(["Hero1", "A", "Aragorn"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(str_inputs))
    assert (
        get_str_input("name: ", min_length=2, only_letters=True) == "Aragorn"
    )
