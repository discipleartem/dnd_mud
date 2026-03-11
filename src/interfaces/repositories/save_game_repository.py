"""Интерфейс репозитория сохранений игр.

Следует Clean Architecture - Use Case зависит от абстракции,
а конкретная реализация может быть любой (файлы, база данных, API).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class SaveGame:
    """Сохранение игры.

    Представляет одно сохранение с метаданными.
    """

    def __init__(
        self,
        save_id: str,
        character_name: str,
        character_level: int,
        character_class: str,
        save_time: datetime,
        slot_number: int,
        game_version: str = "1.0.0",
        playtime_minutes: int = 0,
        location: str = "Начало пути",
    ) -> None:
        """Инициализация сохранения.

        Args:
            save_id: Уникальный идентификатор сохранения
            character_name: Имя персонажа
            character_level: Уровень персонажа
            character_class: Класс персонажа
            save_time: Время сохранения
            slot_number: Номер слота сохранения
            game_version: Версия игры
            playtime_minutes: Время игры в минутах
            location: Текущая локация
        """
        self.save_id = save_id
        self.character_name = character_name
        self.character_level = character_level
        self.character_class = character_class
        self.save_time = save_time
        self.slot_number = slot_number
        self.game_version = game_version
        self.playtime_minutes = playtime_minutes
        self.location = location

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать в словарь.

        Returns:
            Словарь с данными сохранения
        """
        return {
            "save_id": self.save_id,
            "character_name": self.character_name,
            "character_level": self.character_level,
            "character_class": self.character_class,
            "save_time": self.save_time.isoformat(),
            "slot_number": self.slot_number,
            "game_version": self.game_version,
            "playtime_minutes": self.playtime_minutes,
            "location": self.location,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SaveGame":
        """Создать из словаря.

        Args:
            data: Словарь с данными сохранения

        Returns:
            Объект SaveGame
        """
        save_time = datetime.fromisoformat(data["save_time"])
        return cls(
            save_id=data["save_id"],
            character_name=data["character_name"],
            character_level=data["character_level"],
            character_class=data["character_class"],
            save_time=save_time,
            slot_number=data["slot_number"],
            game_version=data.get("game_version", "1.0.0"),
            playtime_minutes=data.get("playtime_minutes", 0),
            location=data.get("location", "Начало пути"),
        )


class SaveGameRepository(ABC):
    """Интерфейс репозитория сохранений игр.

    Следует Clean Architecture - определяет контракт для работы
    с сохранениями без привязки к конкретному хранилищу.
    """

    @abstractmethod
    def save(self, save_game: SaveGame, game_data: dict[str, Any]) -> SaveGame:
        """Сохранить игру.

        Args:
            save_game: Метаданные сохранения
            game_data: Полные данные игры для сохранения

        Returns:
            Сохранённая игра с ID

        Raises:
            RepositoryError: Ошибка сохранения
        """
        pass

    @abstractmethod
    def load(self, save_id: str) -> dict[str, Any] | None:
        """Загрузить игру.

        Args:
            save_id: ID сохранения

        Returns:
            Данные игры или None если не найдено

        Raises:
            RepositoryError: Ошибка загрузки
        """
        pass

    @abstractmethod
    def find_by_id(self, save_id: str) -> SaveGame | None:
        """Найти сохранение по ID.

        Args:
            save_id: ID сохранения

        Returns:
            Сохранение или None если не найдено

        Raises:
            RepositoryError: Ошибка поиска
        """
        pass

    @abstractmethod
    def find_by_slot(self, slot_number: int) -> SaveGame | None:
        """Найти сохранение по номеру слота.

        Args:
            slot_number: Номер слота сохранения

        Returns:
            Сохранение или None если не найдено

        Raises:
            RepositoryError: Ошибка поиска
        """
        pass

    @abstractmethod
    def find_all(self) -> list[SaveGame]:
        """Получить все сохранения.

        Returns:
            Список всех сохранений

        Raises:
            RepositoryError: Ошибка получения
        """
        pass

    @abstractmethod
    def delete(self, save_id: str) -> bool:
        """Удалить сохранение.

        Args:
            save_id: ID сохранения

        Returns:
            True если удалено успешно

        Raises:
            RepositoryError: Ошибка удаления
        """
        pass

    @abstractmethod
    def validate_save_format(self, game_data: dict[str, Any]) -> bool:
        """Валидировать формат сохранения.

        Args:
            game_data: Данные игры для валидации

        Returns:
            True если формат корректен
        """
        pass


class RepositoryError(Exception):
    """Ошибка репозитория."""

    pass
