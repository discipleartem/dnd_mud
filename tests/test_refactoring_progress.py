"""Тесты для проверки прогресса рефакторинга проекта.

Проверяет базовую функциональность после рефакторинга.
"""

import pytest
from pathlib import Path
import sys

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_main_menu_import():
    """Проверка импорта главного меню."""
    try:
        from ui.main_menu.main import show_main_menu
        assert show_main_menu is not None
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать главное меню: {e}")


def test_new_game_import():
    """Проверка импорта создания новой игры."""
    try:
        from ui.main_menu.new_game import new_game
        assert new_game is not None
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать new_game: {e}")


def test_character_adapter_import():
    """Проверка импорта адаптеров персонажа."""
    try:
        from ui.adapters.updated_adapters import Character, Race, SubRace
        assert Character is not None
        assert Race is not None
        assert SubRace is not None
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать адаптеры: {e}")


def test_dto_import():
    """Проверка импорта DTO."""
    try:
        from ui.dto.character_dto import CharacterDTO, RaceDTO, AbilityScoreDTO
        assert CharacterDTO is not None
        assert RaceDTO is not None
        assert AbilityScoreDTO is not None
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать DTO: {e}")


def test_race_factory_import():
    """Проверка импорта фабрики рас."""
    try:
        from ui.factories.domain_factory import RaceFactory
        # Не создаем экземпляр, чтобы избежать проблем с данными
        assert RaceFactory is not None
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать RaceFactory: {e}")


def test_character_creation():
    """Проверка базового создания персонажа."""
    try:
        from ui.adapters.updated_adapters import Character
        from ui.dto.character_dto import CharacterDTO
        
        # Создаем базовый персонаж
        character = Character(CharacterDTO(name="Тестовый персонаж"))
        assert character.name == "Тестовый персонаж"
        assert character.level == 1
    except Exception as e:
        pytest.fail(f"Не удалось создать персонажа: {e}")


def test_race_creation():
    """Проверка создания расы."""
    try:
        from ui.adapters.updated_adapters import Race
        from ui.dto.character_dto import RaceDTO
        
        # Создаем базовую расу
        race = Race(RaceDTO(name="Человек", speed=30))
        assert race.name == "Человек"
        assert race.speed == 30
        assert race.ability_bonuses_description == ""
    except Exception as e:
        pytest.fail(f"Не удалось создать расу: {e}")


def test_container_import():
    """Проверка импорта DI контейнера."""
    try:
        from core.container import DIContainer
        container = DIContainer()
        assert container is not None
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать DI контейнер: {e}")


def test_interfaces_import():
    """Проверка импорта интерфейсов."""
    try:
        from interfaces.repositories import IRaceRepository, ICharacterRepository
        assert IRaceRepository is not None
        assert ICharacterRepository is not None
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать интерфейсы: {e}")


if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v"])
