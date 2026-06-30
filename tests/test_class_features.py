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


@pytest.mark.parametrize(
    "level,needs_picks,applied_at_creation",
    [
        (1, False, False),
        (3, True, True),
    ],
)
def test_bard_class_features_by_level(
    level: int, needs_picks: bool, applied_at_creation: bool
) -> None:
    """Normal: особенности подкласса с 3 уровня."""
    char = Character(
        name="Hero",
        race="elf",
        class_id="bard",
        level=level,
        subclass_id="lore_college",
        difficulty="normal",
        class_features_applied=level < 3,
    )
    assert (
        class_features_applied_at_creation("bard", "lore_college", level)
        is applied_at_creation
    )
    assert needs_class_feature_picks(char) is needs_picks


def test_subclass_training_triggers_class_features():
    """Сценарий: подкласс есть, уровень 3 — apply_class_features."""
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
    """Чемпион без выборов — особенности отмечены применёнными."""
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
        "ui.menus.class_features._deps.update_character",
        lambda c: c,
    )
    monkeypatch.setattr(
        "ui.menus.class_features._print_success_and_wait",
        lambda *args, **kwargs: None,
    )

    result = apply_pending_class_features(ru_strings, char, "ru")
    assert result is not None
    assert result.class_features_applied is True


def test_apply_pending_class_features_noop_when_not_needed(
    ru_strings: dict[str, Any],
) -> None:
    """Особенности не требуются — персонаж возвращается без изменений."""
    char = Character(
        name="Hero",
        race="elf",
        class_id="fighter",
        level=1,
        difficulty="normal",
    )
    result = apply_pending_class_features(ru_strings, char, "ru")
    assert result is char
