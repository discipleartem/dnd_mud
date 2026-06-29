"""Тесты отложенных особенностей класса и подкласса."""

from core.class_features import (
    class_features_applied_at_creation,
    needs_class_feature_picks,
)
from core.expertise import grant_expertise_satisfied, pending_expertise_grants
from core.models import Character
from core.scenario_actions import apply_scenario_action


def test_class_features_not_applied_at_normal_level_one():
    """Normal, 1 ур.: подкласс выбран, особенности ещё не применены."""
    char = Character(
        name="Hero",
        race="elf",
        class_name="bard",
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
        class_name="bard",
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
        class_name="bard",
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
        class_name="bard",
        level=3,
        subclass_id="lore_college",
        difficulty="normal",
    )
    result = apply_scenario_action("subclass_training", {}, char)
    assert result.apply_class_features is True
    assert result.pick_subclass is False
