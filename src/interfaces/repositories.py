"""Интерфейсы репозиториев проекта.

Определяет абстрактные интерфейсы для всех репозиториев данных,
обеспечивая чистую архитектуру и тестируемость.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, TypeVar

T = TypeVar("T")


class IRepository[T](ABC):
    """Базовый интерфейс репозитория.

    Определяет стандартные CRUD операции для всех сущностей.
    Следует принципу Interface Segregation из SOLID.
    """

    @abstractmethod
    def save(self, entity: T) -> T:
        """Сохранить сущность.

        Args:
            entity: Сущность для сохранения

        Returns:
            Сохранённая сущность (возможно с ID)

        Raises:
            RepositoryError: При ошибке сохранения
        """
        pass

    @abstractmethod
    def find_by_id(self, entity_id: str) -> T | None:
        """Найти сущность по ID.

        Args:
            entity_id: Идентификатор сущности

        Returns:
            Сущность или None если не найдена

        Raises:
            RepositoryError: При ошибке поиска
        """
        pass

    @abstractmethod
    def find_all(self) -> list[T]:
        """Получить все сущности.

        Returns:
            Список всех сущностей

        Raises:
            RepositoryError: При ошибке загрузки
        """
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Удалить сущность.

        Args:
            entity_id: Идентификатор сущности

        Returns:
            True если удалена, False если не найдена

        Raises:
            RepositoryError: При ошибке удаления
        """
        pass


class IRaceRepository(IRepository["Race"]):
    """Интерфейс репозитория рас."""

    @abstractmethod
    def find_by_name(self, name: str) -> Optional["Race"]:
        """Найти расу по названию.

        Args:
            name: Название расы

        Returns:
            Раса или None если не найдена
        """
        pass

    @abstractmethod
    def get_all_race_names(self) -> list[str]:
        """Получить список всех названий рас.

        Returns:
            Список названий рас
        """
        pass

    @abstractmethod
    def get_languages_by_race(self, race_name: str) -> list[str]:
        """Получить языки доступные для расы.

        Args:
            race_name: Название расы

        Returns:
            Список кодов языков доступных для расы
        """
        pass

    @abstractmethod
    def get_subraces_by_race(self, race_name: str) -> list[str]:
        """Получить список подрас для расы.

        Args:
            race_name: Название расы

        Returns:
            Список названий подрас
        """
        pass

    @abstractmethod
    def find_subrace_by_name(
        self, race_name: str, subrace_name: str
    ) -> Optional["SubRace"]:
        """Найти подрасу по названию.

        Args:
            race_name: Название основной расы
            subrace_name: Название подрасы

        Returns:
            Подраса или None если не найдена
        """
        pass


class ILanguageRepository(IRepository["Language"]):
    """Интерфейс репозитория языков."""

    @abstractmethod
    def find_by_code(self, code: str) -> Optional["Language"]:
        """Найти язык по коду.

        Args:
            code: Код языка

        Returns:
            Язык или None если не найден
        """
        pass

    @abstractmethod
    def get_languages_by_type(self, language_type: str) -> list["Language"]:
        """Получить языки по типу.

        Args:
            language_type: Тип языка

        Returns:
            Список языков указанного типа
        """
        pass

    @abstractmethod
    def get_available_for_race(self, race_code: str) -> list["Language"]:
        """Получить языки доступные для расы.

        Args:
            race_code: Код расы

        Returns:
            Список доступных языков
        """
        pass


class ICharacterRepository(IRepository["Character"]):
    """Интерфейс репозитория персонажей."""

    @abstractmethod
    def find_by_name(self, name: str) -> Optional["Character"]:
        """Найти персонажа по имени.

        Args:
            name: Имя персонажа

        Returns:
            Персонаж или None если не найден
        """
        pass

    @abstractmethod
    def find_by_race(self, race_name: str) -> list["Character"]:
        """Найти персонажей расы.

        Args:
            race_name: Название расы

        Returns:
            Список персонажей указанной расы
        """
        pass

    @abstractmethod
    def get_by_race(self, race_name: str) -> list["Character"]:
        """Получить персонажей расы.

        Args:
            race_name: Название расы

        Returns:
            Список персонажей указанной расы
        """
        pass


class RepositoryError(Exception):
    """Базовое исключение репозитория."""

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


# Импорты для аннотаций (избегаем циклических зависимостей)
if TYPE_CHECKING:
    # Эти импорты только для аннотаций типов
    from src.domain.entities.character import Character
    from src.domain.entities.language import Language
    from src.domain.entities.race import Race, SubRace
