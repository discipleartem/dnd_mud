"""Тесты для Use Cases после рефакторинга.

Проверяет что бизнес-логика работает корректно с новыми адаптерами.
"""

import pytest
from pathlib import Path
import sys

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_ability_generation_use_case():
    """Тест Use Case для генерации характеристик."""
    try:
        from use_cases.ability_generation import AbilityGenerationUseCase
        from ui.dto.character_dto import AbilityScoreDTO
        
        use_case = AbilityGenerationUseCase()
        
        # Тест базовых характеристик
        basic_scores = use_case.generate_basic_scores()
        assert basic_scores.strength == 10
        assert basic_scores.dexterity == 10
        assert basic_scores.constitution == 10
        
        # Тест стандартного массива
        standard_scores = use_case.generate_standard_array()
        assert standard_scores.strength == 15
        assert standard_scores.dexterity == 14
        assert standard_scores.constitution == 13
        
        # Тест модификаторов
        assert basic_scores.get_modifier("strength") == 0
        assert standard_scores.get_modifier("strength") == 2  # (15-10)//2
        
        # Тест валидации
        errors = use_case.validate_scores(basic_scores)
        assert len(errors) == 0  # Базовые характеристики должны быть валидными
        
        # Тест невалидных характеристик
        invalid_scores = AbilityScoreDTO(strength=25, dexterity=0)
        errors = use_case.validate_scores(invalid_scores)
        assert len(errors) > 0  # Должны быть ошибки
        
        print("✅ AbilityGenerationUseCase работает корректно")
        
    except Exception as e:
        pytest.fail(f"Ошибка в AbilityGenerationUseCase: {e}")


def test_character_creation_use_case():
    """Тест Use Case для создания персонажа."""
    try:
        from use_cases.character_creation import CreateCharacterUseCase
        from ui.dto.character_dto import CharacterDTO
        from ui.adapters.updated_adapters import Character, Race
        
        # Создаем моковые репозитории
        class MockRaceRepository:
            def find_by_name(self, name):
                return None  # Для теста не нужен реальный объект
        
        class MockCharacterRepository:
            def save(self, entity):
                return entity
            def find_by_id(self, entity_id):
                return None
            def find_all(self):
                return []
            def delete(self, entity_id):
                return True
        
        # Создаем Use Case
        use_case = CreateCharacterUseCase(
            MockCharacterRepository(),
            MockRaceRepository()
        )
        
        # Создаем тестовую расу
        from ui.dto.character_dto import RaceDTO
        race_dto = RaceDTO(
            name="Человек",
            ability_bonuses={"strength": 1, "dexterity": 1}
        )
        race = Race(race_dto)
        
        # Тест создания персонажа с обновленными адаптерами
        character, errors = use_case.create_character_with_updated_adapters(
            name="Тестовый персонаж",
            race=race,
            subrace=None,
            character_class="Воин"
        )
        
        assert character is not None
        assert character.name == "Тестовый персонаж"
        assert character._dto.race_name == "Человек"  # Используем _dto для доступа
        assert character.ability_scores is not None
        
        # Проверяем применение бонусов
        scores = character.ability_scores
        assert scores.strength >= 11  # 10 + 1 бонус
        
        print("✅ CreateCharacterUseCase работает корректно")
        
    except Exception as e:
        pytest.fail(f"Ошибка в CreateCharacterUseCase: {e}")


def test_race_bonuses_application():
    """Тест применения расовых бонусов."""
    try:
        from use_cases.ability_generation import AbilityGenerationUseCase
        from ui.dto.character_dto import AbilityScoreDTO, RaceDTO
        from ui.adapters.updated_adapters import Race
        
        use_case = AbilityGenerationUseCase()
        
        # Создаем базовые характеристики
        base_scores = AbilityScoreDTO(
            strength=10, dexterity=10, constitution=10,
            intelligence=10, wisdom=10, charisma=10
        )
        
        # Создаем расу с бонусами
        race_dto = RaceDTO(
            name="Эльф",
            ability_bonuses={"dexterity": 2, "intelligence": 1}
        )
        race = Race(race_dto)
        
        # Применяем бонусы
        enhanced_scores = use_case.apply_racial_bonuses(base_scores, race)
        
        # Проверяем бонусы
        assert enhanced_scores.strength == 10  # Без бонуса
        assert enhanced_scores.dexterity == 12  # 10 + 2
        assert enhanced_scores.intelligence == 11  # 10 + 1
        assert enhanced_scores.constitution == 10  # Без бонуса
        
        print("✅ Применение расовых бонусов работает корректно")
        
    except Exception as e:
        pytest.fail(f"Ошибка в применении расовых бонусов: {e}")


def test_subrace_bonuses():
    """Тест бонусов подрас."""
    try:
        from use_cases.ability_generation import AbilityGenerationUseCase
        from ui.dto.character_dto import AbilityScoreDTO, RaceDTO
        from ui.adapters.updated_adapters import Race, SubRace
        
        use_case = AbilityGenerationUseCase()
        
        # Создаем базовые характеристики
        base_scores = AbilityScoreDTO(
            strength=10, dexterity=10, constitution=10,
            intelligence=10, wisdom=10, charisma=10
        )
        
        # Создаем расу
        race_dto = RaceDTO(name="Дварф", ability_bonuses={"constitution": 2})
        race = Race(race_dto)
        
        # Создаем подрасу с дополнительными бонусами
        subrace_dto = RaceDTO(
            name="Хилл Дварф",
            ability_bonuses={"wisdom": 1}
        )
        subrace = SubRace(subrace_dto)
        
        # Применяем бонусы расы и подрасы
        enhanced_scores = use_case.apply_racial_bonuses(base_scores, race, subrace)
        
        # Проверяем бонусы
        assert enhanced_scores.strength == 10  # Без бонуса
        assert enhanced_scores.constitution == 12  # 10 + 2 от расы
        assert enhanced_scores.wisdom == 11  # 10 + 1 от подрасы
        
        print("✅ Бонусы подрас работают корректно")
        
    except Exception as e:
        pytest.fail(f"Ошибка в бонусах подрас: {e}")


def test_complete_character_flow():
    """Тест полного потока создания персонажа."""
    try:
        from use_cases.ability_generation import AbilityGenerationUseCase
        from use_cases.character_creation import CreateCharacterUseCase
        from ui.dto.character_dto import AbilityScoreDTO, RaceDTO
        from ui.adapters.updated_adapters import Race, SubRace, Character
        
        # Создаем Use Cases
        ability_use_case = AbilityGenerationUseCase()
        
        # Создаем моковые репозитории
        class MockRaceRepository:
            def find_by_name(self, name):
                return None
        
        class MockCharacterRepository:
            def save(self, entity):
                return entity
            def find_by_id(self, entity_id):
                return None
            def find_all(self):
                return []
            def delete(self, entity_id):
                return True
        
        character_use_case = CreateCharacterUseCase(
            MockCharacterRepository(),
            MockRaceRepository()
        )
        
        # Создаем тестовые расу и подрасу
        race_dto = RaceDTO(
            name="Человек",
            ability_bonuses={"strength": 1, "charisma": 1}
        )
        race = Race(race_dto)
        
        subrace_dto = RaceDTO(
            name="Вариант человека",
            ability_bonuses={"intelligence": 1}
        )
        subrace = SubRace(subrace_dto)
        
        # Создаем персонажа через Use Case
        character, errors = character_use_case.create_character_with_updated_adapters(
            name="Арагорн",
            race=race,
            subrace=subrace,
            character_class="Рейнджер"
        )
        
        # Проверяем результат
        assert character is not None
        assert character.name == "Арагорн"
        assert len(errors) == 0  # Не должно быть ошибок
        
        # Проверяем характеристики с бонусами (стандартный массив + бонусы)
        scores = character.ability_scores
        assert scores.strength == 16  # 15 + 1 от расы
        assert scores.dexterity == 14  # 14 + 0 бонусов  
        assert scores.constitution == 13  # 13 + 0 бонусов
        assert scores.intelligence == 13  # 12 + 1 от подрасы
        assert scores.wisdom == 10  # 10 + 0 бонусов
        assert scores.charisma == 9  # 8 + 1 от расы
        
        print("✅ Полный поток создания персонажа работает корректно")
        
    except Exception as e:
        pytest.fail(f"Ошибка в полном потоке: {e}")


if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v", "-s"])
