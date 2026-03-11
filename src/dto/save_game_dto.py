"""DTO для сохранений игр.

Следует Clean Architecture - объекты передачи данных между слоями.
Используются для коммуникации между Controllers, Use Cases и Adapters.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class SaveGameRequest:
    """Запрос на операцию с сохранением."""
    action: str  # "save", "load", "delete", "list"
    save_id: Optional[str] = None
    slot_number: Optional[int] = None
    character_name: Optional[str] = None
    character_level: Optional[int] = None
    character_class: Optional[str] = None
    character_data: Optional[Dict[str, Any]] = None
    location: Optional[str] = None


@dataclass
class SaveGameResponse:
    """Ответ на операцию с сохранением."""
    success: bool
    message: str
    save_game: Optional[Dict[str, Any]] = None
    all_saves: Optional[List[Dict[str, Any]]] = None
    game_data: Optional[Dict[str, Any]] = None
    available_slots: Optional[List[int]] = None


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
        return cls(
            save_id=entity.save_id,
            character_name=entity.character_name,
            character_level=entity.character_level,
            character_class=entity.character_class,
            save_time=entity.save_time.isoformat(),
            slot_number=entity.slot_number,
            game_version=entity.game_version,
            playtime_minutes=entity.playtime_minutes,
            location=entity.location
        )
    
    def to_dict(self) -> Dict[str, Any]:
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
            "location": self.location
        }
    
    def get_display_info(self) -> Dict[str, str]:
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
            "location": self.location
        }


@dataclass
class SaveSlotDTO:
    """DTO для слота сохранения."""
    slot_number: int
    is_occupied: bool
    save_info: Optional[SaveGameDTO] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь.
        
        Returns:
            Словарь с данными слота
        """
        result = {
            "slot_number": self.slot_number,
            "is_occupied": self.is_occupied
        }
        
        if self.save_info:
            result["save_info"] = self.save_info.to_dict()
        
        return result


@dataclass
class CharacterPreviewDTO:
    """DTO для предпросмотра персонажа."""
    name: str
    level: int
    character_class: str
    race: Optional[str] = None
    background: Optional[str] = None
    abilities: Optional[Dict[str, int]] = None
    hp: Optional[int] = None
    ac: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
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
            "ac": self.ac
        }
