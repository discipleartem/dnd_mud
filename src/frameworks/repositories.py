"""Реализации репозиториев для работы с YAML данными.

Находится в слое Frameworks, так как зависит от конкретной технологии.
"""

import yaml
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from src.interfaces.repositories import RaceRepositoryInterface, ClassRepositoryInterface, CharacterRepositoryInterface
from src.entities.character import Character, CharacterData


class YAMLDataRepository:
    """Базовый репозиторий для работы с YAML данными."""
    
    def __init__(self, data_dir: str = "data") -> None:
        self._data_dir = Path(data_dir)
    
    def _load_yaml(self, filename: str) -> Dict:
        """Загрузить YAML файл."""
        try:
            with open(self._data_dir / filename, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"❌ Файл {filename} не найден")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Ошибка чтения YAML {filename}: {e}")
            return {}


class YAMLRaceRepository(YAMLDataRepository, RaceRepositoryInterface):
    """YAML реализация репозитория рас."""
    
    def __init__(self) -> None:
        super().__init__()
        self._races_data = self._load_races()
    
    def _load_races(self) -> Dict[str, Dict]:
        """Загрузить данные рас."""
        raw_data = self._load_yaml("races.yaml")
        return raw_data.get("races", {})
    
    def get_race_choices(self) -> List[Tuple[str, str]]:
        """Получить список рас для выбора."""
        races = []
        for race_id, race_info in self._races_data.items():
            races.append((race_id, race_info.get("name", race_id)))
        return races
    
    def get_race_details(self, race_id: str) -> Optional[Dict]:
        """Получить информацию о расе."""
        race = self._races_data.get(race_id)
        if not race:
            return None
        
        return {
            "name": race.get("name", race_id),
            "description": race.get("description", ""),
            "ability_bonuses": race.get("ability_bonuses", {}),
            "ability_bonuses_description": race.get("ability_bonuses_description", ""),
            "size": race.get("size", "MEDIUM"),
            "speed": race.get("speed", 30),
            "age": race.get("age", {}),
            "languages": race.get("languages", []),
            "features": race.get("features", []),
            "subraces": race.get("subraces", {})
        }
    
    def get_subrace_choices(self, race_id: str) -> List[Tuple[str, str]]:
        """Получить подрасы."""
        race = self._races_data.get(race_id)
        if not race or not race.get("subraces"):
            return []
        
        subraces = []
        for subrace_id, subrace_data in race["subraces"].items():
            subraces.append((subrace_id, subrace_data.get("name", subrace_id)))
        return subraces
    
    def get_subrace_details(self, race_id: str, subrace_id: str) -> Optional[Dict]:
        """Получить информацию о подрасе."""
        race = self._races_data.get(race_id)
        if not race or not race.get("subraces"):
            return None
        
        subrace = race["subraces"].get(subrace_id)
        if not subrace:
            return None
        
        return {
            "name": subrace.get("name", subrace_id),
            "description": subrace.get("description", ""),
            "ability_bonuses": subrace.get("ability_bonuses", {}),
            "ability_bonuses_description": subrace.get("ability_bonuses_description", ""),
            "features": subrace.get("features", [])
        }


class YAMLClassRepository(YAMLDataRepository, ClassRepositoryInterface):
    """YAML реализация репозитория классов."""
    
    def __init__(self) -> None:
        super().__init__()
        self._classes_data = self._load_classes()
    
    def _load_classes(self) -> Dict[str, Dict]:
        """Загрузить данные классов."""
        raw_data = self._load_yaml("classes.yaml")
        return raw_data.get("classes", {})
    
    def get_class_choices(self) -> List[Tuple[str, str]]:
        """Получить список классов для выбора."""
        classes = []
        for class_id, class_info in self._classes_data.items():
            classes.append((class_id, class_info.get("name", class_id)))
        return classes
    
    def get_class_details(self, class_id: str) -> Optional[Dict]:
        """Получить информацию о классе."""
        cls = self._classes_data.get(class_id)
        if not cls:
            return None
        
        return {
            "name": cls.get("name", class_id),
            "description": cls.get("description", ""),
            "hit_dice": cls.get("hit_dice", 8),
            "prime_abilities": cls.get("prime_abilities", []),
            "saving_throws": cls.get("saving_throws", []),
            "skill_choices": cls.get("skill_choices", []),
            "equipment": cls.get("equipment", {}),
            "features": cls.get("features", []),
            "subclasses": cls.get("subclasses", [])
        }


class InMemoryCharacterRepository(CharacterRepositoryInterface):
    """In-memory реализация репозитория персонажей."""
    
    def __init__(self) -> None:
        self._characters: Dict[int, Character] = {}
        self._next_id = 1
    
    def save(self, character: Character) -> Character:
        """Сохранить персонажа."""
        if not hasattr(character.data, 'id') or character.data.id is None:
            # Создаем копию данных с новым ID
            new_data = CharacterData(
                id=self._next_id,
                name=character.data.name,
                race=character.data.race,
                character_class=character.data.character_class,
                level=character.data.level,
                strength=character.data.strength,
                dexterity=character.data.dexterity,
                constitution=character.data.constitution,
                intelligence=character.data.intelligence,
                wisdom=character.data.wisdom,
                charisma=character.data.charisma,
                size=character.data.size,
                speed=character.data.speed,
                languages=character.data.languages.copy(),
                skills=character.data.skills.copy(),
                features=character.data.features.copy(),
                hit_points=character.data.hit_points,
                armor_class=character.data.armor_class,
                proficiency_bonus=character.data.proficiency_bonus
            )
            new_character = Character(new_data)
            self._characters[self._next_id] = new_character
            self._next_id += 1
            return new_character
        else:
            # Обновление существующего персонажа
            self._characters[character.data.id] = character
            return character
    
    def find_by_id(self, character_id: int) -> Optional[Character]:
        """Найти персонажа по ID."""
        return self._characters.get(character_id)
    
    def find_all(self) -> List[Character]:
        """Получить всех персонажей."""
        return list(self._characters.values())
    
    def delete(self, character_id: int) -> bool:
        """Удалить персонажа."""
        if character_id in self._characters:
            del self._characters[character_id]
            return True
        return False