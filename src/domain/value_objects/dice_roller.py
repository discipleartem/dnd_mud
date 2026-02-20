"""
Стратегии бросков кубиков для D&D MUD.

Простой паттерн Стратегия для разных типов бросков d20.
"""

from .dice import Dice


class DiceRoller:
    """Контекст для бросков кубиков."""

    @classmethod
    def roll_d20(cls, advantage: str = "none") -> tuple[int, bool, bool]:
        """Выполняет бросок d20 с указанным преимуществом/помехой.

        Args:
            advantage: Тип преимущества ("none", "advantage", "disadvantage")

        Returns:
            Кортеж (значение, крит_успех, крит_провал)
        """
        value, crit_success, crit_fail = Dice.roll_d20_with_advantage(advantage)
        return value, crit_success, crit_fail
