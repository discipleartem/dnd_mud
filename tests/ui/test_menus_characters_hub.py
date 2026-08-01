"""Тесты UI меню — меню персонажей."""

import pytest

from core.character.models import Character
from core.character.storage import LoadCharactersResult
from ui.menus.hub import characters_menu


def _patch_load_characters(
    monkeypatch: pytest.MonkeyPatch, characters: list[Character]
) -> None:
    monkeypatch.setattr(
        "ui.menus.hub._characters_cache.load_characters",
        lambda: LoadCharactersResult(characters=tuple(characters)),
    )


def test_characters_menu_shows_hub_options(
    monkeypatch, capsys, ru_strings, patch_int_input, minimal_character
):
    _patch_load_characters(monkeypatch, [minimal_character])
    patch_int_input(monkeypatch, [0])
    characters_menu.show_characters_menu(ru_strings)
    output = capsys.readouterr().out
    assert "ПЕРСОНАЖИ" in output
    assert "Hero" in output
    assert "Создать персонажа" in output


def test_characters_menu_delete_one_confirmed(
    monkeypatch,
    ru_strings,
    patch_int_input,
    patch_press_enter,
    minimal_character,
):
    deleted: list[str] = []

    def fake_delete(slug: str) -> bool:
        deleted.append(slug)
        return True

    _patch_load_characters(monkeypatch, [minimal_character])
    monkeypatch.setattr(characters_menu, "delete_character", fake_delete)
    patch_int_input(monkeypatch, [2, 1, 1, 0])
    characters_menu.show_characters_menu(ru_strings)
    assert deleted == ["hero"]
