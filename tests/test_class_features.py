"""Тесты отложенных особенностей класса и подкласса."""

from typing import Any

import pytest

from core.class_features import (
    class_features_applied_at_creation,
    needs_class_feature_picks,
)
from core.models import Character
from core.scenario_actions import apply_scenario_action
from ui.menus.class_features import apply_pending_class_features


def test_bard_class_features_by_level() -> None:
    char = Character(
        name="Hero",
        race="elf",
        class_id="bard",
        level=3,
        subclass_id="lore_college",
        difficulty="normal",
        class_features_applied=False,
    )
    assert (
        class_features_applied_at_creation("bard", "lore_college", 3) is True
    )
    assert needs_class_feature_picks(char) is True


def test_subclass_training_triggers_class_features() -> None:
    char = Character(
        name="Hero",
        race="elf",
        class_id="bard",
        level=3,
        subclass_id="lore_college",
        difficulty="normal",
    )
    result = apply_scenario_action("subclass_training", {}, char)
    assert result.apply_class_features is True
    assert result.pick_subclass is False


def test_apply_pending_class_features_champion_marks_applied(
    monkeypatch: pytest.MonkeyPatch, ru_strings: dict[str, Any]
) -> None:
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        subclass_id="champion",
        class_features_applied=False,
        difficulty="normal",
    )
    monkeypatch.setattr(
        "ui.menus.class_features._deps.update_character", lambda c: c
    )
    monkeypatch.setattr(
        "ui.menus.class_features._print_success_and_wait",
        lambda *args, **kwargs: None,
    )
    result = apply_pending_class_features(ru_strings, char, "ru")
    assert result is not None
    assert result.class_features_applied is True
