"""Тесты навыков при создании персонажа."""

from core.skills import (
    apply_racial_proficiencies,
    available_skills,
    get_class_skill_config,
    get_race_skill_choices_with_source,
    get_subclass_skill_choices,
    merge_proficiencies,
    subclass_skills_active,
)


def test_racial_and_class_skills() -> None:
    assert "perception" in apply_racial_proficiencies("elf", "wood_elf")
    assert apply_racial_proficiencies("human", "variant_human") == []
    choices = get_race_skill_choices_with_source("human", "variant_human")
    assert len(choices) == 1 and choices[0][1] == "subrace"

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
