"""Схемы данных для контента игры."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List
from enum import Enum


class CompatibilityLevel(Enum):
    """Уровни совместимости."""
    EXACT = "exact"          # Точное совпадение версии
    MAJOR = "major"          # Основная версия совпадает
    MINOR = "minor"          # Минорная версия совпадает
    PATCH = "patch"          # Патчная версия совпадает


@dataclass
class ModManifest:
    """Манифест мода."""
    name: str
    version: str
    description: str
    author: str
    
    # Совместимость
    compatible_version: str
    compatibility_level: CompatibilityLevel = CompatibilityLevel.MINOR
    
    # Зависимости
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    load_before: List[str] = field(default_factory=list)
    load_after: List[str] = field(default_factory=list)
    
    # Контент
    provides: List[str] = field(default_factory=list)


@dataclass
class AdventureManifest:
    """Манифест приключения."""
    name: str
    version: str
    description: str
    author: str
    
    # Требования
    min_level: int
    max_level: int
    recommended_level: int
    
    # Предварительные требования
    requires_items: List[str] = field(default_factory=list)
    requires_abilities: List[str] = field(default_factory=list)
    
    # Продолжительность
    estimated_hours: int
    
    # Контент
    start_location: str
    quest_count: int


@dataclass
class Location:
    """Локация приключения."""
    id: str
    name: str
    description: str
    
    # Навигация
    exits: dict[str, str] = field(default_factory=dict)
    
    # Содержимое
    npcs: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    
    # Внешние зависимости
    required_locations: List[str] = field(default_factory=list)


@dataclass
class Quest:
    """Квест в приключении."""
    id: str
    name: str
    description: str
    
    # Статус и прогресс
    status: str
    stages: List[str] = field(default_factory=list)
    
    # Награды
    experience_reward: int = 0
    gold_reward: int = 0
    item_rewards: List[str] = field(default_factory=list)


@dataclass
class Npc:
    """NPC в приключении."""
    id: str
    name: str
    description: str
    
    # Характеристики
    level: int
    health: int
    armor_class: int
    
    # Поведение
    dialogue: str
    hostility: str
    
    # Торговля
    sells_items: List[str] = field(default_factory=list)
    buys_items: List[str] = field(default_factory=list)


@dataclass
class Event:
    """Событие в приключении."""
    id: str
    name: str
    description: str
    
    # Условия срабатывания
    trigger_conditions: List[str] = field(default_factory=list)
    
    # Действия
    actions: List[str] = field(default_factory=list)
    
    # Результаты
    outcomes: dict[str, str] = field(default_factory=dict)
