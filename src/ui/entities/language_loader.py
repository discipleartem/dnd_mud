"""
Загрузчик языков из YAML файла с поддержкой локализации.
Оптимизирован для работы с character.py и race.py.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

# Импорт локализации
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from i18n import t


@dataclass
class Language:
    """Класс языка с поддержкой локализации и игровых механик."""
    code: str
    type: str
    difficulty: str
    localization_keys: Dict[str, str]
    mechanics: Dict[str, Any]
    fallback_data: Dict[str, str]
    
    def get_localized_name(self) -> str:
        """Получить локализованное название языка."""
        try:
            return t(self.localization_keys['name'])
        except KeyError:
            return self.fallback_data.get('name', self.code)
    
    def get_localized_description(self) -> str:
        """Получить локализованное описание языка."""
        try:
            return t(self.localization_keys['description'])
        except KeyError:
            return self.fallback_data.get('description', '')
    
    def get_localized_speakers(self) -> str:
        """Получить локализованный список носителей языка."""
        try:
            return t(self.localization_keys['speakers'])
        except KeyError:
            return self.fallback_data.get('speakers', '')
    
    def is_learnable_by_race(self, race_code: str) -> bool:
        """Проверить, может ли раса изучить этот язык."""
        learnable_by = self.mechanics.get('learnable_by', [])
        race_bonus = self.mechanics.get('race_bonus', [])
        
        return race_code in learnable_by or race_code in race_bonus
    
    def is_learnable_by_class(self, class_code: str) -> bool:
        """Проверить, может ли класс изучить этот язык."""
        learnable_by_special = self.mechanics.get('learnable_by_special', [])
        return class_code in learnable_by_special
    
    def is_magic_language(self) -> bool:
        """Проверить, является ли язык магическим."""
        return self.mechanics.get('magic_language', False)
    
    def is_secret_language(self) -> bool:
        """Проверить, является ли язык секретным."""
        return self.mechanics.get('secret_language', False)
    
    def get_difficulty_level(self) -> int:
        """Получить числовой уровень сложности."""
        difficulty_map = {
            'easy': 1,
            'normal': 2,
            'hard': 3,
            'very_hard': 4
        }
        return difficulty_map.get(self.difficulty, 2)
    
    def __str__(self) -> str:
        """Строковое представление с локализацией."""
        return self.get_localized_name()


class LanguageLoader:
    """Загрузчик языков из YAML файла."""
    
    def __init__(self, data_path: Path = None):
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent.parent / "data" / "languages.yaml"
        self.data_path = data_path
        self._languages_cache: Optional[Dict[str, Language]] = None
    
    def load_languages(self) -> Dict[str, Language]:
        """Загрузить все языки из YAML файла."""
        if self._languages_cache is not None:
            return self._languages_cache
        
        with open(self.data_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        languages = {}
        for lang_code, lang_data in data.get('languages', {}).items():
            languages[lang_code] = Language(
                code=lang_data.get('code', lang_code),
                type=lang_data.get('type', 'standard'),
                difficulty=lang_data.get('difficulty', 'normal'),
                localization_keys=lang_data.get('localization_keys', {}),
                mechanics=lang_data.get('mechanics', {}),
                fallback_data=lang_data.get('fallback_data', {})
            )
        
        self._languages_cache = languages
        return languages
    
    def get_language(self, lang_code: str) -> Optional[Language]:
        """Получить язык по коду."""
        languages = self.load_languages()
        return languages.get(lang_code)
    
    def get_languages_by_type(self, lang_type: str) -> List[Language]:
        """Получить языки по типу."""
        languages = self.load_languages()
        return [lang for lang in languages.values() if lang.type == lang_type]
    
    def get_learnable_languages_for_race(self, race_code: str) -> List[Language]:
        """Получить языки, доступные для изучения расой."""
        languages = self.load_languages()
        return [
            lang for lang in languages.values()
            if lang.is_learnable_by_race(race_code)
        ]
    
    def get_learnable_languages_for_class(self, class_code: str) -> List[Language]:
        """Получить языки, доступные для изучения классом."""
        languages = self.load_languages()
        return [
            lang for lang in languages.values()
            if lang.is_learnable_by_class(class_code)
        ]
    
    def get_magic_languages(self) -> List[Language]:
        """Получить все магические языки."""
        languages = self.load_languages()
        return [lang for lang in languages.values() if lang.is_magic_language()]
    
    def get_secret_languages(self) -> List[Language]:
        """Получить все секретные языки."""
        languages = self.load_languages()
        return [lang for lang in languages.values() if lang.is_secret_language()]
    
    def get_default_language(self) -> Language:
        """Получить язык по умолчанию (обычно Common)."""
        languages = self.load_languages()
        for lang in languages.values():
            if lang.mechanics.get('is_default', False):
                return lang
        
        # Fallback к первому доступному языку
        return next(iter(languages.values()))
    
    def get_all_language_names(self) -> List[str]:
        """Получить список всех локализованных названий языков."""
        languages = self.load_languages()
        return [lang.get_localized_name() for lang in languages.values()]
    
    def clear_cache(self) -> None:
        """Очистить кэш языков."""
        self._languages_cache = None
