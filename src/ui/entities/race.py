from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

from .character import Size

# Импорт локализации и языкового сервиса
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from i18n import t
from src.services.language_service import get_language_service


@dataclass
class Feature:
    """Черта расы или подрасы."""
    name: str
    description: str
    mechanics: Dict[str, Any]


@dataclass
class SubRace:
    """Подраса."""
    name: str
    description: str
    ability_bonuses: Dict[str, int] = field(default_factory=dict)
    ability_bonuses_description: str = ""
    languages: List[str] = field(default_factory=list)
    features: List[Feature] = field(default_factory=list)
    inherit_base_abilities: bool = True  # Наследовать бонусы базовой расы


@dataclass
class Race:
    """Раса персонажа."""
    name: str
    description: str
    ability_bonuses: Dict[str, int] = field(default_factory=dict)
    ability_bonuses_description: str = ""
    size: Size = Size.MEDIUM
    speed: int = 30
    age: Dict[str, int] = field(default_factory=dict)
    languages: List[str] = field(default_factory=list)
    features: List[Feature] = field(default_factory=list)
    subraces: Dict[str, SubRace] = field(default_factory=dict)
    allow_base_race_choice: bool = False  # Можно ли выбрать базовую расу
    
    @staticmethod
    def get_all_races() -> Dict[str, 'Race']:
        """Получить все расы."""
        loader = RaceLoader()
        return loader.load_races()
    
    def get_languages_display(self) -> str:
        """Получить локализованный список языков."""
        language_service = get_language_service()
        
        if not self.languages:
            return t('errors.no_languages')
        
        language_names = []
        for lang_code in self.languages:
            language = language_service.get_language_by_code(lang_code)
            if language:
                language_names.append(language.get_name())
            else:
                language_names.append(lang_code)
        
        return ", ".join(language_names)
    
    def get_effective_ability_bonuses(self, subrace: Optional['SubRace'] = None) -> Dict[str, int]:
        """Получить итоговые бонусы к характеристикам с учетом наследования."""
        bonuses = {}
        
        # Добавляем бонусы базовой расы, если подраса не выбрана или она наследует бонусы
        if not subrace or subrace.inherit_base_abilities:
            bonuses.update(self.ability_bonuses)
        
        # Добавляем бонусы подрасы
        if subrace:
            bonuses.update(subrace.ability_bonuses)
        
        return bonuses
    
    @staticmethod
    def get_race_by_name(race_name: str) -> Optional['Race']:
        """Получить расу по названию."""
        races = Race.get_all_races()
        for race in races.values():
            if race.name.lower() == race_name.lower():
                return race
        return None


class RaceLoader:
    """Загрузчик рас из YAML файла."""
    
    def __init__(self, data_path: Path = None):
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent.parent / "data" / "races.yaml"
        self.data_path = data_path
    
    def load_races(self) -> Dict[str, Race]:
        """Загрузить все расы из YAML файла."""
        with open(self.data_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        races = {}
        for race_id, race_data in data.get('races', {}).items():
            # Загружаем черты расы
            features = []
            for feature_data in race_data.get('features', []):
                features.append(Feature(
                    name=feature_data['name'],
                    description=feature_data['description'],
                    mechanics=feature_data['mechanics']
                ))
            
            # Загружаем подрасы
            subraces = {}
            for subrace_id, subrace_data in race_data.get('subraces', {}).items():
                subrace_features = []
                for feature_data in subrace_data.get('features', []):
                    subrace_features.append(Feature(
                        name=feature_data['name'],
                        description=feature_data['description'],
                        mechanics=feature_data['mechanics']
                    ))
                
                subraces[subrace_id] = SubRace(
                    name=subrace_data.get('name', subrace_id),
                    description=subrace_data.get('description', ''),
                    ability_bonuses=subrace_data.get('ability_bonuses', {}),
                    ability_bonuses_description=subrace_data.get('ability_bonuses_description', ''),
                    languages=subrace_data.get('languages', []),
                    features=subrace_features,
                    inherit_base_abilities=subrace_data.get('inherit_base_abilities', True)
                )
            
            # Преобразуем размер с поддержкой всех значений
            size_str = race_data.get('size', 'medium')
            try:
                size = Size(size_str)
            except ValueError:
                print(f"⚠️ Неизвестный размер '{size_str}' для расы {race_id}, используем MEDIUM")
                size = Size.MEDIUM
            
            races[race_id] = Race(
                name=race_data['name'],
                description=race_data['description'],
                ability_bonuses=race_data.get('ability_bonuses', {}),
                ability_bonuses_description=race_data.get('ability_bonuses_description', ''),
                size=size,
                speed=race_data.get('speed', 30),
                age=race_data.get('age', {}),
                languages=race_data.get('languages', []),
                features=features,
                subraces=subraces,
                allow_base_race_choice=race_data.get('allow_base_race_choice', False)
            )
        
        return races
    
    def get_race(self, race_id: str) -> Optional[Race]:
        """Получить расу по ID."""
        races = self.load_races()
        return races.get(race_id)
    
    def get_all_race_names(self) -> List[str]:
        """Получить список всех названий рас."""
        races = self.load_races()
        return [race.name for race in races.values()]

