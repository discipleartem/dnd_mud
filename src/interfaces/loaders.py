"""Интерфейсы загрузчиков данных.

Определяет абстрактные интерфейсы для загрузки данных из различных источников,
обеспечивая унифицированный доступ к данным.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")


class IDataLoader[T](ABC):
    """Базовый интерфейс загрузчика данных.

    Определяет контракт для загрузки данных из различных источников.
    Следует принципу Open/Closed из SOLID.
    """

    @abstractmethod
    def load(self, source: Any) -> T:
        """Загрузить данные из источника.

        Args:
            source: Источник данных (файл, URL, etc.)

        Returns:
            Загруженные данные

        Raises:
            LoaderError: При ошибке загрузки
        """
        pass


class IYamlLoader(IDataLoader[dict[str, Any]]):
    """Интерфейс загрузчика YAML данных.

    Специализированный интерфейс для работы с YAML файлами.
    """

    @abstractmethod
    def load_from_file(self, file_path: Path) -> dict[str, Any]:
        """Загрузить данные из YAML файла.

        Args:
            file_path: Путь к YAML файлу

        Returns:
            Распарсенные данные

        Raises:
            FileNotFoundError: Если файл не найден
            LoaderError: При ошибке парсинга YAML
        """
        pass

    @abstractmethod
    def load_from_string(self, yaml_string: str) -> dict[str, Any]:
        """Загрузить данные из YAML строки.

        Args:
            yaml_string: YAML строка

        Returns:
            Распарсенные данные

        Raises:
            LoaderError: При ошибке парсинга YAML
        """
        pass


class ICacheableLoader(IDataLoader[T]):
    """Интерфейс загрузчика с кэшированием.

    Расширяет базовый интерфейс возможностью кэширования результатов.
    """

    @abstractmethod
    def clear_cache(self) -> None:
        """Очистить кэш загрузчика."""
        pass

    @abstractmethod
    def is_cached(self, source: Any) -> bool:
        """Проверить наличие данных в кэше.

        Args:
            source: Источник данных

        Returns:
            True если данные в кэше
        """
        pass


class LoaderError(Exception):
    """Базовое исключение загрузчика."""

    def __init__(self, message: str, cause: Exception | None = None):
        """Инициализация исключения.

        Args:
            message: Сообщение об ошибке
            cause: Причина ошибки (опционально)
        """
        super().__init__(message)
        self.cause = cause

    def __str__(self) -> str:
        """Строковое представление с причиной."""
        if self.cause:
            return f"{super().__str__()} (причина: {self.cause})"
        return super().__str__()
