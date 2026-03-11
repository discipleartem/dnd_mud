"""Интерфейс сервиса переводов.

Следует Clean Architecture - Use Case зависит от абстракции.
Определяет контракт для работы с переводами.
"""

from abc import ABC, abstractmethod
from typing import List


class TranslationService(ABC):
    """Интерфейс сервиса переводов.
    
    Следует Clean Architecture - Use Case работает с интерфейсом,
    а конкретная реализация может быть любой (файлы, база данных, API).
    """
    
    @abstractmethod
    def get_translation(self, language_code: str, key: str, default: str) -> str:
        """Получить перевод.
        
        Args:
            language_code: Код языка
            key: Ключ перевода
            default: Значение по умолчанию
            
        Returns:
            Переведённый текст или default
            
        Raises:
            TranslationError: Ошибка получения перевода
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Получить список поддерживаемых языков.
        
        Returns:
            Список кодов поддерживаемых языков
            
        Raises:
            TranslationError: Ошибка получения языков
        """
        pass
    
    @abstractmethod
    def is_language_supported(self, language_code: str) -> bool:
        """Проверить поддержку языка.
        
        Args:
            language_code: Код языка
            
        Returns:
            True если язык поддерживается
            
        Raises:
            TranslationError: Ошибка проверки
        """
        pass


class TranslationError(Exception):
    """Ошибка сервиса переводов."""
    pass