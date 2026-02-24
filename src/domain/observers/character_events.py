"""Наблюдатели для событий персонажа.

Реализует паттерн Observer для отслеживания изменений персонажа.
Следует принципам Domain-Driven Design и Clean Architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol


class CharacterEvent(Protocol):
    """Протокол событий персонажа."""

    def get_event_type(self) -> str:
        """Получить тип события."""
        ...

    def get_character_id(self) -> str:
        """Получить ID персонажа."""
        ...

    def get_data(self) -> dict[str, Any]:
        """Получить данные события."""
        ...


class CharacterEventHandler(Protocol):
    """Протокол обработчика событий персонажа."""

    def handle_event(self, event: CharacterEvent) -> None:
        """Обработать событие персонажа.

        Args:
            event: Событие персонажа
        """
        ...


class CharacterEventObserver(ABC):
    """Абстрактный наблюдатель событий персонажа."""

    @abstractmethod
    def update(self, event: CharacterEvent) -> None:
        """Обновить состояние при событии.

        Args:
            event: Событие персонажа
        """
        pass


class CharacterLevelUpEvent:
    """Событие повышения уровня персонажа."""

    def __init__(self, character_id: str, old_level: int, new_level: int):
        """Инициализировать событие повышения уровня.

        Args:
            character_id: ID персонажа
            old_level: Старый уровень
            new_level: Новый уровень
        """
        self._character_id = character_id
        self._old_level = old_level
        self._new_level = new_level

    def get_event_type(self) -> str:
        """Получить тип события."""
        return "level_up"

    def get_character_id(self) -> str:
        """Получить ID персонажа."""
        return self._character_id

    def get_data(self) -> dict[str, Any]:
        """Получить данные события."""
        return {
            "old_level": self._old_level,
            "new_level": self._new_level,
            "level_difference": self._new_level - self._old_level,
        }


class CharacterAbilityChangeEvent:
    """Событие изменения характеристики."""

    def __init__(
        self, character_id: str, ability: str, old_value: int, new_value: int
    ):
        """Инициализировать событие изменения характеристики.

        Args:
            character_id: ID персонажа
            ability: Название характеристики
            old_value: Старое значение
            new_value: Новое значение
        """
        self._character_id = character_id
        self._ability = ability
        self._old_value = old_value
        self._new_value = new_value

    def get_event_type(self) -> str:
        """Получить тип события."""
        return "ability_change"

    def get_character_id(self) -> str:
        """Получить ID персонажа."""
        return self._character_id

    def get_data(self) -> dict[str, Any]:
        """Получить данные события."""
        return {
            "ability": self._ability,
            "old_value": self._old_value,
            "new_value": self._new_value,
            "difference": self._new_value - self._old_value,
        }


class CharacterEventPublisher:
    """Издатель событий персонажа.

    Реализует Subject в паттерне Observer.
    """

    def __init__(self) -> None:
        """Инициализировать издателя событий."""
        self._observers: list[CharacterEventObserver] = []

    def add_observer(self, observer: CharacterEventObserver) -> None:
        """Добавить наблюдателя.

        Args:
            observer: Наблюдатель событий
        """
        self._observers.append(observer)

    def remove_observer(self, observer: CharacterEventObserver) -> None:
        """Удалить наблюдателя.

        Args:
            observer: Наблюдатель событий
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, event: CharacterEvent) -> None:
        """Уведомить всех наблюдателей о событии.

        Args:
            event: Событие персонажа
        """
        for observer in self._observers:
            observer.update(event)


class CharacterLoggerObserver(CharacterEventObserver):
    """Наблюдатель для логирования событий персонажа."""

    def __init__(self) -> None:
        """Инициализировать наблюдатель логирования."""
        import logging

        self._logger = logging.getLogger(__name__)

    def update(self, event: CharacterEvent) -> None:
        """Записать событие в лог.

        Args:
            event: Событие персонажа
        """
        event_type = event.get_event_type()
        character_id = event.get_character_id()
        data = event.get_data()

        self._logger.info(
            f"Событие персонажа {character_id}: {event_type}",
            extra={
                "character_id": character_id,
                "event_type": event_type,
                "data": data,
            },
        )


class CharacterStatsObserver(CharacterEventObserver):
    """Наблюдатель для сбора статистики персонажа."""

    def __init__(self) -> None:
        """Инициализировать наблюдатель статистики."""
        self._event_counts: dict[str, int] = {}
        self._character_events: dict[str, list] = {}

    def update(self, event: CharacterEvent) -> None:
        """Обновить статистику при событии.

        Args:
            event: Событие персонажа
        """
        event_type = event.get_event_type()
        character_id = event.get_character_id()

        # Счетчик событий по типам
        self._event_counts[event_type] = (
            self._event_counts.get(event_type, 0) + 1
        )

        # История событий по персонажам
        if character_id not in self._character_events:
            self._character_events[character_id] = []

        self._character_events[character_id].append(
            {
                "type": event_type,
                "data": event.get_data(),
            }
        )

    def get_event_count(self, event_type: str) -> int:
        """Получить количество событий определенного типа.

        Args:
            event_type: Тип события

        Returns:
            Количество событий
        """
        return self._event_counts.get(event_type, 0)

    def get_character_events(self, character_id: str) -> list:
        """Получить события персонажа.

        Args:
            character_id: ID персонажа

        Returns:
            Список событий персонажа
        """
        return self._character_events.get(character_id, [])
