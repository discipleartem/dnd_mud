"""Тесты владений снаряжением и навыков при создании."""

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
from core.skills import (
    apply_racial_proficiencies,
    available_skills,
    get_class_skill_config,
    get_subclass_skill_choices,
    merge_proficiencies,
    subclass_skills_active,
)

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_racial_and_class_skills() -> None:
    assert "perception" in apply_racial_proficiencies("elf", "wood_elf")
    pool, count = get_class_skill_config("fighter")
    assert count == 2 and "athletics" in pool
    assert available_skills(["athletics", "perception"], ["perception"]) == [
        "athletics"
    ]
    assert merge_proficiencies(["perception"], ["athletics"]) == [
        "perception",
        "athletics",
    ]


def test_subclass_skill_choices() -> None:
    assert subclass_skills_active("bard", "lore_college", 1) is False
    assert subclass_skills_active("bard", "lore_college", 3) is True
    choices = get_subclass_skill_choices("bard", "lore_college", 3)
    assert len(choices) == 1 and int(choices[0].get("count", 0)) == 3


def test_fighter_and_rogue_class_proficiencies() -> None:
    weapons, armors, tools = get_class_proficiency_tokens("fighter")
    assert "simple" in weapons and "martial" in weapons
    assert "heavy" in armors
    assert tools == []
    rogue_weapons, rogue_armors, _ = get_class_proficiency_tokens("rogue")
    assert "longsword" in rogue_weapons
    assert "light" in rogue_armors


def test_subclass_armor_tokens() -> None:
    _, armors, _, _ = get_subclass_proficiency_tokens(
        "cleric", "life_domain", 1
    )
    assert "heavy" in armors
    weapons, armors, _, _ = get_subclass_proficiency_tokens(
        "bard", "valor_college", 3
    )
    assert "martial" in weapons
    assert "medium" in armors


def test_build_fixed_proficiencies_elf_and_dwarf() -> None:
    weapons, _, _ = build_fixed_proficiencies(
        "elf", "wood_elf", "fighter", None, None, 1
    )
    assert "longsword" in weapons
    assert "longbow" in weapons
    _, armors, _ = build_fixed_proficiencies(
        "dwarf", "mountain_dwarf", "fighter", None, None, 1
    )
    assert "light" in armors
    assert "medium" in armors


def test_background_tools_and_proficiency_checks() -> None:
    fixed, choices = get_background_tool_proficiencies("charlatan")
    assert "disguise_kit" in fixed
    assert choices == []
    assert has_weapon_proficiency(["simple"], "club")
    assert has_armor_proficiency(["shield"], "shield")
    merged = merge_proficiency_tokens(["simple"], ["martial", "simple"])
    assert merged == ["simple", "martial"]
