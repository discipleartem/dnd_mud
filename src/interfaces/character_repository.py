"""Интерфейс репозитория персонажей."""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.entities.character import Character


class CharacterRepository(ABC):
    """Интерфейс для работы с данными персонажей."""
    
    @abstractmethod
    def save(self, character: Character) -> Character:
        """Сохранить персонажа."""
        pass
    
    @abstractmethod
    def find_by_id(self, character_id: int) -> Optional[Character]:
        """Найти персонажа по ID."""
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Character]:
        """Найти персонажа по имени."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Character]:
        """Получить всех персонажей."""
        pass
    
    @abstractmethod
    def delete(self, character_id: int) -> bool:
        """Удалить персонажа."""
        pass
    
    @abstractmethod
    def update(self, character: Character) -> Character:
        """Обновить персонажа."""
        pass