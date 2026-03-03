"""Модель сущности персонажа."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Character:
    """Сущность персонажа D&D.
    
    Применяемые паттерны:
    - Entity (Сущность) — представляет бизнес-объект с уникальной идентичностью
    - Dataclass — автоматическая генерация __init__, __repr__, __eq__
    
    Применяемые принципы:
    - Single Responsibility — отвечает только за данные персонажа
    - Immutability — поле id неизменяемо после создания
    """
    
    id: Optional[int] = None
    name: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    @property
    def is_new(self) -> bool:
        """Проверяет, является ли персонаж новым (не сохраненным)."""
        return self.id is None
    
    def with_updated_timestamp(self) -> "Character":
        """Возвращает копию персонажа с обновленным timestamp."""
        if self.id is None:
            return Character(
                name=self.name,
                created_at=self.created_at,
                updated_at=datetime.now()
            )
        return Character(
            id=self.id,
            name=self.name,
            created_at=self.created_at,
            updated_at=datetime.now()
        )
