"""JSON репозиторий персонажей для сохранения в файл."""

import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from src.interfaces.character_repository import CharacterRepository
from src.models.entities.character import Character


class JsonCharacterRepository(CharacterRepository):
    """JSON репозиторий персонажей с сохранением в файл.
    
    Применяемые паттерны:
    - Repository (Хранилище) — инкапсулирует логику доступа к данным
    - Serializer (Сериализатор) — преобразует объекты в JSON и обратно
    
    Применяемые принципы:
    - Persistence — данные сохраняются между запусками программы
    - File I/O Safety — безопасная работа с файлами
    - Data Integrity — проверка целостности данных
    """
    
    def __init__(self, file_path: str = "data/characters.json"):
        """Инициализировать репозиторий с путем к файлу.
        
        Args:
            file_path: Путь к JSON файлу для сохранения персонажей
        """
        self.file_path = Path(file_path)
        self._characters: dict[int, Character] = {}
        self._next_id: int = 1
        self._ensure_data_directory()
        self._load_characters()
    
    def _ensure_data_directory(self) -> None:
        """Создать директорию для данных если не существует."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_characters(self) -> None:
        """Загрузить персонажей из JSON файла."""
        if not self.file_path.exists():
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверяем, что данные - это словарь
            if not isinstance(data, dict):
                print(f"⚠️ Некорректный формат файла данных: ожидается словарь, получено {type(data)}")
                print("🔄 Создание нового хранилища...")
                self._characters.clear()
                self._next_id = 1
                return
            
            # Загрузка персонажей
            characters_data = data.get('characters', [])
            if not isinstance(characters_data, list):
                print(f"⚠️ Некорректный формат списка персонажей: ожидается список, получено {type(characters_data)}")
                characters_data = []
            
            for char_data in characters_data:
                character = self._deserialize_character(char_data)
                self._characters[character.id] = character
            
            # Установка следующего ID
            max_id = data.get('next_id', 1)
            self._next_id = max_id
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"⚠️ Ошибка загрузки персонажей: {e}")
            print("🔄 Создание нового хранилища...")
            self._characters.clear()
            self._next_id = 1
    
    def _save_characters(self) -> None:
        """Сохранить персонажей в JSON файл."""
        data = {
            'characters': [self._serialize_character(char) for char in self._characters.values()],
            'next_id': self._next_id,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            # Атомарное сохранение через временный файл
            temp_file = self.file_path.with_suffix('.tmp')
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Заменяем основной файл только при успешной записи
            temp_file.replace(self.file_path)
            
        except (OSError, IOError) as e:
            raise RuntimeError(f"Ошибка сохранения персонажей: {e}")
    
    def _serialize_character(self, character: Character) -> dict:
        """Сериализовать персонажа в словарь для JSON.
        
        Args:
            character: Персонаж для сериализации
            
        Returns:
            Словарь с данными персонажа
        """
        return {
            'id': character.id,
            'name': character.name,
            'created_at': character.created_at.isoformat() if character.created_at else None,
            'updated_at': character.updated_at.isoformat() if character.updated_at else None
        }
    
    def _deserialize_character(self, data: dict) -> Character:
        """Десериализовать персонажа из словаря JSON.
        
        Args:
            data: Словарь с данными персонажа
            
        Returns:
            Объект Character
        """
        created_at = None
        updated_at = None
        
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            updated_at = datetime.fromisoformat(data['updated_at'])
        
        return Character(
            id=data['id'],
            name=data['name'],
            created_at=created_at,
            updated_at=updated_at
        )
    
    def save(self, character: Character) -> Character:
        """Сохранить персонажа.
        
        Args:
            character: Персонаж для сохранения
            
        Returns:
            Сохраненный персонаж с присвоенным ID
        """
        if character.is_new:
            # Новый персонаж — присваиваем ID
            character.id = self._next_id
            self._characters[self._next_id] = character
            self._next_id += 1
        else:
            # Существующий персонаж — обновляем
            self._characters[character.id] = character
        
        # Сохраняем в файл
        self._save_characters()
        
        return character
    
    def find_by_id(self, character_id: int) -> Optional[Character]:
        """Найти персонажа по ID.
        
        Args:
            character_id: ID персонажа
            
        Returns:
            Персонаж или None если не найден
        """
        return self._characters.get(character_id)
    
    def find_by_name(self, name: str) -> Optional[Character]:
        """Найти персонажа по имени.
        
        Args:
            name: Имя персонажа
            
        Returns:
            Персонаж или None если не найден
        """
        # Поиск без учета регистра и пробелов
        search_name = name.strip().lower()
        
        for character in self._characters.values():
            if character.name.strip().lower() == search_name:
                return character
        
        return None
    
    def find_all(self) -> List[Character]:
        """Получить всех персонажей.
        
        Returns:
            Список всех персонажей
        """
        return list(self._characters.values())
    
    def delete(self, character_id: int) -> bool:
        """Удалить персонажа.
        
        Args:
            character_id: ID персонажа для удаления
            
        Returns:
            True если удален, иначе False
        """
        if character_id in self._characters:
            del self._characters[character_id]
            self._save_characters()
            return True
        return False
    
    def update(self, character: Character) -> Character:
        """Обновить персонажа.
        
        Args:
            character: Персонаж с обновленными данными
            
        Returns:
            Обновленный персонаж
        """
        if character.id is None:
            raise ValueError("Cannot update character without ID")
        
        self._characters[character.id] = character
        self._save_characters()
        return character
    
    def get_stats(self) -> dict:
        """Получить статистику репозитория.
        
        Returns:
            Словарь со статистикой
        """
        return {
            'total_characters': len(self._characters),
            'next_id': self._next_id,
            'file_path': str(self.file_path),
            'file_exists': self.file_path.exists(),
            'file_size': self.file_path.stat().st_size if self.file_path.exists() else 0
        }
