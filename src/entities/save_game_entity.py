"""Сущность сохранения игры.

Следует Clean Architecture - бизнес-сущность в слое Entities.
Определяет структуру и валидацию сохранений игр.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SaveGameEntity:
    """Сущность сохранения игры.

    Определяет структуру сохранения с валидацией.
    """

    save_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    character_name: str = ""
    character_level: int = 1
    character_class: str = ""
    save_time: datetime = field(default_factory=datetime.now)
    slot_number: int = 1
    game_version: str = "1.0.0"
    playtime_minutes: int = 0
    location: str = "Начало пути"
    character_data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Пост-инициализация с валидацией."""
        self._validate_save_game()

    def _validate_save_game(self) -> None:
        """Валидировать сохранение.

        Raises:
            ValueError: Если сохранение невалидно
        """
        if not self.character_name.strip():
            raise ValueError("Имя персонажа не может быть пустым")

        if self.character_level < 1 or self.character_level > 20:
            raise ValueError("Уровень персонажа должен быть от 1 до 20")

        if not self.character_class.strip():
            raise ValueError("Класс персонажа не может быть пустым")

        if self.slot_number < 1 or self.slot_number > 10:
            raise ValueError("Номер слота должен быть от 1 до 10")

        if self.playtime_minutes < 0:
            raise ValueError("Время игры не может быть отрицательным")

    def update_character_info(
        self, name: str, level: int, character_class: str
    ) -> None:
        """Обновить информацию о персонаже.

        Args:
            name: Новое имя персонажа
            level: Новый уровень
            character_class: Новый класс
        """
        self.character_name = name
        self.character_level = level
        self.character_class = character_class
        self._validate_save_game()

    def update_playtime(self, additional_minutes: int) -> None:
        """Обновить время игры.

        Args:
            additional_minutes: Дополнительное время в минутах
        """
        if additional_minutes < 0:
            raise ValueError(
                "Дополнительное время не может быть отрицательным"
            )

        self.playtime_minutes += additional_minutes

    def update_location(self, new_location: str) -> None:
        """Обновить локацию.

        Args:
            new_location: Новая локация
        """
        if not new_location.strip():
            raise ValueError("Локация не может быть пустой")

        self.location = new_location

    def set_character_data(self, data: dict[str, Any]) -> None:
        """Установить данные персонажа.

        Args:
            data: Данные персонажа
        """
        if not isinstance(data, dict):
            raise ValueError("Данные персонажа должны быть словарем")

        self.character_data = data.copy()

    def get_character_data(self) -> dict[str, Any]:
        """Получить данные персонажа.

        Returns:
            Копия данных персонажа
        """
        return self.character_data.copy()

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
            "character_data": self.character_data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SaveGameEntity":
        """Создать из словаря.

        Args:
            data: Словарь с данными сохранения

        Returns:
            Объект SaveGameEntity
        """
        save_time = datetime.fromisoformat(data["save_time"])

        return cls(
            save_id=data.get("save_id", str(uuid.uuid4())),
            character_name=data.get("character_name", ""),
            character_level=data.get("character_level", 1),
            character_class=data.get("character_class", ""),
            save_time=save_time,
            slot_number=data.get("slot_number", 1),
            game_version=data.get("game_version", "1.0.0"),
            playtime_minutes=data.get("playtime_minutes", 0),
            location=data.get("location", "Начало пути"),
            character_data=data.get("character_data", {}),
        )

    def get_display_info(self) -> dict[str, str]:
        """Получить информацию для отображения.

        Returns:
            Словарь с отображаемой информацией
        """
        return {
            "save_id": self.save_id,
            "character_name": self.character_name,
            "character_level": str(self.character_level),
            "character_class": self.character_class,
            "save_time": self.save_time.strftime("%Y-%m-%d %H:%M"),
            "slot_number": str(self.slot_number),
            "playtime_hours": f"{self.playtime_minutes // 60}ч {self.playtime_minutes % 60}м",
            "location": self.location,
        }
