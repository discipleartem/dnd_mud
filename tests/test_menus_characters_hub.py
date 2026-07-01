"""Тесты UI меню — меню персонажей."""

import pytest

from core.character_storage import LoadCharactersResult
from core.models import Character
from ui.menus import (
    _deps,
    characters_menu,
)


def _patch_load_characters(
    monkeypatch: pytest.MonkeyPatch, characters: list[Character]
) -> None:
    monkeypatch.setattr(
        _deps,
        "load_characters",
        lambda: LoadCharactersResult(characters=tuple(characters)),
    )


def _noop_press_enter(monkeypatch: pytest.MonkeyPatch) -> None:
    from ui.menus import _common

    monkeypatch.setattr(_common, "_press_enter", lambda strings: None)


def test_characters_menu_shows_hub_options(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Hub «Персонажи» показывает список и пункты создания/удаления."""
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
    assert "Удалить персонажа" in output
    assert "Удалить всех персонажей" in output


def test_characters_menu_delete_one_confirmed(
    monkeypatch, ru_strings, patch_int_input
):
    """Удаление персонажа вызывает delete_character после подтверждения."""
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
    patch_int_input(monkeypatch, [2, 1, 1, 0])
    _noop_press_enter(monkeypatch)

    characters_menu.show_characters_menu(ru_strings)

    assert deleted == ["hero"]


def test_characters_menu_delete_all_cancelled(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Отмена удаления всех персонажей не вызывает delete_all_characters."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        save_slug="hero",
    )
    deleted_all_called: list[bool] = []

    def fake_delete_all() -> int:
        deleted_all_called.append(True)
        return 0

    _patch_load_characters(monkeypatch, [character])
    monkeypatch.setattr(_deps, "delete_all_characters", fake_delete_all)
    patch_int_input(monkeypatch, [3, 0, 0])
    _noop_press_enter(monkeypatch)

    characters_menu.show_characters_menu(ru_strings)
    output = capsys.readouterr().out

    assert deleted_all_called == []
    assert "Удаление отменено" in output
