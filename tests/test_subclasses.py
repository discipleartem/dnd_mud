"""Тесты подклассов, правил выбора и NPC-наставника."""

from collections.abc import Callable
from typing import Any, Literal

import pytest

from core.classes import get_subclass_choice_level, load_class_full
from core.models import Character
from core.subclasses import (
    features_up_to_level,
    needs_subclass_npc,
    start_level_for_difficulty,
    subclass_is_active,
    subclass_offered_at_creation,
)
from ui.menus.subclass_trainer import (
    assign_subclass_from_menu,
    run_subclass_trainer,
)

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


@pytest.mark.parametrize(
    "class_id,expected",
    [("cleric", 1), ("fighter", 3)],
)
def test_subclass_choice_level(class_id: str, expected: int) -> None:
    assert get_subclass_choice_level(class_id) == expected


@pytest.mark.parametrize(
    "difficulty,class_id,level,offered",
    [
        ("normal", "fighter", 1, True),
        ("hardcore", "fighter", 1, False),
        ("hardcore", "cleric", 1, True),
    ],
)
def test_subclass_offered_at_creation(
    difficulty: Literal["easy", "normal", "hardcore"],
    class_id: str,
    level: int,
    offered: bool,
) -> None:
    assert subclass_offered_at_creation(difficulty, class_id, level) is offered


def test_subclass_pending_and_npc_rules() -> None:
    assert start_level_for_difficulty("normal") == 1
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=1,
        subclass_id="champion",
        difficulty="normal",
    )
    assert subclass_is_active(char) is False
    char.level = 3
    assert subclass_is_active(char) is True
    hc = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        difficulty="hardcore",
    )
    assert needs_subclass_npc(hc) is True


def test_features_up_to_level_and_class_catalog() -> None:
    features = [
        {"id": "a", "level": 3, "name": "A"},
        {"id": "b", "level": 11, "name": "B"},
    ]
    assert len(features_up_to_level(features)) == 1
    fighter = load_class_full("fighter", "ru")
    assert "Улучшенная критическая атака" not in {
        f.get("name") for f in fighter.get("features", [])
    }


def test_run_subclass_trainer_requires_higher_level(
    capsys: pytest.CaptureFixture[str],
    ru_strings: dict[str, Any],
) -> None:
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


def test_assign_subclass_from_menu_champion(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
    patch_int_input: Callable[[pytest.MonkeyPatch, list[int]], None],
) -> None:
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
    assert saved[-1].subclass_id == "champion"
