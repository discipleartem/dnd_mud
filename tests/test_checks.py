"""Тесты проверок характеристик."""

from core.checks import (
    passive_skill,
    roll_d20,
    saving_throw_modifier,
    skill_check_modifier,
)
from core.models import Character


def _fighter() -> Character:
    return Character(
        name="Test",
        race="human",
        class_id="fighter",
        stats={
            "strength": 16,
            "dexterity": 10,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        },
        skills=["athletics"],
    )


def test_skill_check_modifier_with_proficiency():
    """Владение навыком добавляет бонус мастерства."""
    char = _fighter()
    mod = skill_check_modifier(char, "athletics")
    assert mod == 5  # +3 str +2 PB


def test_skill_check_modifier_without_proficiency():
    """Без владения — только модификатор характеристики."""
    char = _fighter()
    mod = skill_check_modifier(char, "stealth")
    assert mod == 0


def test_saving_throw_modifier_fighter():
    """Воин владеет спасбросками Силы и Телосложения."""
    char = _fighter()
    assert saving_throw_modifier(char, "strength") == 5
    assert saving_throw_modifier(char, "dexterity") == 0


def test_passive_skill_perception():
    """Пассивное восприятие = 10 без владения."""
    char = _fighter()
    assert passive_skill(char, "perception") == 10


def test_advantage_disadvantage_cancel():
    """Преимущество и помеха — один к20."""
    rolls = [roll_d20(advantage=True, disadvantage=True) for _ in range(20)]
    assert all(1 <= r <= 20 for r in rolls)
