# src/core/mechanics/dice.py
"""
Core система бросков кубиков D&D.

Применяемые паттерны:
- Factory (Фабрика) — создание разных типов кубиков и бросков
- Strategy (Стратегия) — разные модификаторы бросков (advantage/disadvantage)
- Value Object (Объект-значение) — результат броска как неизменяемый объект
- Repository (Хранилище) — конфигурация кубиков из YAML

Применяемые принципы:
- Single Responsibility — каждый класс отвечает за одну вещь
- Open/Closed — легко добавлять новые типы кубиков и модификаторы
- Dependency Inversion — зависимость от абстракций, а не реализаций
"""

import random
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from enum import Enum


class RollModifierType(Enum):
    """Типы модификаторов бросков."""
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"
    TRIPLE_ADVANTAGE = "triple_advantage"
    TRIPLE_DISADVANTAGE = "triple_disadvantage"


class SpecialResultType(Enum):
    """Типы особых результатов бросков."""
    CRITICAL_SUCCESS = "critical_success"
    CRITICAL_FAILURE = "critical_failure"
    NORMAL = "normal"


@dataclass(frozen=True)
class DiceConfig:
    """Конфигурация типа кубика."""
    sides: int
    name: str
    description: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiceConfig':
        """Создает конфигурацию из словаря."""
        return cls(
            sides=data['sides'],
            name=data['name'],
            description=data.get('description', '')
        )


@dataclass
class DiceResult:
    """Результат броска кубика (Value Object)."""
    value: int
    dice_type: str
    rolls: List[int] = field(default_factory=list)
    modifier_type: RollModifierType = RollModifierType.NORMAL
    special_result: SpecialResultType = SpecialResultType.NORMAL
    modifier: int = 0
    
    @property
    def total(self) -> int:
        """Возвращает итоговое значение с модификатором."""
        return self.value + self.modifier
    
    @property
    def is_critical(self) -> bool:
        """Проверяет, является ли результат критическим."""
        return self.special_result != SpecialResultType.NORMAL
    
    @property
    def is_critical_success(self) -> bool:
        """Проверяет, является ли результат критическим успехом."""
        return self.special_result == SpecialResultType.CRITICAL_SUCCESS
    
    @property
    def is_critical_failure(self) -> bool:
        """Проверяет, является ли результат критическим провалом."""
        return self.special_result == SpecialResultType.CRITICAL_FAILURE
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует в словарь."""
        return {
            'value': self.value,
            'total': self.total,
            'dice_type': self.dice_type,
            'rolls': self.rolls,
            'modifier_type': self.modifier_type.value,
            'special_result': self.special_result.value,
            'modifier': self.modifier,
            'is_critical': self.is_critical
        }


class Dice:
    """Кубик для бросков (Entity)."""
    
    def __init__(self, dice_type: str, config: Optional[DiceConfig] = None):
        """Инициализирует кубик."""
        self.dice_type = dice_type
        self._config = config or self._load_dice_config(dice_type)
    
    def roll(self, modifier: int = 0) -> DiceResult:
        """Выполняет обычный бросок кубика."""
        if not self._config:
            raise ValueError(f"Неизвестный тип кубика: {self.dice_type}")
        
        value = random.randint(1, self._config.sides)
        special_result = self._check_special_result(value)
        
        return DiceResult(
            value=value,
            dice_type=self.dice_type,
            rolls=[value],
            modifier=modifier,
            special_result=special_result
        )
    
    def roll_with_modifier(self, modifier_type: RollModifierType, modifier: int = 0) -> DiceResult:
        """Выполняет бросок с модификатором (advantage/disadvantage)."""
        if not self._config:
            raise ValueError(f"Неизвестный тип кубика: {self.dice_type}")
        
        modifier_config = RollModifierConfig._load_config(modifier_type.value)
        rolls = [random.randint(1, self._config.sides) for _ in range(modifier_config.rolls)]
        
        if modifier_config.type == "best_of":
            value = max(rolls)
        elif modifier_config.type == "worst_of":
            value = min(rolls)
        else:
            value = rolls[0]  # Обычный бросок
        
        special_result = self._check_special_result(value)
        
        return DiceResult(
            value=value,
            dice_type=self.dice_type,
            rolls=rolls,
            modifier_type=modifier_type,
            modifier=modifier,
            special_result=special_result
        )
    
    def _check_special_result(self, value: int) -> SpecialResultType:
        """Проверяет особые результаты (криты)."""
        if self.dice_type == "d20":
            if value == 20:
                return SpecialResultType.CRITICAL_SUCCESS
            elif value == 1:
                return SpecialResultType.CRITICAL_FAILURE
        return SpecialResultType.NORMAL
    
    @property
    def sides(self) -> int:
        """Возвращает количество граней кубика."""
        return self._config.sides if self._config else 0
    
    @property
    def name(self) -> str:
        """Возвращает название кубика."""
        return self._config.name if self._config else self.dice_type
    
    @staticmethod
    def _load_dice_config(dice_type: str) -> Optional[DiceConfig]:
        """Загружает конфигурацию кубика из YAML."""
        try:
            config_path = Path(__file__).parent.parent.parent.parent / "data" / "yaml" / "dice" / "core_dice.yaml"
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            dice_data = config.get('dice_types', {}).get(dice_type)
            if dice_data:
                return DiceConfig.from_dict(dice_data)
        except FileNotFoundError:
            pass
        
        # Fallback для базовых кубиков
        fallback_configs = {
            'd4': DiceConfig(4, 'd4'),
            'd6': DiceConfig(6, 'd6'),
            'd8': DiceConfig(8, 'd8'),
            'd10': DiceConfig(10, 'd10'),
            'd12': DiceConfig(12, 'd12'),
            'd20': DiceConfig(20, 'd20'),
            'd100': DiceConfig(100, 'd100')
        }
        return fallback_configs.get(dice_type)


class RollModifierConfig:
    """Конфигурация модификаторов бросков."""
    
    _config_cache: Dict[str, 'RollModifierConfig'] = {}
    
    def __init__(self, name: str, description: str, type: str, rolls: int):
        """Инициализирует конфигурацию модификатора."""
        self.name = name
        self.description = description
        self.type = type
        self.rolls = rolls
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RollModifierConfig':
        """Создает конфигурацию из словаря."""
        return cls(
            name=data['name'],
            description=data['description'],
            type=data['type'],
            rolls=data['rolls']
        )
    
    @classmethod
    def _load_config(cls, modifier_name: str) -> Optional['RollModifierConfig']:
        """Загружает конфигурацию модификатора из YAML."""
        if modifier_name in cls._config_cache:
            return cls._config_cache[modifier_name]
        
        try:
            config_path = Path(__file__).parent.parent.parent.parent / "data" / "yaml" / "dice" / "core_dice.yaml"
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            modifier_data = config.get('roll_modifiers', {}).get(modifier_name)
            if modifier_data:
                modifier_config = cls.from_dict(modifier_data)
                cls._config_cache[modifier_name] = modifier_config
                return modifier_config
        except FileNotFoundError:
            pass
        
        # Fallback конфигурации
        fallback_configs = {
            'advantage': cls('advantage', 'Преимущество', 'best_of', 2),
            'disadvantage': cls('disadvantage', 'Помеха', 'worst_of', 2),
            'triple_advantage': cls('triple_advantage', 'Тройное преимущество', 'best_of', 3),
            'triple_disadvantage': cls('triple_disadvantage', 'Тройная помеха', 'worst_of', 3)
        }
        config = fallback_configs.get(modifier_name)
        if config:
            cls._config_cache[modifier_name] = config
        return config


class DiceRoll:
    """Фабрика для создания различных типов бросков."""
    
    @staticmethod
    def create(dice_type: str) -> Dice:
        """Создает кубик указанного типа."""
        return Dice(dice_type)
    
    @staticmethod
    def roll(dice_type: str, modifier: int = 0) -> DiceResult:
        """Выполняет простой бросок."""
        dice = Dice(dice_type)
        return dice.roll(modifier)
    
    @staticmethod
    def roll_with_advantage(dice_type: str, modifier: int = 0) -> DiceResult:
        """Выполняет бросок с преимуществом."""
        dice = Dice(dice_type)
        return dice.roll_with_modifier(RollModifierType.ADVANTAGE, modifier)
    
    @staticmethod
    def roll_with_disadvantage(dice_type: str, modifier: int = 0) -> DiceResult:
        """Выполняет бросок с помехой."""
        dice = Dice(dice_type)
        return dice.roll_with_modifier(RollModifierType.DISADVANTAGE, modifier)
    
    @staticmethod
    def roll_multiple(dice_type: str, count: int, modifier: int = 0) -> List[DiceResult]:
        """Выполняет несколько бросков."""
        dice = Dice(dice_type)
        return [dice.roll(modifier) for _ in range(count)]
    
    @staticmethod
    def roll_dice_pool(dice_types: List[str], modifier: int = 0) -> List[DiceResult]:
        """Выполняет бросок пула кубиков разных типов."""
        return [Dice(dice_type).roll(modifier) for dice_type in dice_types]


class DiceValidator:
    """Валидатор параметров бросков."""
    
    @staticmethod
    def validate_dice_type(dice_type: str) -> bool:
        """Проверяет корректность типа кубика."""
        try:
            config = Dice._load_dice_config(dice_type)
            return config is not None
        except:
            return False
    
    @staticmethod
    def validate_modifier(modifier: int) -> bool:
        """Проверяет корректность модификатора."""
        return -1000 <= modifier <= 1000
    
    @staticmethod
    def validate_dice_count(count: int) -> bool:
        """Проверяет корректность количества кубиков."""
        return 1 <= count <= 100


# Удобные функции для использования
def roll_d20(modifier: int = 0) -> DiceResult:
    """Бросок d20."""
    return DiceRoll.roll('d20', modifier)


def roll_d20_advantage(modifier: int = 0) -> DiceResult:
    """Бросок d20 с преимуществом."""
    return DiceRoll.roll_with_advantage('d20', modifier)


def roll_d20_disadvantage(modifier: int = 0) -> DiceResult:
    """Бросок d20 с помехой."""
    return DiceRoll.roll_with_disadvantage('d20', modifier)


def roll_damage(dice_type: str, count: int = 1, modifier: int = 0) -> int:
    """Бросок урона."""
    results = DiceRoll.roll_multiple(dice_type, count, modifier)
    return sum(result.total for result in results)


# Пример использования
if __name__ == "__main__":
    # Простые броски
    print("=== Простые броски ===")
    print(f"d20: {roll_d20().to_dict()}")
    print(f"d20+5: {roll_d20(5).to_dict()}")
    
    # Броски с модификаторами
    print("\n=== Броски с модификаторами ===")
    print(f"d20 с преимуществом: {roll_d20_advantage().to_dict()}")
    print(f"d20 с помехой: {roll_d20_disadvantage().to_dict()}")
    
    # Броски урона
    print("\n=== Броски урона ===")
    print(f"2d6+3: {roll_damage('d6', 2, 3)}")
    print(f"1d8: {roll_damage('d8', 1)}")
    
    # Пул кубиков
    print("\n=== Пул кубиков ===")
    pool_results = DiceRoll.roll_dice_pool(['d6', 'd8', 'd4'])
    for i, result in enumerate(pool_results):
        print(f"Кубик {i+1}: {result.to_dict()}")
