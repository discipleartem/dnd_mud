"""DTO для сохранений игр.

Следует Clean Architecture - объекты передачи данных между слоями.
Используются для коммуникации между Controllers, Use Cases и Adapters.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SaveGameRequest:
    """Запрос на операцию с сохранением."""

    action: str  # "save", "load", "delete", "list"
    save_id: str | None = None
    slot_number: int | None = None
    character_name: str | None = None
    character_level: int | None = None
    character_class: str | None = None
    character_data: dict[str, Any] | None = None
    location: str | None = None


@dataclass
class SaveGameResponse:
    """Ответ на операцию с сохранением."""

    success: bool
    message: str
    save_game: dict[str, Any] | None = None
    all_saves: list[dict[str, Any]] | None = None
    game_data: dict[str, Any] | None = None
    available_slots: list[int] | None = None


@dataclass
class SaveGameDTO:
    """DTO для передачи данных сохранения."""

    save_id: str
    character_name: str
    character_level: int
    character_class: str
    save_time: str
    slot_number: int
    game_version: str
    playtime_minutes: int
    location: str

    @classmethod
    def from_entity(cls, entity) -> "SaveGameDTO":
        """Создать DTO из сущности.

        Args:
            entity: Сущность сохранения

        Returns:
            DTO сохранения
        """
        # Безопасное преобразование даты
        save_time = entity.save_time
        if isinstance(save_time, str):
            save_time = save_time  # Уже строка
        else:
            save_time = save_time.isoformat()  # datetime в строку

        return cls(
            save_id=entity.save_id,
            character_name=entity.character_name,
            character_level=entity.character_level,
            character_class=entity.character_class,
            save_time=save_time,
            slot_number=entity.slot_number,
            game_version=entity.game_version,
            playtime_minutes=(
                int(entity.playtime_minutes)
                if isinstance(entity.playtime_minutes, (int, str))
                else 0
            ),
            location=entity.location,
        )

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать в словарь.

        Returns:
            Словарь с данными
        """
        return {
            "save_id": self.save_id,
            "character_name": self.character_name,
            "character_level": self.character_level,
            "character_class": self.character_class,
            "save_time": self.save_time,
            "slot_number": self.slot_number,
            "game_version": self.game_version,
            "playtime_minutes": self.playtime_minutes,
            "location": self.location,
        }

    def get_display_info(self) -> dict[str, str]:
        """Получить информацию для отображения.

        Returns:
            Словарь с отображаемой информацией
        """
        save_time = datetime.fromisoformat(self.save_time)
        return {
            "save_id": self.save_id,
            "character_name": self.character_name,
            "character_level": str(self.character_level),
            "character_class": self.character_class,
            "save_time": save_time.strftime("%Y-%m-%d %H:%M"),
            "slot_number": str(self.slot_number),
            "playtime_hours": f"{self.playtime_minutes // 60}ч {self.playtime_minutes % 60}м",
            "location": self.location,
        }


@dataclass
class SaveSlotDTO:
    """DTO для слота сохранения."""

    slot_number: int
    is_occupied: bool
    save_info: SaveGameDTO | None = None

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать в словарь.

        Returns:
            Словарь с данными слота
        """
        result = {
            "slot_number": self.slot_number,
            "is_occupied": self.is_occupied,
        }

        if self.save_info:
            result["save_info"] = self.save_info.to_dict()  # type: ignore

        return result


@dataclass
class CharacterPreviewDTO:
    """DTO для предпросмотра персонажа."""

    name: str
    level: int
    character_class: str
    race: str | None = None
    background: str | None = None
    abilities: dict[str, int] | None = None
    hp: int | None = None
    ac: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать в словарь.

        Returns:
            Словарь с данными персонажа
        """
        return {
            "name": self.name,
            "level": self.level,
            "character_class": self.character_class,
            "race": self.race,
            "background": self.background,
            "abilities": self.abilities,
            "hp": self.hp,
            "ac": self.ac,
        }
