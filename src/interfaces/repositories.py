"""Интерфейсы репозиториев.

Определяет контракты для доступа к данным без конкретных реализаций.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from src.entities.character import Character


class RaceRepositoryInterface(ABC):
    """Интерфейс репозитория рас."""
    
    @abstractmethod
    def get_race_choices(self) -> List[Tuple[str, str]]:
        """Получить список рас для выбора."""
        pass
    
    @abstractmethod
    def get_race_details(self, race_id: str) -> Optional[Dict]:
        """Получить информацию о расе."""
        pass
    
    @abstractmethod
    def get_subrace_choices(self, race_id: str) -> List[Tuple[str, str]]:
        """Получить подрасы."""
        pass
    
    @abstractmethod
    def get_subrace_details(self, race_id: str, subrace_id: str) -> Optional[Dict]:
        """Получить информацию о подрасе."""
        pass


class ClassRepositoryInterface(ABC):
    """Интерфейс репозитория классов."""
    
    @abstractmethod
    def get_class_choices(self) -> List[Tuple[str, str]]:
        """Получить список классов для выбора."""
        pass
    
    @abstractmethod
    def get_class_details(self, class_id: str) -> Optional[Dict]:
        """Получить информацию о классе."""
        pass


class CharacterRepositoryInterface(ABC):
    """Интерфейс репозитория персонажей."""
    
    @abstractmethod
    def save(self, character: Character) -> Character:
        """Сохранить персонажа."""
        pass
    
    @abstractmethod
    def find_by_id(self, character_id: int) -> Optional[Character]:
        """Найти персонажа по ID."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Character]:
        """Получить всех персонажей."""
        pass
    
    @abstractmethod
    def delete(self, character_id: int) -> bool:
        """Удалить персонажа."""
        pass