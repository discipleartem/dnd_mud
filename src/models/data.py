"""
Модели данных D&D на основе dataclass.

Простые и понятные модели для создания персонажа.
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
class RaceData:
    """Данные расы из YAML."""
    id: str
    name: str
    description: str
    ability_bonuses: Dict[str, int] = field(default_factory=dict)
    ability_bonuses_description: str = ""
    size: str = Size.MEDIUM.value
    speed: int = 30
    age: Dict[str, int] = field(default_factory=dict)
    languages: List[str] = field(default_factory=list)
    features: List[Dict[str, str]] = field(default_factory=list)
    subraces: Dict[str, Dict] = field(default_factory=dict)


@dataclass
class ClassData:
    """Данные класса из YAML."""
    id: str
    name: str
    description: str
    hit_dice: int = 8
    prime_abilities: List[str] = field(default_factory=list)
    saving_throws: List[str] = field(default_factory=list)
    skill_choices: List[str] = field(default_factory=list)
    equipment: Dict[str, List[str]] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    subclasses: List[str] = field(default_factory=list)


@dataclass
class CharacterData:
    """Данные персонажа."""
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


@dataclass
class Character:
    """Персонаж D&D."""
    data: CharacterData
    
    def __post_init__(self) -> None:
        """Инициализация после создания."""
        self.abilities = self._create_abilities()
        self._update_derived_stats()
    
    def _create_abilities(self) -> Dict[str, Ability]:
        """Создать объекты характеристик."""
        return {
            "strength": Ability("Сила", self.data.strength),
            "dexterity": Ability("Ловкость", self.data.dexterity),
            "constitution": Ability("Выносливость", self.data.constitution),
            "intelligence": Ability("Интеллект", self.data.intelligence),
            "wisdom": Ability("Мудрость", self.data.wisdom),
            "charisma": Ability("Харизма", self.data.charisma)
        }
    
    def _update_derived_stats(self) -> None:
        """Обновить производные характеристики."""
        if self.data.hit_points == 0:
            class_hp_dice = self._get_class_hit_dice()
            self.data.hit_points = class_hp_dice + self.abilities["constitution"].modifier
        
        self.data.armor_class = 10 + self.abilities["dexterity"].modifier
    
    def _get_class_hit_dice(self) -> int:
        """Получить кубик здоровья для класса."""
        hit_dice_map = {
            CharacterClass.FIGHTER: 10,
            CharacterClass.ROGUE: 8,
            CharacterClass.CLERIC: 8,
            CharacterClass.BARD: 8
        }
        return hit_dice_map.get(self.data.character_class, 8)
    
    @property
    def name(self) -> str:
        return self.data.name
    
    def __str__(self) -> str:
        """Строковое представление персонажа."""
        lines = [
            f"=== {self.data.name} ===",
            f"Уровень {self.data.level} {self.data.race.value if self.data.race else 'Неизвестная раса'} {self.data.character_class.value if self.data.character_class else 'Неизвестный класс'}",
            "",
            "Характеристики:"
        ]
        
        for ability in self.abilities.values():
            lines.append(f"  {ability}")
        
        lines.extend([
            "",
            f"Хиты: {self.data.hit_points}",
            f"КД: {self.data.armor_class}",
            f"Скорость: {self.data.speed} фт.",
            f"Языки: {', '.join(self.data.languages) if self.data.languages else 'Нет'}"
        ])
        
        return "\n".join(lines)
