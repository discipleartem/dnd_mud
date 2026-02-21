"""
Репозитории для доступа к данным D&D.

Простые и эффективные загрузчики данных из YAML файлов.
"""

import yaml
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from src.models.data import RaceData, ClassData


class DataRepository:
    """Базовый репозиторий для работы с YAML данными."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
    
    def _load_yaml(self, filename: str) -> Dict:
        """Загрузить YAML файл."""
        try:
            with open(self.data_dir / filename, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"❌ Файл {filename} не найден")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Ошибка чтения YAML {filename}: {e}")
            return {}


class RaceRepository(DataRepository):
    """Репозиторий рас."""
    
    def __init__(self):
        super().__init__()
        self._races_data = self._load_races()
    
    def _load_races(self) -> Dict[str, RaceData]:
        """Загрузить данные рас."""
        raw_data = self._load_yaml("races.yaml")
        races = {}
        
        for race_id, race_info in raw_data.get("races", {}).items():
            races[race_id] = RaceData(
                id=race_id,
                name=race_info.get("name", race_id),
                description=race_info.get("description", ""),
                ability_bonuses=race_info.get("ability_bonuses", {}),
                ability_bonuses_description=race_info.get("ability_bonuses_description", ""),
                size=race_info.get("size", "MEDIUM"),
                speed=race_info.get("speed", 30),
                age=race_info.get("age", {}),
                languages=race_info.get("languages", []),
                features=race_info.get("features", []),
                subraces=race_info.get("subraces", {})
            )
        
        return races
    
    def get_race_choices(self) -> List[Tuple[str, str]]:
        """Получить список рас для выбора."""
        return [
            (race.id, race.name) 
            for race in self._races_data.values()
        ]
    
    def get_race_details(self, race_id: str) -> Optional[Dict]:
        """Получить подробную информацию о расе."""
        race = self._races_data.get(race_id)
        if not race:
            return None
        
        return {
            "name": race.name,
            "description": race.description,
            "ability_bonuses": race.ability_bonuses,
            "ability_bonuses_description": race.ability_bonuses_description,
            "size": race.size,
            "speed": race.speed,
            "age": race.age,
            "languages": race.languages,
            "features": race.features
        }
    
    def get_subrace_choices(self, race_id: str) -> List[Tuple[str, str]]:
        """Получить список подрас для выбора."""
        race = self._races_data.get(race_id)
        if not race or not race.subraces:
            return []
        
        return [
            (subrace_id, subrace_data.get("name", subrace_id))
            for subrace_id, subrace_data in race.subraces.items()
        ]
    
    def get_subrace_details(self, race_id: str, subrace_id: str) -> Optional[Dict]:
        """Получить подробную информацию о подрасе."""
        race = self._races_data.get(race_id)
        if not race or not race.subraces:
            return None
        
        subrace = race.subraces.get(subrace_id)
        if not subrace:
            return None
        
        return {
            "name": subrace.get("name", subrace_id),
            "description": subrace.get("description", ""),
            "ability_bonuses": subrace.get("ability_bonuses", {}),
            "ability_bonuses_description": subrace.get("ability_bonuses_description", ""),
            "features": subrace.get("features", [])
        }


class SizeRepository(DataRepository):
    """Репозиторий размеров."""
    
    def __init__(self):
        super().__init__()
        self._size_values = self._load_sizes()
    
    def _load_sizes(self) -> Dict[str, str]:
        """Загрузить названия размеров."""
        raw_data = self._load_yaml("sizes.yaml")
        return raw_data.get("size_values", {})
    
    def get_size_name(self, size_key: str) -> str:
        """Получить человекочитаемое название размера."""
        return self._size_values.get(size_key, size_key)


class ClassRepository(DataRepository):
    """Репозиторий классов."""
    
    def __init__(self):
        super().__init__()
        self._classes_data = self._load_classes()
    
    def _load_classes(self) -> Dict[str, ClassData]:
        """Загрузить данные классов."""
        raw_data = self._load_yaml("classes.yaml")
        classes = {}
        
        for class_id, class_info in raw_data.get("classes", {}).items():
            classes[class_id] = ClassData(
                id=class_id,
                name=class_info.get("name", class_id),
                description=class_info.get("description", ""),
                hit_dice=class_info.get("hit_dice", 8),
                prime_abilities=class_info.get("prime_abilities", []),
                saving_throws=class_info.get("saving_throws", []),
                skill_choices=class_info.get("skill_choices", []),
                equipment=class_info.get("equipment", {}),
                features=class_info.get("features", []),
                subclasses=class_info.get("subclasses", [])
            )
        
        return classes
    
    def get_class_choices(self) -> List[Tuple[str, str]]:
        """Получить список классов для выбора."""
        return [
            (cls.id, cls.name) 
            for cls in self._classes_data.values()
        ]
    
    def get_class_details(self, class_id: str) -> Optional[Dict]:
        """Получить подробную информацию о классе."""
        cls = self._classes_data.get(class_id)
        if not cls:
            return None
        
        return {
            "name": cls.name,
            "description": cls.description,
            "hit_dice": cls.hit_dice,
            "prime_abilities": cls.prime_abilities,
            "saving_throws": cls.saving_throws,
            "skill_choices": cls.skill_choices,
            "equipment": cls.equipment,
            "features": cls.features,
            "subclasses": cls.subclasses
        }
