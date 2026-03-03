"""In-memory реализация репозитория персонажей."""

from typing import List, Optional
from src.interfaces.character_repository import CharacterRepository
from src.models.entities.character import Character


class MemoryCharacterRepository(CharacterRepository):
    """In-memory репозиторий персонажей для разработки и тестирования.
    
    Применяемые паттерны:
    - Repository (Хранилище) — инкапсулирует логику доступа к данным
    - Singleton (Одиночка) — глобальное хранилище в памяти
    
    Применяемые принципы:
    - Dependency Inversion — зависит от абстракции, а не от реализации
    - Testability — легко подменяется в тестах
    """
    
    def __init__(self):
        """Инициализировать репозиторий."""
        self._characters: dict[int, Character] = {}
        self._next_id: int = 1
    
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
        return character
    
    def clear(self) -> None:
        """Очистить репозиторий (для тестов)."""
        self._characters.clear()
        self._next_id = 1
