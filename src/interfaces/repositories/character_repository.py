"""Интерфейс репозитория персонажей.

Следует Clean Architecture - Use Case зависит от абстракции,
а конкретная реализация может быть любой (база данных, файлы, API).
"""

from abc import ABC, abstractmethod

from src.entities.welcome_screen import WelcomeScreen


class CharacterRepository(ABC):
    """Интерфейс репозитория персонажей.

    Следует Clean Architecture - определяет контракт для работы
    с данными персонажей без привязки к конкретному хранилищу.
    """

    @abstractmethod
    def save(self, character: WelcomeScreen) -> WelcomeScreen:
        """Сохранить персонажа.

        Args:
            character: Сущность персонажа

        Returns:
            Сохранённый персонаж с ID

        Raises:
            RepositoryError: Ошибка сохранения
        """
        pass

    @abstractmethod
    def find_by_id(self, character_id: int) -> WelcomeScreen | None:
        """Найти персонажа по ID.

        Args:
            character_id: ID персонажа

        Returns:
            Персонаж или None если не найден

        Raises:
            RepositoryError: Ошибка поиска
        """
        pass

    @abstractmethod
    def find_all(self) -> list[WelcomeScreen]:
        """Получить всех персонажей.

        Returns:
            Список всех персонажей

        Raises:
            RepositoryError: Ошибка получения
        """
        pass

    @abstractmethod
    def delete(self, character_id: int) -> bool:
        """Удалить персонажа.

        Args:
            character_id: ID персонажа

        Returns:
            True если удалён успешно

        Raises:
            RepositoryError: Ошибка удаления
        """
        pass


class RepositoryError(Exception):
    """Ошибка репозитория."""

    pass
