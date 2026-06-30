"""Тесты отложенных особенностей класса и подкласса."""

from typing import Any

import pytest

from core.class_features import (
    class_features_applied_at_creation,
    needs_class_feature_picks,
)
from core.expertise import grant_expertise_satisfied, pending_expertise_grants
from core.models import Character
from core.scenario_actions import apply_scenario_action
from ui.menus.class_features import apply_pending_class_features


def test_class_features_not_applied_at_normal_level_one():
    """Normal, 1 ур.: подкласс выбран, особенности ещё не применены."""
    char = Character(
        name="Hero",
        race="elf",
        class_id="bard",
        level=1,
        subclass_id="lore_college",
        difficulty="normal",
    )
    assert (
        class_features_applied_at_creation("bard", "lore_college", 1) is False
    )
    assert needs_class_feature_picks(char) is False


def test_needs_class_features_at_level_three_normal():
    """Normal, 3 ур.: нужны особенности подкласса."""
    char = Character(
        name="Hero",
        race="elf",
        class_id="bard",
        level=3,
        subclass_id="lore_college",
        difficulty="normal",
        class_features_applied=False,
    )
    assert needs_class_feature_picks(char) is True


def test_bard_expertise_pending_at_level_three():
    """Бард 3 ур. без компетентности — grant в очереди."""
    char = Character(
        name="Hero",
        race="elf",
        class_id="bard",
        level=3,
        subclass_id="lore_college",
        skills=["arcana", "history", "performance"],
    )
    pending = pending_expertise_grants(char)
    assert len(pending) == 1
    assert pending[0].pick == 2
    assert not grant_expertise_satisfied(char, pending[0])


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


def test_apply_scenario_action_grant_xp() -> None:
    """grant_xp начисляет XP; повышение уровня — через UI."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=1,
        stats={"constitution": 14},
        current_hp=12,
        max_hp=12,
        difficulty="hardcore",
    )
    result = apply_scenario_action("grant_xp", {"amount": 900}, character)
    assert result.character.level == 1
    assert result.character.experience == 900
    assert result.level_up_pending is True
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
