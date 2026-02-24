#!/usr/bin/env python3
"""Тест только доменной модели D&D MUD.

Проверяет базовую функциональность новой чистой архитектуры
без зависимостей от UI слоя.
"""

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_domain_only():
    """Тест только доменных сущностей."""
    print("🧪 Тест доменной модели...")

    # Тест Value Objects
    from src.domain.value_objects.ability_scores import AbilityScores
    from src.domain.value_objects.size import Size, SizeCategory

    # Тест Size
    medium_size = Size.from_category(SizeCategory.MEDIUM)
    print(f"✅ Size: {medium_size}")
    print(f"✅ Категория размера: {medium_size.category}")
    print(f"✅ Модификатор скрытости: {medium_size.get_modifier_for_stealth()}")

    # Тест AbilityScores с валидными значениями для point buy
    scores = AbilityScores(strength=14, dexterity=14, constitution=13, intelligence=12, wisdom=10, charisma=8)
    print(f"✅ AbilityScores: {scores}")
    print(f"✅ Модификатор силы: {scores.get_modifier('strength')}")
    print(f"✅ Все модификаторы: {scores.get_all_modifiers()}")
    print(f"✅ Стоимость point buy: {scores.get_point_buy_cost()}")

    # Тест Race entity
    from src.domain.entities.language import Language, LanguageMechanics
    from src.domain.entities.race import Feature, Race, SubRace

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
    print(f"✅ Бонусы к характеристикам: {race.ability_bonuses}")
    print(f"✅ Эффективные бонусы: {race.get_effective_ability_bonuses()}")

    # Тест SubRace
    subrace = SubRace(
        name="Высший эльф",
        description="Магически одаренный эльф",
        ability_bonuses={"intelligence": 1},
        languages=["elvish"],
        inherit_base_abilities=True
    )

    print(f"✅ SubRace: {subrace}")
    print(f"✅ Бонусы подрасы: {subrace.ability_bonuses}")

    # Тест эффективных бонусов с подрасой
    effective_bonuses = race.get_effective_ability_bonuses(subrace)
    print(f"✅ Эффективные бонусы с подрасой: {effective_bonuses}")

    # Тест Character entity
    from src.domain.entities.character import Character

    character = Character(
        name="Леголас",
        race=race,
        subrace=subrace,
        character_class="Воин",
        level=3,
        ability_scores=scores
    )

    print(f"✅ Character: {character}")
    print(f"✅ Размер персонажа: {character.size.category.value}")
    print(f"✅ Скорость персонажа: {character.speed}")
    print(f"✅ Языки персонажа: {character.languages}")
    print(f"✅ Модификатор силы: {character.get_ability_modifier('strength')}")
    print(f"✅ Все модификаторы: {character.get_all_ability_modifiers()}")

    # Тест операций с языками
    print(f"✅ Знает язык 'elvish': {character.knows_language('elvish')}")

    # Создадим тестовый язык для проверки
    dwarvish_lang = Language(
        code="dwarvish",
        type="standard",
        difficulty="medium",
        mechanics=LanguageMechanics(learnable_by_all=True)
    )
    print(f"✅ Может изучить 'dwarvish': {character.can_learn_language(dwarvish_lang)}")

    # Тест валидации
    errors = character.validate()
    print(f"✅ Ошибки валидации: {errors}")

    # Тест сводной информации
    summary = character.get_summary()
    print(f"✅ Сводка: {summary}")

    return True


def test_domain_services():
    """Тест доменных сервисов."""
    print("\n🧪 Тест доменных сервисов...")

    from src.domain.entities.language import Language, LanguageMechanics
    from src.domain.entities.race import Race
    from src.domain.services.character_creation_service import (
        CharacterCreationService,
    )
    from src.domain.value_objects.size import Size, SizeCategory

    # Создаем тестовые данные
    human_race = Race(
        name="Человек",
        description="Универсальная раса",
        ability_bonuses={"strength": 1, "dexterity": 1},
        size=Size.from_category(SizeCategory.MEDIUM),
        speed=30,
        languages=["common"]
    )

    common_lang = Language(
        code="common",
        type="standard",
        difficulty="easy",
        mechanics=LanguageMechanics(is_default=True, learnable_by_all=True)
    )

    # Создаем сервис
    creation_service = CharacterCreationService([human_race], [common_lang])

    # Тест создания персонажа
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

    # Тест валидации
    errors = creation_service.validate_character_data(character_data)
    print(f"✅ Ошибки валидации: {errors}")

    # Тест доступных рас
    races = creation_service.get_available_races()
    print(f"✅ Доступные расы: {[r.name for r in races]}")

    # Тест стоимости point buy
    cost = creation_service.calculate_point_buy_cost(character_data["ability_scores"])
    print(f"✅ Стоимость характеристик: {cost}")

    return True


def test_yaml_infrastructure():
    """Тест YAML инфраструктуры."""
    print("\n🧪 Тест YAML инфраструктуры...")

    from infrastructure.loaders.yaml_loader import YamlLoader

    loader = YamlLoader(enable_cache=True)

    # Тест загрузки из строки
    yaml_string = """
    test:
      name: "Тест"
      value: 42
      nested:
        items: [1, 2, 3]
    """

    data = loader.load_from_string(yaml_string)
    print(f"✅ Загружено из строки: {data}")

    # Тест кэширования
    is_cached = loader.is_cached(yaml_string)
    print(f"✅ Данные в кэше: {is_cached}")

    # Тест статистики кэша
    stats = loader.get_cache_stats()
    print(f"✅ Статистика кэша: {stats}")

    # Тест очистки кэша
    loader.clear_cache()
    stats_after_clear = loader.get_cache_stats()
    print(f"✅ Статистика после очистки: {stats_after_clear}")

    return True


def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование доменной модели D&D MUD\n")

    tests = [
        test_domain_only,
        test_domain_services,
        test_yaml_infrastructure,
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
        print("\n🎉 Все тесты пройдены! Доменная модель работает корректно.")
        return 0
    else:
        print(f"\n⚠️ {failed} тестов не пройдены. Нужно исправить ошибки.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
