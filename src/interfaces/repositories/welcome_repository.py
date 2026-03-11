"""Интерфейс репозитория приветственного экрана.

Следует Clean Architecture - Use Case зависит от абстракции,
а конкретная реализация может быть любой.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from src.entities.welcome_screen import WelcomeScreen


class WelcomeRepository(ABC):
    """Интерфейс репозитория приветственного экрана.
    
    Следует Clean Architecture - определяет контракт для работы
    с данными приветственного экрана.
    """
    
    @abstractmethod
    def save_welcome_config(self, config: Dict[str, Any]) -> bool:
        """Сохранить конфигурацию приветствия.
        
        Args:
            config: Конфигурация приветствия
            
        Returns:
            True если сохранено успешно
            
        Raises:
            RepositoryError: Ошибка сохранения
        """
        pass
    
    @abstractmethod
    def get_welcome_config(self, language: str = "ru") -> Optional[Dict[str, Any]]:
        """Получить конфигурацию приветствия.
        
        Args:
            language: Язык конфигурации
            
        Returns:
            Конфигурация или None
            
        Raises:
            RepositoryError: Ошибка получения
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Получить поддерживаемые языки.
        
        Returns:
            Список кодов языков
            
        Raises:
            RepositoryError: Ошибка получения языков
        """
        pass


class RepositoryError(Exception):
    """Ошибка репозитория."""
    pass
