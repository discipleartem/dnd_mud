# src/systems/character_manager.py
"""
Менеджер персонажей D&D MUD.

Применяемые паттерны:
- Repository (Хранилище) — сохранение и загрузка персонажей
- Factory (Фабрика) — создание персонажей из разных источников
- Singleton (Одиночка) — единый менеджер персонажей

Применяемые принципы:
- Single Responsibility — управление персонажами
- Open/Closed — легко добавлять новые форматы сохранения
- Dependency Inversion — зависимость от абстракций
"""

import json
import yaml
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ...domain.entities.character import Character
from ...domain.services.character_generation import CharacterFactory
from ...domain.entities.race_factory import RaceFactory
from ...domain.entities.class_factory import CharacterClassFactory


@dataclass
class CharacterSaveData:
    """Данные для сохранения персонажа."""
    name: str
    level: int
    race_name: str
    class_name: str
    
    # Характеристики
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    
    # Производные характеристики
    hp_max: int
    hp_current: int
    ac: int
    gold: int
    
    # Метаданные
    created_at: str
    last_updated: str
    version: str = "1.0"
    
    @classmethod
    def from_character(cls, character: Character) -> 'CharacterSaveData':
        """Создает данные сохранения из персонажа."""
        return cls(
            name=character.name,
            level=character.level,
            race_name=character.race.name,
            class_name=character.character_class.name,
            strength=character.strength.value,
            dexterity=character.dexterity.value,
            constitution=character.constitution.value,
            intelligence=character.intelligence.value,
            wisdom=character.wisdom.value,
            charisma=character.charisma.value,
            hp_max=character.hp_max,
            hp_current=character.hp_current,
            ac=character.ac,
            gold=character.gold,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
    
    def to_character(self) -> Character:
        """Создает персонажа из данных сохранения."""
        # Создаем базового персонажа
        character = Character(
            name=self.name,
            level=self.level,
            race=RaceFactory.create_race(self.race_name),
            character_class=CharacterClassFactory.create_class(self.class_name)
        )
        
        # Устанавливаем характеристики
        character.strength.value = self.strength
        character.dexterity.value = self.dexterity
        character.constitution.value = self.constitution
        character.intelligence.value = self.intelligence
        character.wisdom.value = self.wisdom
        character.charisma.value = self.charisma
        
        # Устанавливаем производные характеристики
        character.hp_max = self.hp_max
        character.hp_current = self.hp_current
        character.ac = self.ac
        character.gold = self.gold
        
        return character


class CharacterRepository:
    """Репозиторий для сохранения и загрузки персонажей."""
    
    def __init__(self, save_directory: Optional[Path] = None):
        """Инициализирует репозиторий."""
        if save_directory is None:
            save_directory = Path(__file__).parent.parent.parent / "data" / "saves"
        
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
    
    def save_character(self, character: Character, format: str = "json") -> bool:
        """Сохраняет персонажа в файл."""
        try:
            save_data = CharacterSaveData.from_character(character)
            
            if format.lower() == "json":
                return self._save_json(save_data)
            elif format.lower() == "yaml":
                return self._save_yaml(save_data)
            else:
                raise ValueError(f"Неподдерживаемый формат: {format}")
                
        except Exception as e:
            print(f"Ошибка при сохранении персонажа: {e}")
            return False
    
    def load_character(self, filename: str) -> Optional[Character]:
        """Загружает персонажа из файла."""
        try:
            file_path = self.save_directory / filename
            
            if not file_path.exists():
                print(f"Файл не найден: {file_path}")
                return None
            
            # Определяем формат по расширению
            if filename.endswith('.json'):
                save_data = self._load_json(file_path)
            elif filename.endswith('.yaml') or filename.endswith('.yml'):
                save_data = self._load_yaml(file_path)
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {filename}")
            
            return save_data.to_character()
            
        except Exception as e:
            print(f"Ошибка при загрузке персонажа: {e}")
            return None
    
    def list_characters(self) -> List[str]:
        """Возвращает список сохраненных персонажей."""
        try:
            files = []
            for file_path in self.save_directory.glob("*"):
                if file_path.is_file() and file_path.suffix in ['.json', '.yaml', '.yml']:
                    files.append(file_path.name)
            return sorted(files)
        except Exception as e:
            print(f"Ошибка при получении списка персонажей: {e}")
            return []
    
    def delete_character(self, filename: str) -> bool:
        """Удаляет файл персонажа."""
        try:
            file_path = self.save_directory / filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Ошибка при удалении персонажа: {e}")
            return False
    
    def _save_json(self, save_data: CharacterSaveData) -> bool:
        """Сохраняет в JSON формат."""
        filename = f"{save_data.name}_{save_data.race_name}_{save_data.class_name}.json"
        file_path = self.save_directory / filename
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(asdict(save_data), file, ensure_ascii=False, indent=2)
        
        return True
    
    def _save_yaml(self, save_data: CharacterSaveData) -> bool:
        """Сохраняет в YAML формат."""
        filename = f"{save_data.name}_{save_data.race_name}_{save_data.class_name}.yaml"
        file_path = self.save_directory / filename
        
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(asdict(save_data), file, default_flow_style=False, 
                     allow_unicode=True, indent=2)
        
        return True
    
    def _load_json(self, file_path: Path) -> CharacterSaveData:
        """Загружает из JSON формата."""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return CharacterSaveData(**data)
    
    def _load_yaml(self, file_path: Path) -> CharacterSaveData:
        """Загружает из YAML формата."""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return CharacterSaveData(**data)


class CharacterManager:
    """Менеджер персонажей (Singleton)."""
    
    _instance: Optional['CharacterManager'] = None
    _repository: CharacterRepository
    
    def __new__(cls) -> 'CharacterManager':
        """Создает singleton экземпляр."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._repository = CharacterRepository()
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'CharacterManager':
        """Возвращает экземпляр менеджера."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def save_character(self, character: Character, format: str = "json") -> bool:
        """Сохраняет персонажа."""
        return self._repository.save_character(character, format)
    
    def load_character(self, filename: str) -> Optional[Character]:
        """Загружает персонажа."""
        return self._repository.load_character(filename)
    
    def list_characters(self) -> List[str]:
        """Возвращает список персонажей."""
        return self._repository.list_characters()
    
    def delete_character(self, filename: str) -> bool:
        """Удаляет персонажа."""
        return self._repository.delete_character(filename)
    
    def create_new_character(self, name: str = "Безымянный") -> Character:
        """Создает нового персонажа."""
        return CharacterFactory.create_standard_character(name)
    
    def get_character_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """Возвращает базовую информацию о персонаже без полной загрузки."""
        try:
            file_path = self._repository.save_directory / filename
            if not file_path.exists():
                return None
            
            # Определяем формат
            if filename.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            elif filename.endswith('.yaml') or filename.endswith('.yml'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
            else:
                return None
            
            return {
                'name': data.get('name', 'Unknown'),
                'level': data.get('level', 1),
                'race': data.get('race_name', 'Unknown'),
                'class': data.get('class_name', 'Unknown'),
                'created_at': data.get('created_at', 'Unknown'),
                'filename': filename
            }
            
        except Exception as e:
            print(f"Ошибка при получении информации о персонаже: {e}")
            return None


# Удобные функции для использования
def save_character(character: Character, format: str = "json") -> bool:
    """Сохраняет персонажа."""
    manager = CharacterManager.get_instance()
    return manager.save_character(character, format)


def load_character(filename: str) -> Optional[Character]:
    """Загружает персонажа."""
    manager = CharacterManager.get_instance()
    return manager.load_character(filename)


def list_characters() -> List[str]:
    """Возвращает список персонажей."""
    manager = CharacterManager.get_instance()
    return manager.list_characters()


def get_character_info(filename: str) -> Optional[Dict[str, Any]]:
    """Возвращает информацию о персонаже."""
    manager = CharacterManager.get_instance()
    return manager.get_character_info(filename)


# Пример использования
if __name__ == "__main__":
    # Создаем тестового персонажа
    character = CharacterFactory.create_standard_character("Тестовый персонаж")
    
    # Сохраняем
    success = save_character(character)
    print(f"Сохранение: {'Успешно' if success else 'Ошибка'}")
    
    # Получаем список
    characters = list_characters()
    print(f"Сохраненные персонажи: {characters}")
    
    # Загружаем
    if characters:
        loaded = load_character(characters[0])
        if loaded:
            print(f"Загружен персонаж: {loaded.name}")
        
        # Информация о персонаже
        info = get_character_info(characters[0])
        print(f"Информация: {info}")
