"""Тесты UI меню — меню персонажей."""

import pytest

from core.character_storage import LoadCharactersResult
from core.models import Character
from ui.menus import _deps, characters_menu


def _patch_load_characters(
    monkeypatch: pytest.MonkeyPatch, characters: list[Character]
) -> None:
    monkeypatch.setattr(
        _deps,
        "load_characters",
        lambda: LoadCharactersResult(characters=tuple(characters)),
    )


def test_characters_menu_shows_hub_options(
    monkeypatch, capsys, ru_strings, patch_int_input
):
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


def test_characters_menu_delete_one_confirmed(
    monkeypatch, ru_strings, patch_int_input
):
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
    from ui.menus import _common

    monkeypatch.setattr(_common, "_press_enter", lambda strings: None)
    patch_int_input(monkeypatch, [2, 1, 1, 0])
    characters_menu.show_characters_menu(ru_strings)
    assert deleted == ["hero"]
