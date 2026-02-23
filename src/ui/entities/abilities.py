from dataclasses import dataclass, field
from typing import Dict, Optional, List
from enum import Enum
import random


class Ability(Enum):
    """Характеристики D&D 5e."""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"
    
    def get_localized_name(self) -> str:
        """Получить локализованное название характеристики."""
        from pathlib import Path
        import sys
        sys.path.append(str(Path(__file__).parent.parent.parent.parent))
        from i18n import t
        return t(f'abilities.{self.value}.name')
    
    def get_localized_description(self) -> str:
        """Получить локализованное описание характеристики."""
        from pathlib import Path
        import sys
        sys.path.append(str(Path(__file__).parent.parent.parent.parent))
        from i18n import t
        return t(f'abilities.{self.value}.description')


@dataclass
class AbilityScores:
    """Характеристики персонажа с базовыми значениями и бонусами."""
    base_scores: Dict[Ability, int] = field(default_factory=dict)
    racial_bonuses: Dict[Ability, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Инициализация базовых значений."""
        if not self.base_scores:
            for ability in Ability:
                self.base_scores[ability] = 10  # Базовое значение
    
    def get_total_score(self, ability: Ability) -> int:
        """Получить итоговое значение характеристики с бонусами."""
        base = self.base_scores.get(ability, 10)
        bonus = self.racial_bonuses.get(ability, 0)
        return base + bonus
    
    def get_modifier(self, ability: Ability) -> int:
        """Получить модификатор характеристики."""
        total = self.get_total_score(ability)
        return (total - 10) // 2
    
    def set_base_score(self, ability: Ability, value: int) -> None:
        """Установить базовое значение характеристики."""
        if 1 <= value <= 20:
            self.base_scores[ability] = value
        else:
            raise ValueError(f"Значение характеристики должно быть от 1 до 20")
    
    def apply_racial_bonuses(self, bonuses: Dict[str, int]) -> None:
        """Применить расовые бонусы к характеристикам."""
        self.racial_bonuses.clear()
        for ability_name, bonus in bonuses.items():
            try:
                ability = Ability(ability_name)
                self.racial_bonuses[ability] = bonus
            except ValueError:
                continue  # Игнорируем неизвестные характеристики
    
    def get_all_totals(self) -> Dict[Ability, int]:
        """Получить все итоговые значения характеристик."""
        return {ability: self.get_total_score(ability) for ability in Ability}
    
    def get_all_modifiers(self) -> Dict[Ability, int]:
        """Получить все модификаторы характеристик."""
        return {ability: self.get_modifier(ability) for ability in Ability}


class PointBuyCosts:
    """Стоимость значений характеристик при покупке очков."""
    
    COSTS = {
        8: 0,
        9: 1,
        10: 2,
        11: 3,
        12: 4,
        13: 5,
        14: 7,
        15: 9,
    }
    
    @classmethod
    def get_cost(cls, value: int) -> int:
        """Получить стоимость значения."""
        return cls.COSTS.get(value, 0)
    
    @classmethod
    def get_valid_values(cls) -> List[int]:
        """Получить список допустимых значений."""
        return list(cls.COSTS.keys())


class DiceRoller:
    """Утилита для бросков костей."""
    
    @staticmethod
    def roll_ability_score() -> int:
        """Генерация характеристики: 4d6 - наименьший."""
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls.sort()
        return sum(rolls[1:])  # Сумма трёх наибольших
    
    @staticmethod
    def roll_multiple_scores(count: int = 6) -> List[int]:
        """Сгенерировать несколько значений характеристик."""
        return [DiceRoller.roll_ability_score() for _ in range(count)]


class StandardArray:
    """Стандартный массив значений характеристик."""
    
    VALUES = [15, 14, 13, 12, 10, 8]
    
    @classmethod
    def get_values(cls) -> List[int]:
        """Получить стандартные значения."""
        return cls.VALUES.copy()


class PointBuySystem:
    """Система покупки очков характеристик."""
    
    POINTS_TOTAL = 27
    
    def __init__(self):
        self.points_spent = 0
    
    def get_remaining_points(self) -> int:
        """Получить оставшиеся очки."""
        return self.POINTS_TOTAL - self.points_spent
    
    def can_afford(self, value: int) -> bool:
        """Проверить, можно ли купить значение."""
        cost = PointBuyCosts.get_cost(value)
        return cost <= self.get_remaining_points()
    
    def buy_score(self, old_value: int, new_value: int) -> bool:
        """Купить значение характеристики."""
        if not PointBuyCosts.get_valid_values().__contains__(new_value):
            return False
        
        old_cost = PointBuyCosts.get_cost(old_value)
        new_cost = PointBuyCosts.get_cost(new_value)
        cost_diff = new_cost - old_cost
        
        if cost_diff <= self.get_remaining_points():
            self.points_spent += cost_diff
            return True
        return False
    
    def refund_score(self, old_value: int, new_value: int) -> None:
        """Вернуть очки при уменьшении значения."""
        old_cost = PointBuyCosts.get_cost(old_value)
        new_cost = PointBuyCosts.get_cost(new_value)
        cost_diff = old_cost - new_cost
        self.points_spent -= cost_diff
        if self.points_spent < 0:
            self.points_spent = 0


class RandomGeneration:
    """Случайная генерация характеристик."""
    
    @staticmethod
    def generate_scores() -> List[int]:
        """Сгенерировать 6 значений характеристик."""
        return DiceRoller.roll_multiple_scores(6)
    
    @staticmethod
    def assign_randomly(scores: List[int]) -> Dict[Ability, int]:
        """Случайно распределить значения по характеристикам (hardcore режим)."""
        abilities = list(Ability)
        random.shuffle(abilities)
        return {ability: score for ability, score in zip(abilities, scores)}
