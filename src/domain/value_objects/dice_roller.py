"""
Стратегии бросков кубиков для D&D MUD.

Простой паттерн Стратегия для разных типов бросков d20.
"""

from .dice import roll_d20


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
        value, total, crit_success, crit_fail = roll_d20(advantage)
        return value, crit_success, crit_fail
