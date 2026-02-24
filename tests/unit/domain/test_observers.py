"""Тесты для наблюдателей доменных событий."""


from src.domain.observers.character_events import (
    CharacterAbilityChangeEvent,
    CharacterEventPublisher,
    CharacterLevelUpEvent,
    CharacterLoggerObserver,
    CharacterStatsObserver,
)


class TestCharacterLevelUpEvent:
    """Тесты события повышения уровня."""

    def test_level_up_event_data(self) -> None:
        """Тест данных события повышения уровня."""
        event = CharacterLevelUpEvent("char_123", 3, 4)

        assert event.get_event_type() == "level_up"
        assert event.get_character_id() == "char_123"

        data = event.get_data()
        assert data["old_level"] == 3
        assert data["new_level"] == 4
        assert data["level_difference"] == 1


class TestCharacterAbilityChangeEvent:
    """Тесты события изменения характеристики."""

    def test_ability_change_event_data(self) -> None:
        """Тест данных события изменения характеристики."""
        event = CharacterAbilityChangeEvent("char_123", "strength", 14, 16)

        assert event.get_event_type() == "ability_change"
        assert event.get_character_id() == "char_123"

        data = event.get_data()
        assert data["ability"] == "strength"
        assert data["old_value"] == 14
        assert data["new_value"] == 16
        assert data["difference"] == 2


class TestCharacterEventPublisher:
    """Тесты издателя событий персонажа."""

    def test_add_remove_observers(self) -> None:
        """Тест добавления и удаления наблюдателей."""
        publisher = CharacterEventPublisher()
        observer = CharacterStatsObserver()

        # Добавление наблюдателя
        publisher.add_observer(observer)
        assert observer in publisher._observers

        # Удаление наблюдателя
        publisher.remove_observer(observer)
        assert observer not in publisher._observers

    def test_notify_observers(self) -> None:
        """Тест уведомления наблюдателей."""
        publisher = CharacterEventPublisher()
        observer = CharacterStatsObserver()

        publisher.add_observer(observer)

        event = CharacterLevelUpEvent("char_123", 3, 4)
        publisher.notify_observers(event)

        # Проверяем, что наблюдатель получил событие
        assert observer.get_event_count("level_up") == 1
        events = observer.get_character_events("char_123")
        assert len(events) == 1
        assert events[0]["type"] == "level_up"


class TestCharacterStatsObserver:
    """Тесты наблюдателя статистики."""

    def test_track_events(self) -> None:
        """Тест отслеживания событий."""
        observer = CharacterStatsObserver()

        # Добавляем несколько событий
        level_up = CharacterLevelUpEvent("char_123", 3, 4)
        ability_change = CharacterAbilityChangeEvent("char_123", "strength", 14, 16)

        observer.update(level_up)
        observer.update(ability_change)

        # Проверяем счетчики
        assert observer.get_event_count("level_up") == 1
        assert observer.get_event_count("ability_change") == 1

        # Проверяем события персонажа
        events = observer.get_character_events("char_123")
        assert len(events) == 2
        assert events[0]["type"] == "level_up"
        assert events[1]["type"] == "ability_change"

    def test_multiple_characters(self) -> None:
        """Тест отслеживания событий нескольких персонажей."""
        observer = CharacterStatsObserver()

        # События для разных персонажей
        event1 = CharacterLevelUpEvent("char_123", 3, 4)
        event2 = CharacterLevelUpEvent("char_456", 2, 3)

        observer.update(event1)
        observer.update(event2)

        # Проверяем, что события разделены по персонажам
        assert len(observer.get_character_events("char_123")) == 1
        assert len(observer.get_character_events("char_456")) == 1
        assert observer.get_event_count("level_up") == 2


class TestCharacterLoggerObserver:
    """Тесты наблюдателя логирования."""

    def test_logging_events(self) -> None:
        """Тест логирования событий."""
        observer = CharacterLoggerObserver()

        event = CharacterLevelUpEvent("char_123", 3, 4)

        # Проверяем, что логгер создан и метод не вызывает ошибок
        assert hasattr(observer, '_logger')

        # Вызов должен пройти без ошибок
        observer.update(event)
