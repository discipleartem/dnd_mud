"""Сущности рас и подрас.

Следует Clean Architecture - бизнес-сущности без внешних зависимостей.
Содержат правила валидации и бизнес-логику рас.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, TYPE_CHECKING

from src.value_objects.base_validatable import BaseValidatable

if TYPE_CHECKING:
    from typing import Any


@dataclass
class Subrace(BaseValidatable):
    """Подраса персонажа.
    
    Бизнес-сущность представляющая подрасу в D&D 5e.
    Следует Clean Architecture - не зависит от внешних слоев.
    """
    
    name: str
    parent_race: str
    description: str
    ability_bonuses: Dict[str, int] = field(default_factory=dict)
    traits: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    inherit_base_abilities: bool = True
    ability_bonuses_description: str = ""
    features: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        """Валидация после инициализации."""
        self.validate()
    
    def validate(self) -> None:
        """Валидация бизнес-правил подрасы.
        
        Raises:
            ValueError: Если подраса невалидна
        """
        if not self.name or not self.name.strip():
            raise ValueError("Название подрасы не может быть пустым")
        
        if not self.parent_race or not self.parent_race.strip():
            raise ValueError("Название родительской расы не может быть пустым")
        
        for ability, bonus in self.ability_bonuses.items():
            if not isinstance(bonus, int) or bonus < 0:
                raise ValueError(f"Некорректный бонус для {ability}: {bonus}")


@dataclass
class Race(BaseValidatable):
    """Раса персонажа.
    
    Бизнес-сущность представляющая расу в D&D 5e.
    Следует Clean Architecture - не зависит от внешних слоев.
    """
    
    name: str
    description: str
    speed: int
    size: str
    ability_bonuses: Dict[str, int] = field(default_factory=dict)
    traits: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    subraces: Optional[List[Subrace]] = None
    allow_base_race_choice: bool = True


@dataclass
class RaceSelectionResult(BaseValidatable):
    """Результат выбора расы.
    
    Бизнес-сущность представляющая результат выбора расы и подрасы
    с применёнными бонусами к характеристикам.
    """
    
    race_name: str
    subrace_name: Optional[str] = None
    race: Optional[Race] = None
    subrace: Optional['Subrace'] = None
    applied_bonuses: Dict[str, int] = field(default_factory=dict)
    final_abilities: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Валидация после инициализации."""
        self.validate()
    
    def validate(self) -> None:
        """Валидация бизнес-правил результата выбора.
        
        Raises:
            ValueError: Если результат выбора невалиден
        """
        if not self.race_name or not self.race_name.strip():
            raise ValueError("Название расы не может быть пустым")
        
        if self.subrace_name and not self.subrace:
            raise ValueError("Указана подраса, но объект подрасы отсутствует")
        
        if not self.race:
            raise ValueError("Объект расы обязателен")
