"""Фабрики доменных сущностей.

Содержит фабрики для создания доменных объектов согласно паттерну Factory.
"""

from .character_factory import CharacterFactory
from .race_factory import RaceFactory

__all__ = ["CharacterFactory", "RaceFactory"]
