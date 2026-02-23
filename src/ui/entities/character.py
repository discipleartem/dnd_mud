from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Union
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
import yaml

if TYPE_CHECKING:
    from .race import Race, Subrace
    from .language_loader import Language
    from .abilities import AbilityScores

# Импорт локализации
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from i18n import t


class Size(Enum):
    """Размер персонажа с поддержкой локализации."""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"
    COLOSSAL = "colossal"
    
    def get_localized_name(self) -> str:
        """Получить локализованное название размера."""
        return t(f"character.size.{self.value}")
    
    def __str__(self) -> str:
        """Строковое представление с локализацией."""
        return self.get_localized_name()




    

@dataclass
class Character:
    name: str = "Безымянный"
    race: Optional['Race'] = None
    _class: str = ""
    level: int = 1
    subrace: Union['Subrace', None] = None
    sub_class: Union[str, None] = None
    ability_scores: Optional['AbilityScores'] = None
    
    @property
    def size(self) -> Size:
        """Получить размер персонажа от расы."""
        return self.race.size if self.race else Size.MEDIUM
    
    @property
    def speed(self) -> int:
        """Получить скорость персонажа от расы."""
        return self.race.speed if self.race else 30
    
    @property
    def age(self) -> Dict[str, int]:
        """Получить возрастные характеристики от расы."""
        return self.race.age if self.race else {}
    
    @property
    def languages(self) -> List[str]:
        """Получить языки персонажа от расы и подрасы."""
        languages = []
        if self.race:
            languages.extend(self.race.languages)
        if self.subrace:
            languages.extend(self.subrace.languages)
        return languages
    
    def get_language_objects(self) -> List['Language']:
        """Получить объекты языков персонажа с поддержкой локализации."""
        from .language_loader import LanguageLoader
        
        loader = LanguageLoader()
        language_objects = []
        
        for lang_code in self.languages:
            lang_obj = loader.get_language(lang_code)
            if lang_obj:
                language_objects.append(lang_obj)
        
        return language_objects
    
    def get_learnable_languages(self) -> List['Language']:
        """Получить языки, которые может изучить персонаж."""
        from .language_loader import LanguageLoader
        
        loader = LanguageLoader()
        learnable = set()
        
        # Языки доступные для расы
        if self.race:
            race_code = self.race.name.lower().replace(' ', '_')
            race_languages = loader.get_learnable_languages_for_race(race_code)
            learnable.update(race_languages)
        
        # Языки доступные для класса
        if self._class:
            class_code = self._class.lower().replace(' ', '_')
            class_languages = loader.get_learnable_languages_for_class(class_code)
            learnable.update(class_languages)
        
        # Удаляем уже известные языки
        known_codes = {lang.code for lang in self.get_language_objects()}
        return [lang for lang in learnable if lang.code not in known_codes]
    
    def can_learn_language(self, lang_code: str) -> bool:
        """Проверить, может ли персонаж изучить конкретный язык."""
        from .language_loader import LanguageLoader
        
        loader = LanguageLoader()
        language = loader.get_language(lang_code)
        
        if not language:
            return False
        
        # Нельзя изучать уже известные языки
        if lang_code in self.languages:
            return False
        
        # Проверка доступности для расы
        if self.race:
            race_code = self.race.name.lower().replace(' ', '_')
            if language.is_learnable_by_race(race_code):
                return True
        
        # Проверка доступности для класса
        if self._class:
            class_code = self._class.lower().replace(' ', '_')
            if language.is_learnable_by_class(class_code):
                return True
        
        return False