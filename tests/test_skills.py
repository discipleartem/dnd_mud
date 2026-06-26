"""Тесты навыков при создании персонажа."""

from core.skills import (
    apply_racial_proficiencies,
    available_skills,
    get_class_skill_config,
    get_fixed_racial_proficiencies_with_source,
    get_race_skill_choices_with_source,
    merge_proficiencies,
)


def test_elf_gets_perception_automatically():
    """Эльф получает владение Восприятием без выбора."""
    skills = apply_racial_proficiencies("elf", "wood_elf")
    assert "perception" in skills


def test_elf_perception_source_is_race():
    """Восприятие эльфа помечается источником «раса»."""
    fixed = get_fixed_racial_proficiencies_with_source("elf", "wood_elf")
    assert ("perception", "race") in fixed


def test_variant_human_skill_choice_is_subrace():
    """Выборный навык варианта человека — источник «подраса»."""
    choices = get_race_skill_choices_with_source("human", "variant_human")
    assert len(choices) == 1
    mechanics, source = choices[0]
    assert int(mechanics.get("count", 0)) == 1
    assert source == "subrace"


def test_variant_human_has_no_auto_skills():
    """Вариант человека не даёт фиксированных навыков."""
    skills = apply_racial_proficiencies("human", "variant_human")
    assert skills == []


def test_available_skills_excludes_proficient():
    """Занятые навыки исключаются из доступного пула."""
    pool = ["athletics", "perception", "stealth"]
    proficient = ["perception"]
    assert available_skills(pool, proficient) == ["athletics", "stealth"]


def test_fighter_class_skill_config():
    """Воин: 2 навыка из списка класса."""
    pool, count = get_class_skill_config("fighter")
    assert count == 2
    assert "athletics" in pool
    assert "expertise" not in pool


def test_rogue_class_skill_config_has_perception():
    """Плут: полный PHB-список без expertise."""
    pool, count = get_class_skill_config("rogue")
    assert count == 4
    assert "perception" in pool
    assert "persuasion" in pool
    assert "expertise" not in pool


def test_merge_proficiencies_dedupes():
    """merge_proficiencies не дублирует навыки."""
    merged = merge_proficiencies(["perception"], ["athletics", "perception"])
    assert merged == ["perception", "athletics"]
