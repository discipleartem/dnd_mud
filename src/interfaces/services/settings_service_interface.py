"""Интерфейс сервиса настроек.

Следует Clean Architecture - интерфейс в слое Interfaces.
Определяет контракт для работы с настройками.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from src.entities.settings_entity import Setting, GameSettings


class SettingsServiceInterface(ABC):
    """Интерфейс сервиса настроек.
    
    Следует Clean Architecture - определяет контракт
    для работы с настройками игры.
    """
    
    @abstractmethod
    def load_settings(self) -> GameSettings:
        """Загрузить настройки.
        
        Returns:
            Загруженные настройки
        """
        pass
    
    @abstractmethod
    def save_settings(self, settings: GameSettings) -> bool:
        """Сохранить настройки.
        
        Args:
            settings: Настройки для сохранения
            
        Returns:
            True если настройки сохранены
        """
        pass
    
    @abstractmethod
    def get_setting(self, key: str) -> Optional[Setting]:
        """Получить настройку по ключу.
        
        Args:
            key: Ключ настройки
            
        Returns:
            Настройка или None
        """
        pass
    
    @abstractmethod
    def set_setting(self, key: str, value: Any) -> bool:
        """Установить значение настройки.
        
        Args:
            key: Ключ настройки
            value: Новое значение
            
        Returns:
            True если значение установлено
        """
        pass
    
    @abstractmethod
    def get_value(self, key: str, default: Any = None) -> Any:
        """Получить значение настройки.
        
        Args:
            key: Ключ настройки
            default: Значение по умолчанию
            
        Returns:
            Значение настройки или default
        """
        pass
    
    @abstractmethod
    def get_all_settings(self) -> List[Setting]:
        """Получить все настройки.
        
        Returns:
            Список всех настроек
        """
        pass
    
    @abstractmethod
    def reset_to_defaults(self) -> bool:
        """Сбросить настройки к умолчанию.
        
        Returns:
            True если настройки сброшены
        """
        pass
    
    @abstractmethod
    def export_settings(self) -> Optional[Dict[str, Any]]:
        """Экспортировать настройки.
        
        Returns:
            Словарь с настройками или None
        """
        pass
    
    @abstractmethod
    def import_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Импортировать настройки.
        
        Args:
            settings_data: Данные настроек
            
        Returns:
            True если настройки импортированы
        """
        pass
