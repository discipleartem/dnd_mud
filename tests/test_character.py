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


def test_save_easy_starts_at_level_three(characters_dir):
    """Режим easy: персонаж создаётся с 3 уровня."""
    stats = dict.fromkeys(character_mod.STAT_NAMES, 12)
    saved = character_mod.save_character(
        name="EasyHero",
        race_id="human",
        class_id="fighter",
        difficulty="easy",
        stats=stats,
        subclass_id="champion",
    )
    assert saved.level == 3
    assert saved.subclass_id == "champion"
    assert saved.max_hp > character_mod.starting_max_hp("fighter", stats)


def test_save_normal_starts_at_level_one_with_subclass(characters_dir):
    """Режим normal: подкласс при создании, старт с 1 уровня."""
    stats = dict.fromkeys(character_mod.STAT_NAMES, 12)
    saved = character_mod.save_character(
        name="NormHero",
        race_id="human",
        class_id="fighter",
        difficulty="normal",
        stats=stats,
        subclass_id="champion",
    )
    assert saved.level == 1
    assert saved.subclass_id == "champion"


def test_save_with_subclass_persisted(characters_dir):
    """subclass_id сохраняется в JSON."""
    character_mod.save_character(
        name="ClericHero",
        race_id="human",
        class_id="cleric",
        difficulty="normal",
        subclass_id="life_domain",
        stats=dict.fromkeys(character_mod.STAT_NAMES, 10),
    )
    loaded = character_mod.load_characters()[-1]
    assert loaded.subclass_id == "life_domain"


def test_save_skills_and_expertise_persisted(characters_dir):
    """Навыки и компетентность сохраняются в JSON."""
    saved = character_mod.save_character(
        name="RogueHero",
        race_id="human",
        class_id="rogue",
        stats=dict.fromkeys(character_mod.STAT_NAMES, 10),
        skills=["stealth", "perception", "athletics", "deception"],
        skill_expertise=["stealth", "athletics"],
        tool_expertise=[],
    )
    assert saved.skills == [
        "stealth",
        "perception",
        "athletics",
        "deception",
    ]
    assert saved.skill_expertise == ["stealth", "athletics"]

    save_path = characters_dir / "roguehero.json"
    with open(save_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["skills"] == saved.skills
    assert data["skill_expertise"] == saved.skill_expertise

    loaded = character_mod.load_characters()[-1]
    assert loaded.skills == saved.skills
    assert loaded.skill_expertise == saved.skill_expertise


def test_save_languages_and_background_persisted(characters_dir):
    """Языки и предыстория сохраняются в JSON."""
    saved = character_mod.save_character(
        name="SageHero",
        race_id="human",
        class_id="wizard",
        stats=dict.fromkeys(character_mod.STAT_NAMES, 10),
        languages=["common", "elvish", "dwarvish"],
        background_id="sage",
    )
    assert saved.languages == ["common", "elvish", "dwarvish"]
    assert saved.background_id == "sage"

    save_path = characters_dir / "sagehero.json"
    with open(save_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["languages"] == saved.languages
    assert data["background"] == "sage"

    loaded = character_mod.load_characters()[-1]
    assert loaded.languages == saved.languages
    assert loaded.background_id == saved.background_id


def test_starting_max_hp_floor_and_max_hp_field(characters_dir):
    """HP на 1 уровне (normal): max(1, кость + CON), current_hp == max_hp."""
    stats = {
        "strength": 10,
        "dexterity": 10,
        "constitution": 8,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10,
    }
    saved = character_mod.save_character(
        name="LowCon",
        race_id="human",
        class_id="bard",
        stats=stats,
        difficulty="normal",
    )

    assert saved.max_hp == 7
    assert saved.current_hp == saved.max_hp
    assert saved.max_hp >= 1


def test_hardcore_creation_uses_rolls(characters_dir, monkeypatch):
    """HardCore: HP при создании — сумма бросков кости по уровням."""
    stats = dict.fromkeys(character_mod.STAT_NAMES, 10)
    stats["constitution"] = 14

    rolls_level1 = iter([5])

    monkeypatch.setattr(
        "core.progression.roll",
        lambda count, sides, modifier=0: next(rolls_level1) + modifier,
    )
    saved = character_mod.save_character(
        name="HardHero",
        race_id="human",
        class_id="fighter",
        difficulty="hardcore",
        stats=stats,
    )
    assert saved.level == 1
    assert saved.max_hp == 7

    rolls_level3 = iter([5, 8, 3])
    monkeypatch.setattr(
        "core.progression.roll",
        lambda count, sides, modifier=0: next(rolls_level3) + modifier,
    )
    saved_level3 = character_mod.save_character(
        name="HardLvl3",
        race_id="human",
        class_id="fighter",
        difficulty="hardcore",
        level=3,
        stats=stats,
        subclass_id="champion",
    )
    assert saved_level3.level == 3
    assert saved_level3.max_hp == 22


def test_validate_final_stats_rejects_over_20():
    """Потолок 20 после всех бонусов."""
    stats = dict.fromkeys(character_mod.STAT_NAMES, 10)
    stats["strength"] = 21

    assert character_mod.validate_final_stats(stats) == ("strength", 21)
    ok_stats = dict.fromkeys(character_mod.STAT_NAMES, 20)
    assert character_mod.validate_final_stats(ok_stats) is None


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
    assert data["max_hp"] == saved.max_hp
    assert "created_at" in data


def test_load_characters_sorted_by_creation_date(characters_dir):
    """load_characters возвращает персонажей от старых к новым."""
    old_data = {
        "schema_version": 1,
        "name": "Zeta",
        "race": "human",
        "class": "fighter",
        "save_slug": "zeta",
        "created_at": "2024-01-01T00:00:00+00:00",
    }
    new_data = {
        "schema_version": 1,
        "name": "Alpha",
        "race": "elf",
        "class": "rogue",
        "save_slug": "alpha",
        "created_at": "2024-06-01T00:00:00+00:00",
    }
    characters_dir.mkdir(parents=True, exist_ok=True)
    (characters_dir / "alpha.json").write_text(
        json.dumps(new_data), encoding="utf-8"
    )
    (characters_dir / "zeta.json").write_text(
        json.dumps(old_data), encoding="utf-8"
    )

    loaded = character_mod.load_characters()

    assert [c.name for c in loaded] == ["Zeta", "Alpha"]


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


def test_delete_character(characters_dir):
    """delete_character удаляет файл и персонаж пропадает из списка."""
    saved = character_mod.save_character(
        name="Hero",
        race_id="human",
        class_id="fighter",
    )
    assert saved.save_slug is not None
    assert character_mod.delete_character(saved.save_slug) is True
    assert len(character_mod.load_characters()) == 0
    assert not (characters_dir / "hero.json").exists()
    assert character_mod.delete_character("missing") is False


def test_delete_all_characters(characters_dir):
    """delete_all_characters удаляет всех персонажей."""
    character_mod.save_character(
        name="Hero",
        race_id="human",
        class_id="fighter",
    )
    character_mod.save_character(
        name="Elf",
        race_id="elf",
        class_id="rogue",
    )

    deleted = character_mod.delete_all_characters()

    assert deleted == 2
    assert len(character_mod.load_characters()) == 0
    assert list(characters_dir.glob("*.json")) == []


def test_save_character_applies_feat_bonuses_to_base_stats(characters_dir):
    """save_character применяет бонусы черт к базовым stats."""
    stats = dict.fromkeys(character_mod.STAT_NAMES, 10)
    saved = character_mod.save_character(
        name="FeatHero",
        race_id="human",
        class_id="fighter",
        stats=stats,
        feat_ids=["resilient"],
        feat_choices={"resilient": {"ability": "constitution"}},
    )
    assert saved.stats["constitution"] == 11


def test_save_character_skips_feat_stat_bonuses_when_stats_final(
    characters_dir,
):
    """stats уже с бонусами черты — повторно не применять."""
    from core.feats import apply_feats_to_stats

    base = dict.fromkeys(character_mod.STAT_NAMES, 10)
    base["constitution"] = 13
    feat_ids = ["resilient"]
    feat_choices = {"resilient": {"ability": "constitution"}}
    with_feat = apply_feats_to_stats(base, feat_ids, feat_choices)
    saved = character_mod.save_character(
        name="FeatHero",
        race_id="human",
        class_id="fighter",
        stats=with_feat,
        feat_ids=feat_ids,
        feat_choices=feat_choices,
        apply_feat_stat_bonuses=False,
    )
    assert saved.stats["constitution"] == 14
