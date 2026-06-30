"""Тесты владений снаряжением."""

import pytest

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


@pytest.mark.parametrize(
    "level,expect_martial,expect_medium",
    [
        (1, False, False),
        (3, True, True),
    ],
)
def test_valor_bard_martial_and_armor_by_level(
    level: int, expect_martial: bool, expect_medium: bool
) -> None:
    """Коллегия доблести — воинское оружие и средние доспехи с 3 уровня."""
    weapons, armors, _, _ = get_subclass_proficiency_tokens(
        "bard", "valor_college", level
    )
    assert ("martial" in weapons) is expect_martial
    assert ("medium" in armors) is expect_medium


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


def test_has_weapon_and_armor_proficiency():
    """Владение категориями оружия и доспехов."""
    assert has_weapon_proficiency(["simple"], "club")
    assert not has_weapon_proficiency(["martial"], "club")
    assert has_armor_proficiency(["shield"], "shield")
    assert has_armor_proficiency(["light"], "leather")


def test_merge_proficiency_tokens_dedupes():
    """merge не дублирует токены."""
    merged = merge_proficiency_tokens(["simple"], ["martial", "simple"])
    assert merged == ["simple", "martial"]


def test_dwarf_tool_proficiency_choice_and_build():
    """Дварф: инструмент на выбор; fixed-владения без инструментов до UI."""
    from core.proficiencies import get_racial_proficiency_tokens

    _, _, tools, choices = get_racial_proficiency_tokens("dwarf", None)
    assert tools == []
    assert len(choices) == 1
    assert choices[0].count == 1
    assert set(choices[0].options or []) == {
        "smith_tools",
        "brewer_supplies",
        "mason_tools",
    }

    weapons, armors, built_tools = build_fixed_proficiencies(
        "dwarf", None, "fighter", None, None, 1
    )
    assert "battleaxe" in weapons
    assert built_tools == []


def test_mountain_dwarf_armor_proficiency():
    """Горный дварф — лёгкие и средние доспехи."""
    _, armors, _ = build_fixed_proficiencies(
        "dwarf", "mountain_dwarf", "fighter", None, None, 1
    )
    assert "light" in armors
    assert "medium" in armors


def test_has_tool_proficiency_by_pool_token():
    """Токен artisans_tools покрывает конкретный ремесленный инструмент."""
    from core.proficiencies import has_tool_proficiency

    assert has_tool_proficiency(["artisans_tools"], "smith_tools")
    assert not has_tool_proficiency(["smith_tools"], "brewer_supplies")
