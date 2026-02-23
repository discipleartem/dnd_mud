"""
Сервис для централизованной работы с языками в D&D MUD.

Реализует паттерн Service Repository для унификации доступа к данным языков
и их локализации. Использует существующий i18n менеджер.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

# Импорт локализации
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from i18n import t


@dataclass
class LanguageMechanics:
    """Игровые механики языка."""
    script: str = ""
    is_default: bool = False
    learnable_by_all: bool = False
    learnable_by: List[str] = field(default_factory=list)
    race_bonus: List[str] = field(default_factory=list)
    learnable_by_special: List[str] = field(default_factory=list)
    magic_language: bool = False
    secret_language: bool = False
    evil_alignment: bool = False
    good_alignment: bool = False
    lawful_evil_alignment: bool = False


@dataclass
class Language:
    """Язык в D&D."""
    code: str
    type: str
    difficulty: str
    localization_keys: Dict[str, str] = field(default_factory=dict)
    mechanics: LanguageMechanics = field(default_factory=LanguageMechanics)
    fallback_data: Dict[str, str] = field(default_factory=dict)
    
    def get_name(self) -> str:
        """Получить локализованное название языка."""
        if self.localization_keys.get('name'):
            return t(self.localization_keys['name'])
        return self.fallback_data.get('name', self.code)
    
    def get_description(self) -> str:
        """Получить локализованное описание языка."""
        if self.localization_keys.get('description'):
            return t(self.localization_keys['description'])
        return self.fallback_data.get('description', '')
    
    def get_speakers(self) -> str:
        """Получить локализованный список носителей языка."""
        if self.localization_keys.get('speakers'):
            return t(self.localization_keys['speakers'])
        return self.fallback_data.get('speakers', '')
    
    def get_type_name(self) -> str:
        """Получить локализованное название типа языка."""
        return t(f'language.types.{self.type}')
    
    def get_difficulty_name(self) -> str:
        """Получить локализованное название сложности языка."""
        return t(f'language.difficulties.{self.difficulty}')
    
    def is_available_for_race(self, race_code: str) -> bool:
        """Проверить доступность языка для расы."""
        if self.mechanics.learnable_by_all:
            return True
        if race_code in self.mechanics.learnable_by:
            return True
        if race_code in self.mechanics.race_bonus:
            return True
        return False
    
    def is_available_for_class(self, class_code: str) -> bool:
        """Проверить доступность языка для класса."""
        return class_code in self.mechanics.learnable_by_special


class LanguageService:
    """Централизованный сервис для работы с языками.
    
    Реализует паттерн Service для унификации доступа к данным языков
    и их локализации.
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        """Инициализация сервиса.
        
        Args:
            data_path: Путь к файлу с данными языков
        """
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent / "data" / "languages.yaml"
        self.data_path = data_path
        self._languages: Optional[Dict[str, Language]] = None
        self._metadata: Optional[Dict[str, Any]] = None
    
    def _load_data(self) -> None:
        """Загрузить данные из YAML файла."""
        if self._languages is not None:
            return
            
        with open(self.data_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        # Загружаем метаданные
        self._metadata = data.get('language_metadata', {})
        
        # Загружаем языки
        self._languages = {}
        for lang_code, lang_data in data.get('languages', {}).items():
            # Загружаем механики
            mechanics_data = lang_data.get('mechanics', {})
            mechanics = LanguageMechanics(**mechanics_data)
            
            self._languages[lang_code] = Language(
                code=lang_data['code'],
                type=lang_data['type'],
                difficulty=lang_data['difficulty'],
                localization_keys=lang_data.get('localization_keys', {}),
                mechanics=mechanics,
                fallback_data=lang_data.get('fallback_data', {})
            )
    
    def get_all_languages(self) -> Dict[str, Language]:
        """Получить все языки."""
        self._load_data()
        return self._languages.copy()
    
    def get_language_by_code(self, code: str) -> Optional[Language]:
        """Получить язык по коду."""
        self._load_data()
        return self._languages.get(code)
    
    def get_languages_by_type(self, language_type: str) -> List[Language]:
        """Получить языки по типу."""
        self._load_data()
        return [
            lang for lang in self._languages.values()
            if lang.type == language_type
        ]
    
    def get_languages_by_difficulty(self, difficulty: str) -> List[Language]:
        """Получить языки по сложности."""
        self._load_data()
        return [
            lang for lang in self._languages.values()
            if lang.difficulty == difficulty
        ]
    
    def get_available_languages_for_race(self, race_code: str) -> List[Language]:
        """Получить доступные языки для расы."""
        self._load_data()
        return [
            lang for lang in self._languages.values()
            if lang.is_available_for_race(race_code)
        ]
    
    def get_default_language(self) -> Optional[Language]:
        """Получить язык по умолчанию."""
        self._load_data()
        for lang in self._languages.values():
            if lang.mechanics.is_default:
                return lang
        return None
    
    def get_language_types(self) -> Dict[str, str]:
        """Получить типы языков с локализованными названиями."""
        self._load_data()
        types = {}
        for type_code, type_name in self._metadata.get('types', {}).items():
            types[type_code] = t(f'language.types.{type_code}')
        return types
    
    def get_language_difficulties(self) -> Dict[str, str]:
        """Получить сложности языков с локализованными названиями."""
        self._load_data()
        difficulties = {}
        for diff_code, diff_value in self._metadata.get('difficulties', {}).items():
            difficulties[diff_code] = t(f'language.difficulties.{diff_code}')
        return difficulties
    
    def get_language_names_list(self) -> List[str]:
        """Получить список локализованных названий всех языков."""
        self._load_data()
        return [lang.get_name() for lang in self._languages.values()]
    
    def format_languages_list(self, languages: List[Language]) -> str:
        """Форматировать список языков для отображения."""
        if not languages:
            return "Нет доступных языков"
        
        formatted = []
        for lang in languages:
            name = lang.get_name()
            difficulty = lang.get_difficulty_name()
            formatted.append(f"{name} ({difficulty})")
        
        return ", ".join(formatted)


# Глобальный экземпляр сервиса (паттерн Singleton)
_language_service: Optional[LanguageService] = None


def get_language_service() -> LanguageService:
    """Получить глобальный экземпляр сервиса языков."""
    global _language_service
    if _language_service is None:
        _language_service = LanguageService()
    return _language_service
