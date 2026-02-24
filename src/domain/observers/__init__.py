"""Наблюдатели доменных событий.

Содержит реализации паттерна Observer для обработки событий.
"""

from .character_events import (
    CharacterAbilityChangeEvent,
    CharacterEventPublisher,
    CharacterLevelUpEvent,
    CharacterLoggerObserver,
    CharacterStatsObserver,
)

__all__ = [
    "CharacterEventPublisher",
    "CharacterLevelUpEvent",
    "CharacterAbilityChangeEvent",
    "CharacterLoggerObserver",
    "CharacterStatsObserver",
]
