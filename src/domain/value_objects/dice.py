import random
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class RollType(Enum):
    """Типы бросков."""
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"



@dataclass
class DiceResult:
    """Результат броска кубика."""
    value: int
    rolls: List[int] = None
    roll_type: RollType = RollType.NORMAL
    modifier: int = 0
    
    def __post_init__(self) -> None:
        self.rolls = self.rolls or [self.value]
    
    @property
    def total(self) -> int:
        """Возвращает итоговое значение с модификатором."""
        return self.value + self.modifier
    
    @property
    def is_critical_success(self) -> bool:
        """Проверяет, является ли результат критическим успехом."""
        return self.value == 20
    
    @property
    def is_critical_failure(self) -> bool:
        """Проверяет, является ли результат критическим провалом."""
        return self.value == 1


class Dice:
    """Простой класс для бросков кубиков."""
    
    @staticmethod
    def roll_d20(roll_type: RollType = RollType.NORMAL, modifier: int = 0) -> DiceResult:
        """Выполняет бросок d20."""
        if roll_type == RollType.ADVANTAGE:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            value = max(rolls)
        elif roll_type == RollType.DISADVANTAGE:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            value = min(rolls)
        else:
            rolls = [random.randint(1, 20)]
            value = rolls[0]
        
        return DiceResult(value=value, rolls=rolls, roll_type=roll_type, modifier=modifier)
    
    @staticmethod
    def roll(sides: int, count: int = 1, modifier: int = 0) -> int:
        """Выполняет простой бросок кубика."""
        return sum(random.randint(1, sides) for _ in range(count)) + modifier


# Удобные функции
def roll_d20(advantage: str = "none", modifier: int = 0) -> tuple[int, int, bool, bool]:
    """Бросок d20 для совместимости с Character."""
    roll_type_map = {
        "advantage": RollType.ADVANTAGE,
        "disadvantage": RollType.DISADVANTAGE,
        "none": RollType.NORMAL
    }
    
    result = Dice.roll_d20(roll_type_map.get(advantage, RollType.NORMAL), modifier)
    return result.value, result.total, result.is_critical_success, result.is_critical_failure
