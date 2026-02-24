#!/usr/bin/env python3
"""Тест новой архитектуры D&D MUD.

Проверяет базовую функциональность новой чистой архитектуры.
"""

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_domain_entities():
    """Тест доменных сущностей."""
    print("🧪 Тест доменных сущностей...")

    # Тест Value Objects
    from src.domain.value_objects.ability_scores import AbilityScores
    from src.domain.value_objects.size import Size, SizeCategory

    # Тест Size
    medium_size = Size.from_category(SizeCategory.MEDIUM)
    print(f"✅ Size: {medium_size}")

    # Тест AbilityScores
    scores = AbilityScores(strength=16, dexterity=14, constitution=12, intelligence=10, wisdom=8, charisma=6)
    print(f"✅ AbilityScores: {scores}")
    print(f"✅ Модификатор силы: {scores.get_modifier('strength')}")

    # Тест Race entity
    from src.domain.entities.race import Feature, Race

    feature = Feature(
        name="Темное зрение",
        description="Вы можете видеть в темноте",
        mechanics={"range": 60}
    )

    race = Race(
        name="Эльф",
        description="Изящное долгоживущее существо",
        ability_bonuses={"dexterity": 2},
        size=medium_size,
        speed=30,
        languages=["elvish", "common"],
        features=[feature]
    )

    print(f"✅ Race: {race}")
    print(f"✅ Языки расы: {race.languages}")

    # Тест Character entity
    from src.domain.entities.character import Character

    character = Character(
        name="Леголас",
        race=race,
        character_class="Воин",
        level=3,
        ability_scores=scores
    )

    print(f"✅ Character: {character}")
    print(f"✅ Скорость персонажа: {character.speed}")
    print(f"✅ Языки персонажа: {character.languages}")

    return True


def test_yaml_loader():
    """Тест YAML загрузчика."""
    print("\n🧪 Тест YAML загрузчика...")

    from src.infrastructure.loaders.yaml_loader import YamlLoader

    loader = YamlLoader(enable_cache=True)

    # Тест загрузки из строки
    yaml_string = """
    test:
      name: "Тест"
      value: 42
    """

    data = loader.load_from_string(yaml_string)
    print(f"✅ Загружено из строки: {data}")

    # Тест кэширования
    is_cached = loader.is_cached(yaml_string)
    print(f"✅ Данные в кэше: {is_cached}")

    # Тест статистики кэша
    stats = loader.get_cache_stats()
    print(f"✅ Статистика кэша: {stats}")

    return True


def test_di_container():
    """Тест DI контейнера."""
    print("\n🧪 Тест DI контейнера...")

    from src.core.container import get_container

    container = get_container()

    # Тест регистрации и получения
    from src.infrastructure.loaders.yaml_loader import YamlLoader

    container.register_singleton(YamlLoader, YamlLoader)

    loader = container.get(YamlLoader)
    print(f"✅ Получен из контейнера: {type(loader).__name__}")

    # Тест проверки наличия
    has_loader = container.has(YamlLoader)
    print(f"✅ Загрузчик зарегистрирован: {has_loader}")

    return True


def test_integration():
    """Тест интеграции компонентов."""
    print("\n🧪 Тест интеграции...")

    # Создаем расу
    from src.domain.entities.race import Race
    from src.domain.services.character_creation_service import (
        CharacterCreationService,
    )
    from src.domain.value_objects.size import Size, SizeCategory

    # Создаем расу
    human_race = Race(
        name="Человек",
        description="Универсальная раса",
        ability_bonuses={"strength": 1, "dexterity": 1},
        size=Size.from_category(SizeCategory.MEDIUM),
        speed=30,
        languages=["common"]
    )

    # Создаем сервис создания персонажей
    creation_service = CharacterCreationService([human_race], [])

    # Создаем персонажа
    character_data = {
        "name": "Арагорн",
        "race": "Человек",
        "character_class": "Рейнджер",
        "level": 5,
        "ability_scores": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 15,
            "intelligence": 12,
            "wisdom": 13,
            "charisma": 10
        }
    }

    character = creation_service.create_character(character_data)
    print(f"✅ Создан персонаж: {character}")

    # Проверяем валидацию
    errors = creation_service.validate_character_data(character_data)
    print(f"✅ Ошибки валидации: {errors}")

    return True


def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование новой архитектуры D&D MUD\n")

    tests = [
        test_domain_entities,
        test_yaml_loader,
        test_di_container,
        test_integration,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Ошибка в {test.__name__}: {e}")
            failed += 1

    print("\n📊 Результаты тестов:")
    print(f"✅ Пройдено: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📈 Всего: {passed + failed}")

    if failed == 0:
        print("\n🎉 Все тесты пройдены! Новая архитектура работает корректно.")
        return 0
    else:
        print(f"\n⚠️ {failed} тестов не пройдены. Нужно исправить ошибки.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
