"""Тесты NPC-наставника подкласса."""

from core.models import Character
from ui.menus.subclass_trainer import (
    assign_subclass_from_menu,
    run_subclass_trainer,
)


def test_run_subclass_trainer_requires_higher_level(
    capsys, ru_strings, patch_int_input
):
    """Боец 1 ур. не может выбрать подкласс у наставника."""
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=1,
        difficulty="normal",
    )
    result = run_subclass_trainer(ru_strings, char, "ru")
    output = capsys.readouterr().out
    assert result is char
    assert result.subclass_id is None
    assert "3" in output


def test_run_subclass_trainer_already_has_subclass(capsys, ru_strings):
    """Подкласс уже выбран — сообщение без повторного выбора."""
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        subclass_id="champion",
        class_features_applied=True,
        difficulty="normal",
    )
    result = run_subclass_trainer(ru_strings, char, "ru")
    output = capsys.readouterr().out
    assert result is char
    assert "уже выбран" in output.lower() or "already" in output.lower()


def test_assign_subclass_from_menu_champion(
    monkeypatch, ru_strings, patch_int_input
):
    """Наставник: выбор чемпиона сохраняет subclass_id."""
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        skills=["athletics", "intimidation"],
        difficulty="normal",
    )
    saved: list[Character] = []

    def fake_update(character: Character) -> Character:
        saved.append(character)
        return character

    monkeypatch.setattr(
        "ui.menus.subclass_trainer._deps.update_character",
        fake_update,
    )
    patch_int_input(monkeypatch, [3])

    updated = assign_subclass_from_menu(ru_strings, char, "ru")
    assert updated is not None
    assert updated.subclass_id == "champion"
    assert saved
    assert saved[-1].subclass_id == "champion"
