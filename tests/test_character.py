"""Тесты персонажей: бонусы, генерация stats, save/load."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_character_round_trip_with_subrace():
    """Character.to_dict/from_dict сохраняет subrace."""
    from core.models import Character

    original = Character(
        name="Test",
        race="human",
        class_name="fighter",
        subrace="variant_human",
        stats={"strength": 10},
        current_hp=12,
    )
    restored = Character.from_dict(original.to_dict())
    assert restored.subrace == "variant_human"
    assert restored.class_name == "fighter"
    assert restored.name == "Test"


def test_variant_human_does_not_inherit_base_bonuses():
    """Человек (вариант) не получает +1 ко всем характеристикам."""
    from core.character import get_race_bonuses

    base_bonuses = get_race_bonuses("human")
    variant_bonuses = get_race_bonuses("human", "variant_human")

    assert base_bonuses == {
        "strength": 1,
        "dexterity": 1,
        "constitution": 1,
        "intelligence": 1,
        "wisdom": 1,
        "charisma": 1,
    }
    assert variant_bonuses == {}


def test_generate_stats_random_accepts_race_only():
    """generate_stats_random без лишних kwargs."""
    from core.character import STAT_NAMES, generate_stats_random

    values = [15, 14, 13, 12, 10, 8]
    stats = generate_stats_random(values, "elf")

    assert set(stats.keys()) == set(STAT_NAMES)
    assert stats["dexterity"] == 14 + 2


def test_generate_stats_hardcore():
    """HardCore генерация возвращает все шесть характеристик с бонусами."""
    from core.character import STAT_NAMES, generate_stats_hardcore

    stats = generate_stats_hardcore("human")

    assert set(stats.keys()) == set(STAT_NAMES)
    assert all(3 <= value <= 20 for value in stats.values())


def test_remaining_standard_array_pool():
    """Остаток пула уменьшается по мере назначения значений."""
    from core.character import remaining_standard_array_pool

    assert remaining_standard_array_pool([]) == [15, 14, 13, 12, 10, 8]
    assert remaining_standard_array_pool([15, 14]) == [13, 12, 10, 8]


def test_point_buy_total_cost():
    """Суммарная стоимость point-buy считается по таблице."""
    from core.character import point_buy_total_cost

    assert point_buy_total_cost([8, 8, 8, 8, 8, 8]) == 0
    assert point_buy_total_cost([15, 15, 15, 8, 8, 8]) == 27


def test_can_assign_point_buy_value():
    """Point-buy: допустимость значения с учётом бюджета."""
    from core.character import STAT_NAMES, can_assign_point_buy_value

    stats = dict.fromkeys(STAT_NAMES, 8)
    assert can_assign_point_buy_value(stats, "strength", 15) is True
    stats["strength"] = 15
    stats["dexterity"] = 15
    stats["constitution"] = 15
    assert can_assign_point_buy_value(stats, "intelligence", 15) is False
    assert can_assign_point_buy_value(stats, "constitution", 10) is True
    assert can_assign_point_buy_value(stats, "intelligence", 16) is False


def test_save_and_load_character(tmp_path, monkeypatch):
    """save_character и load_characters работают с Character."""
    import core.character as character_mod

    saves_file = tmp_path / "characters.json"
    monkeypatch.setattr(character_mod, "CHARACTERS_FILE", saves_file)

    saved = character_mod.save_character(
        name="Hero",
        race_id="human",
        class_id="fighter",
        stats={
            "strength": 16,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 8,
        },
    )
    assert saved.name == "Hero"
    assert saved.race == "human"

    loaded = character_mod.load_characters()
    assert len(loaded) == 1
    assert loaded[0].name == "Hero"
    assert loaded[0].class_name == "fighter"

    with open(saves_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema_version"] == 1
    assert data["characters"][0]["class"] == "fighter"
