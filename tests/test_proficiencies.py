"""Тесты владений снаряжением."""

from core.proficiencies import (
    build_fixed_proficiencies,
    get_background_tool_proficiencies,
    get_class_proficiency_tokens,
    get_subclass_proficiency_tokens,
    has_armor_proficiency,
    has_weapon_proficiency,
    merge_proficiency_tokens,
)


def test_fighter_class_proficiencies():
    """Воин владеет простым и воинским оружием, всеми доспехами."""
    weapons, armors, tools = get_class_proficiency_tokens("fighter")
    assert "simple" in weapons
    assert "martial" in weapons
    assert "heavy" in armors
    assert "shield" in armors
    assert tools == []


def test_rogue_specific_weapons():
    """Плут — конкретное оружие и воровские инструменты."""
    weapons, armors, _ = get_class_proficiency_tokens("rogue")
    assert "simple" in weapons
    assert "longsword" in weapons
    assert "light" in armors


def test_life_domain_heavy_armor():
    """Домен жизни — тяжёлые доспехи с 1 уровня."""
    _, armors, _, _ = get_subclass_proficiency_tokens(
        "cleric", "life_domain", 1
    )
    assert "heavy" in armors


def test_valor_bard_level_1_no_martial():
    """Коллегия доблести — воинское оружие только с 3 уровня."""
    weapons, _, _, _ = get_subclass_proficiency_tokens(
        "bard", "valor_college", 1
    )
    assert "martial" not in weapons


def test_valor_bard_level_3_martial():
    """Коллегия доблести на 3 уровне — воинское оружие."""
    weapons, armors, _, _ = get_subclass_proficiency_tokens(
        "bard", "valor_college", 3
    )
    assert "martial" in weapons
    assert "medium" in armors


def test_elf_weapon_proficiency():
    """Лесной эльф — владение мечами и луками."""
    weapons, _, _ = build_fixed_proficiencies(
        "elf", "wood_elf", "fighter", None, None, 1
    )
    assert "longsword" in weapons
    assert "longbow" in weapons


def test_charlatan_background_tools():
    """Шарлатан — набор для грима и фальсификации."""
    fixed, choices = get_background_tool_proficiencies("charlatan")
    assert "disguise_kit" in fixed
    assert "forgery_kit" in fixed
    assert choices == []


def test_criminal_background_tool_choice():
    """Преступник — выбор игрового набора."""
    fixed, choices = get_background_tool_proficiencies("criminal")
    assert "thieves_tools" in fixed
    assert len(choices) == 1
    assert choices[0].pool == "gaming_sets"


def test_has_weapon_proficiency_by_category():
    """Владение simple покрывает club."""
    assert has_weapon_proficiency(["simple"], "club")
    assert not has_weapon_proficiency(["martial"], "club")


def test_has_armor_proficiency_shield():
    """Владение shield."""
    assert has_armor_proficiency(["shield"], "shield")
    assert has_armor_proficiency(["light"], "leather")


def test_merge_proficiency_tokens_dedupes():
    """merge не дублирует токены."""
    merged = merge_proficiency_tokens(["simple"], ["martial", "simple"])
    assert merged == ["simple", "martial"]
