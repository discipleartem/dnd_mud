"""Тесты констант PHB."""

from core.constants import difficulty_class, proficiency_bonus


def test_proficiency_bonus_level_1():
    """На 1 уровне бонус мастерства +2."""
    assert proficiency_bonus(1) == 2


def test_proficiency_bonus_level_5():
    """На 5 уровне бонус мастерства +3."""
    assert proficiency_bonus(5) == 3


def test_difficulty_class_medium():
    """Сл medium = 10."""
    assert difficulty_class("medium") == 10
