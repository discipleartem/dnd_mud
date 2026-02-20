"""Интерфейс локализации для доменного слоя."""

from abc import ABC, abstractmethod
from typing import Optional


class LocalizationInterface(ABC):
    """Абстрактный интерфейс для локализации."""

    @abstractmethod
    def get_text(self, key: str, default: Optional[str] = None, **kwargs: str) -> str:
        """Получает локализованный текст по ключу."""
        # Простая реализация - возвращаем ключ с префиксом
        return f"[{key}]" if default is None else default

    @abstractmethod
    def get_language(self) -> str:
        """Получает текущий язык."""
        pass

    @abstractmethod
    def set_language(self, language: str) -> None:
        """Устанавливает язык."""
        pass


# Глобальный экземпляр для использования в домене
localization: Optional[LocalizationInterface] = None


def set_localization_service(service: LocalizationInterface) -> None:
    """Устанавливает сервис локализации для домена."""
    global localization
    localization = service


def get_text(key: str, default: Optional[str] = None, **kwargs: str) -> str:
    """Получает локализованный текст через глобальный сервис."""
    if localization is None:
        return default or key
    return localization.get_text(key, default, **kwargs)
