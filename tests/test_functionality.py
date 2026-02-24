"""Тесты функциональности после рефакторинга.

Проверяет что базовая функциональность работает корректно.
"""

import pytest
from pathlib import Path
import sys

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_character_creation_flow():
    """Тест полного потока создания персонажа."""
    try:
        from ui.adapters.updated_adapters import Character
        from ui.dto.character_dto import CharacterDTO, AbilityScoreDTO
        
        # 1. Создаем персонажа
        character = Character(CharacterDTO(name="Тестовый персонаж"))
        assert character.name == "Тестовый персонаж"
        assert character.level == 1
        
        # 2. Устанавливаем характеристики
        scores = AbilityScoreDTO(strength=16, dexterity=14, constitution=15)
        character.set_ability_scores(scores)
        
        # 3. Проверяем DTO
        dto = character.get_dto()
        assert dto.name == "Тестовый персонаж"
        assert dto.ability_scores is not None
        
        print("✅ Поток создания персонажа работает")
        
    except Exception as e:
        pytest.fail(f"Ошибка в потоке создания персонажа: {e}")


def test_race_adapter_functionality():
    """Тест функциональности адаптера рас."""
    try:
        from ui.adapters.updated_adapters import Race
        from ui.dto.character_dto import RaceDTO
        
        # Создаем DTO с данными
        race_dto = RaceDTO(
            name="Человек",
            description="Человечество - самая разнообразная раса",
            ability_bonuses={"strength": 1, "dexterity": 1},
            languages=["Общий", "Дварфийский"],
            features=[
                {"name": "Мастерство", "description": "Дополнительное умение"}
            ]
        )
        
        # Создаем адаптер
        race = Race(race_dto)
        
        # Проверяем свойства
        assert race.name == "Человек"
        assert race.speed == 30
        assert race.ability_bonuses == {"strength": 1, "dexterity": 1}
        assert race.languages == ["Общий", "Дварфийский"]
        assert len(race.features) == 1
        assert race.features[0]["name"] == "Мастерство"
        
        # Проверяем методы
        display = race.get_languages_display()
        assert "Общий" in display
        
        print("✅ Адаптер рас работает корректно")
        
    except Exception as e:
        pytest.fail(f"Ошибка в адаптере рас: {e}")


def test_dto_conversion():
    """Тест преобразования DTO."""
    try:
        from ui.dto.character_dto import CharacterDTO, RaceDTO, AbilityScoreDTO
        
        # Тест AbilityScoreDTO
        scores = AbilityScoreDTO(strength=16, dexterity=14)
        scores_dict = scores.to_dict()
        
        assert "strength" in scores_dict
        assert scores_dict["strength"]["value"] == 16
        assert scores_dict["strength"]["modifier"] == 3  # (16-10)//2
        
        # Тест модификаторов
        modifiers = scores.get_all_modifiers()
        assert modifiers["strength"] == 3
        assert modifiers["dexterity"] == 2
        
        print("✅ Преобразование DTO работает корректно")
        
    except Exception as e:
        pytest.fail(f"Ошибка в преобразовании DTO: {e}")


def test_size_class():
    """Тест класса Size."""
    try:
        from ui.adapters.updated_adapters import Size
        
        # Тест создания
        size = Size("medium")
        assert size.category == "medium"
        
        # Тест локализации
        localized = size.get_localized_name()
        assert localized == "Средний"
        
        # Тест других размеров
        small_size = Size("small")
        assert small_size.get_localized_name() == "Маленький"
        
        large_size = Size("large")
        assert large_size.get_localized_name() == "Большой"
        
        print("✅ Класс Size работает корректно")
        
    except Exception as e:
        pytest.fail(f"Ошибка в классе Size: {e}")


def test_container_integration():
    """Тест интеграции с DI контейнером."""
    try:
        from core.container import DIContainer
        
        # Создаем контейнер
        container = DIContainer()
        
        # Регистрируем сервис
        container.register_singleton(str, lambda: "test_service")
        
        # Получаем сервис
        service = container.get(str)
        assert service == "test_service"
        
        print("✅ DI контейнер работает корректно")
        
    except Exception as e:
        pytest.fail(f"Ошибка в DI контейнере: {e}")


def test_interfaces_compliance():
    """Тест соответствия интерфейсам."""
    try:
        from interfaces.repositories import IRaceRepository, ICharacterRepository
        
        # Проверяем что интерфейсы существуют
        assert IRaceRepository is not None
        assert ICharacterRepository is not None
        
        # Проверяем методы
        assert hasattr(IRaceRepository, 'find_by_name')
        assert hasattr(IRaceRepository, 'find_all')
        assert hasattr(IRaceRepository, 'find_subrace_by_name')
        
        assert hasattr(ICharacterRepository, 'find_by_name')
        assert hasattr(ICharacterRepository, 'find_all')
        
        print("✅ Интерфейсы корректно определены")
        
    except Exception as e:
        pytest.fail(f"Ошибка в интерфейсах: {e}")


if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v", "-s"])
