"""Бизнес-сущности D&D.

Содержит основные сущности предметной области без внешних зависимостей.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class CharacterClass(Enum):
    """Классы персонажей."""
    FIGHTER = "fighter"
    ROGUE = "rogue"
    CLERIC = "cleric"
    BARD = "bard"


class CharacterRace(Enum):
    """Расы персонажей."""
    HUMAN = "human"
    ELF = "elf"
    HALF_ORC = "half_orc"


class Size(Enum):
    """Размеры персонажей."""
    TINY = "TINY"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    HUGE = "HUGE"
    GARGANTUAN = "GARGANTUAN"


@dataclass
class Ability:
    """Характеристика персонажа."""
    
    name: str
    value: int
    
    @property
    def modifier(self) -> int:
        """Модификатор характеристики."""
        return (self.value - 10) // 2
    
    def __str__(self) -> str:
        return f"{self.name}: {self.value} ({self.modifier:+})"


@dataclass
class CharacterData:
    """Данные персонажа."""
    
    id: Optional[int] = None
    name: str = ""
    race: Optional[CharacterRace] = None
    character_class: Optional[CharacterClass] = None
    level: int = 1
    
    # Характеристики
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    # Дополнительные параметры
    size: str = Size.MEDIUM.value
    speed: int = 30
    languages: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    
    # Параметры боя
    hit_points: int = 0
    armor_class: int = 10
    proficiency_bonus: int = 2


class Character:
    """Персонаж D&D.
    
    Бизнес-сущность, содержащая правила и логику предметной области.
    Не зависит от внешних слоев.
    """
    
    def __init__(self, data: CharacterData) -> None:
        """Инициализировать персонажа."""
        self._data = data
        self._abilities = self._create_abilities()
        self._update_derived_stats()
    
    def _create_abilities(self) -> Dict[str, Ability]:
        """Создать объекты характеристик."""
        return {
            "strength": Ability("Сила", self._data.strength),
            "dexterity": Ability("Ловкость", self._data.dexterity),
            "constitution": Ability("Выносливость", self._data.constitution),
            "intelligence": Ability("Интеллект", self._data.intelligence),
            "wisdom": Ability("Мудрость", self._data.wisdom),
            "charisma": Ability("Харизма", self._data.charisma)
        }
    
    def _update_derived_stats(self) -> None:
        """Обновить производные характеристики."""
        if self._data.hit_points == 0:
            class_hp_dice = self._get_class_hit_dice()
            self._data.hit_points = class_hp_dice + self._abilities["constitution"].modifier
        
        self._data.armor_class = 10 + self._abilities["dexterity"].modifier
    
    def _get_class_hit_dice(self) -> int:
        """Получить кубик здоровья для класса."""
        hit_dice_map = {
            CharacterClass.FIGHTER: 10,
            CharacterClass.ROGUE: 8,
            CharacterClass.CLERIC: 8,
            CharacterClass.BARD: 8
        }
        return hit_dice_map.get(self._data.character_class, 8)
    
    @property
    def data(self) -> CharacterData:
        """Получить данные персонажа."""
        return self._data
    
    @property
    def abilities(self) -> Dict[str, Ability]:
        """Получить характеристики персонажа."""
        return self._abilities
    
    @property
    def name(self) -> str:
        """Получить имя персонажа."""
        return self._data.name
    
    def is_alive(self) -> bool:
        """Проверить, жив ли персонаж."""
        return self._data.hit_points > 0
    
    def take_damage(self, damage: int) -> None:
        """Получить урон."""
        self._data.hit_points = max(0, self._data.hit_points - damage)
    
    def heal(self, amount: int) -> None:
        """Лечить персонажа."""
        max_hp = self._get_max_hit_points()
        self._data.hit_points = min(max_hp, self._data.hit_points + amount)
    
    def _get_max_hit_points(self) -> int:
        """Получить максимальное количество хитов."""
        class_hp_dice = self._get_class_hit_dice()
        return class_hp_dice + self._abilities["constitution"].modifier
    
    def __str__(self) -> str:
        """Строковое представление персонажа."""
        lines = [
            f"=== {self._data.name} ===",
            f"Уровень {self._data.level} {self._data.race.value if self._data.race else 'Неизвестная раса'} {self._data.character_class.value if self._data.character_class else 'Неизвестный класс'}",
            "",
            "Характеристики:"
        ]
        
        for ability in self._abilities.values():
            lines.append(f"  {ability}")
        
        lines.extend([
            "",
            f"Хиты: {self._data.hit_points}",
            f"КД: {self._data.armor_class}",
            f"Скорость: {self._data.speed} фт.",
            f"Языки: {', '.join(self._data.languages) if self._data.languages else 'Нет'}"
        ])
        
        return "\n".join(lines)