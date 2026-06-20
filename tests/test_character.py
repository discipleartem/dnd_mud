"""Тесты персонажей: бонусы, генерация stats, save/load."""

import json

import core.character as character_mod


def test_variant_human_does_not_inherit_base_bonuses():
    """Человек (вариант) не получает +1 ко всем характеристикам."""
    base_bonuses = character_mod.get_race_bonuses("human")
    variant_bonuses = character_mod.get_race_bonuses("human", "variant_human")

    assert base_bonuses == {
        "strength": 1,
        "dexterity": 1,
        "constitution": 1,
        "intelligence": 1,
        "wisdom": 1,
        "charisma": 1,
    }
    assert variant_bonuses == {}


def test_variant_human_choice_mechanics():
    """Человек (вариант): mechanics выборного бонуса из features."""
    mechanics = character_mod.get_choice_ability_bonus_mechanics(
        "human", "variant_human"
    )

    assert mechanics is not None
    assert mechanics["count"] == 2
    assert mechanics["value"] == 1
    assert mechanics["choice"] is True
    assert mechanics["allow_duplicates"] is False


def test_elf_has_no_choice_ability_bonus():
    """Эльф не имеет выборных бонусов к характеристикам."""
    mechanics = character_mod.get_choice_ability_bonus_mechanics("elf", None)
    assert mechanics is None


def test_apply_choice_bonuses_to_stats():
    """Выборные бонусы корректно добавляются к характеристикам."""
    base = {
        "strength": 15,
        "dexterity": 14,
        "constitution": 13,
        "intelligence": 12,
        "wisdom": 10,
        "charisma": 8,
    }
    choice_bonuses = character_mod.build_bonuses_from_choices(
        ["strength", "wisdom"], 1
    )
    final = character_mod.apply_bonuses_to_stats(base, choice_bonuses)

    assert final["strength"] == 16
    assert final["wisdom"] == 11
    assert final["dexterity"] == 14


def test_get_effective_race_bonuses_includes_choices():
    """Эффективные бонусы объединяют статические и выборные."""
    effective = character_mod.get_effective_race_bonuses(
        "human",
        "variant_human",
        {"strength": 1, "dexterity": 1},
    )

    assert effective == {"strength": 1, "dexterity": 1}


def test_generate_stats_apply_racial_bonuses():
    """generate_stats_* применяет расовые бонусы к итоговым stats."""
    values = [15, 14, 13, 12, 10, 8]

    standard = character_mod.generate_stats_standard_array(values, "elf")
    point_buy = character_mod.generate_stats_point_buy(values, "elf")

    assert standard["dexterity"] == 14 + 2
    assert point_buy["dexterity"] == 14 + 2


def test_generate_stats_random_accepts_race_only():
    """generate_stats_random без лишних kwargs."""
    values = [15, 14, 13, 12, 10, 8]
    stats = character_mod.generate_stats_random(values, "elf")

    assert set(stats.keys()) == set(character_mod.STAT_NAMES)
    assert stats["dexterity"] == 14 + 2


def test_remaining_standard_array_pool():
    """Остаток пула уменьшается по мере назначения значений."""
    full_pool = [15, 14, 13, 12, 10, 8]
    partial_pool = [13, 12, 10, 8]
    assert character_mod.remaining_standard_array_pool([]) == full_pool
    used = character_mod.remaining_standard_array_pool([15, 14])
    assert used == partial_pool


def test_point_buy_total_cost():
    """Суммарная стоимость point-buy считается по таблице."""
    assert character_mod.point_buy_total_cost([8, 8, 8, 8, 8, 8]) == 0
    assert character_mod.point_buy_total_cost([15, 15, 15, 8, 8, 8]) == 27


def test_can_assign_point_buy_value():
    """Point-buy: допустимость значения с учётом бюджета."""
    stats = dict.fromkeys(character_mod.STAT_NAMES, 8)
    assert (
        character_mod.can_assign_point_buy_value(stats, "strength", 15) is True
    )
    stats["strength"] = 15
    stats["dexterity"] = 15
    stats["constitution"] = 15
    assert (
        character_mod.can_assign_point_buy_value(stats, "intelligence", 15)
        is False
    )
    assert (
        character_mod.can_assign_point_buy_value(stats, "constitution", 10)
        is True
    )
    assert (
        character_mod.can_assign_point_buy_value(stats, "intelligence", 16)
        is False
    )


def test_save_and_load_character(characters_dir):
    """save_character и load_characters работают с Character."""
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
    assert saved.save_slug == "hero"

    loaded = character_mod.load_characters()
    assert len(loaded) == 1
    assert loaded[0].name == "Hero"
    assert loaded[0].class_name == "fighter"

    save_path = characters_dir / "hero.json"
    assert save_path.exists()
    with open(save_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema_version"] == 1
    assert data["save_slug"] == "hero"
    assert data["class"] == "fighter"


def test_slug_from_cyrillic_name(characters_dir):
    """Кириллическое имя транслитерируется в save_slug."""
    saved = character_mod.save_character(
        name="Арагорн",
        race_id="human",
        class_id="fighter",
    )
    assert saved.save_slug == "aragorn"
    assert (characters_dir / "aragorn.json").exists()


def test_save_slug_collision(characters_dir):
    """При коллизии имён добавляется суффикс _2, _3."""
    first = character_mod.save_character(
        name="Hero",
        race_id="human",
        class_id="fighter",
    )
    second = character_mod.save_character(
        name="Hero",
        race_id="elf",
        class_id="rogue",
    )

    assert first.save_slug == "hero"
    assert second.save_slug == "hero_2"
    assert (characters_dir / "hero.json").exists()
    assert (characters_dir / "hero_2.json").exists()
    assert len(character_mod.load_characters()) == 2
