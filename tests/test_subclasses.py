"""Тесты подклассов и правил выбора по сложности."""

from core.classes import get_subclass_choice_level, load_class_full
from core.models import Character
from core.subclasses import (
    features_up_to_level,
    needs_subclass_npc,
    start_level_for_difficulty,
    subclass_is_active,
    subclass_offered_at_creation,
)


def test_subclass_choice_level_cleric_is_one():
    assert get_subclass_choice_level("cleric") == 1


def test_subclass_choice_level_fighter_is_three():
    assert get_subclass_choice_level("fighter") == 3


def test_start_level_easy_is_three():
    assert start_level_for_difficulty("easy") == 3


def test_start_level_normal_is_one():
    assert start_level_for_difficulty("normal") == 1


def test_subclass_offered_normal_always():
    assert subclass_offered_at_creation("normal", "fighter", 1) is True


def test_subclass_not_offered_hardcore_fighter_level_one():
    assert subclass_offered_at_creation("hardcore", "fighter", 1) is False


def test_subclass_offered_hardcore_cleric_level_one():
    assert subclass_offered_at_creation("hardcore", "cleric", 1) is True


def test_subclass_pending_until_level_three():
    char = Character(
        name="Hero",
        race="human",
        class_name="fighter",
        level=1,
        subclass_id="champion",
        difficulty="normal",
    )
    assert subclass_is_active(char) is False
    char.level = 3
    assert subclass_is_active(char) is True


def test_needs_subclass_npc_hardcore_fighter_level_three():
    char = Character(
        name="Hero",
        race="human",
        class_name="fighter",
        level=3,
        difficulty="hardcore",
    )
    assert needs_subclass_npc(char) is True


def test_needs_subclass_npc_hardcore_cleric_level_one():
    char = Character(
        name="Hero",
        race="human",
        class_name="cleric",
        level=1,
        difficulty="hardcore",
    )
    assert needs_subclass_npc(char) is False


def test_features_up_to_level_filters_high_levels():
    features = [
        {"id": "a", "level": 3, "name": "A"},
        {"id": "b", "level": 11, "name": "B"},
    ]
    filtered = features_up_to_level(features)
    assert len(filtered) == 1
    assert filtered[0]["id"] == "a"


def test_class_features_exclude_subclass_abilities():
    """Карточка класса не дублирует умения подклассов."""
    fighter = load_class_full("fighter", "ru")
    feature_names = {f.get("name") for f in fighter.get("features", [])}
    assert "Улучшенная критическая атака" not in feature_names

    cleric = load_class_full("cleric", "ru")
    cleric_names = {f.get("name") for f in cleric.get("features", [])}
    assert "Божественный домен" not in cleric_names

    bard = load_class_full("bard", "ru")
    bard_names = {f.get("name") for f in bard.get("features", [])}
    assert "Вдохновляющая защитная мантия" not in bard_names
    assert "Джек всех мастеров" not in bard_names
    assert "Мастер на все руки" in bard_names
    jack = next(f for f in bard["features"] if f["id"] == "jack_of_all_trades")
    assert jack["level"] == 2
    assert "трёх навыков" not in jack["description"]
