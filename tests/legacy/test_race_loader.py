#!/usr/bin/env python3
"""Тестовый скрипт для проверки загрузки рас из YAML."""

import sys
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.entities.race import Race, SubRace


def test_race_loading() -> None:
    """Тест загрузки рас.

    Проверяет корректность загрузки рас из YAML файла
    и выводит информацию о каждой расе.
    """
    print("🧪 Тестируем загрузку рас из YAML...\n")

    races = _load_all_races()
    print(f"📊 Загружено рас: {len(races)}")

    for race_id, race in races.items():
        _print_race_info(race_id, race)

    _test_specific_race(races)


def _load_all_races() -> dict[str, "Race"]:
    """Загрузить все расы.

    Returns:
        Словарь рас
    """
    try:
        return Race.get_all_races()
    except Exception as e:
        print(f"❌ Ошибка загрузки рас: {e}")
        return {}


def _print_race_info(race_id: str, race: "Race") -> None:
    """Вывести информацию о расе.

    Args:
        race_id: ID расы.
        race: Объект расы.
    """
    print(f"\n🎭 Раса: {race.name} (ID: {race_id})")
    print(f"   Описание: {race.description}")
    print(f"   Бонусы: {race.ability_bonuses_description}")
    print(f"   Размер: {race.size}, Скорость: {race.speed}")
    print(f"   Языки: {', '.join(race.languages)}")
    print(f"   Черты: {len(race.features)}")
    print(f"   Подрасы: {len(race.subraces)}")

    # Показываем подрасы
    for subrace_id, subrace in race.subraces.items():
        _print_subrace_info(subrace_id, subrace)


def _print_subrace_info(subrace_id: str, subrace: "SubRace") -> None:
    """Вывести информацию о подрасе.

    Args:
        subrace_id: ID подрасы
        subrace: Объект подрасы
    """
    print(f"      📍 Подраса: {subrace.name} (ID: {subrace_id})")
    print(f"         Описание: {subrace.description}")
    print(f"         Бонусы: {subrace.ability_bonuses_description}")
    print(f"         Черты: {len(subrace.features)}")


def _test_specific_race(races: dict[str, "Race"]) -> None:
    """Тестировать получение конкретной расы.

    Args:
        races: Словарь рас для тестирования
    """
    print("\n🔍 Тестируем получение конкретной расы...")

    # Пробуем получить первую расу из списка
    if races:
        first_race_id = list(races.keys())[0]
        try:
            race = races[first_race_id]
            print(f"✅ Успешно получена раса: {race.name}")
        except Exception as e:
            print(f"❌ Ошибка получения расы: {e}")
    else:
        print("⚠️ Нет рас для тестирования")


def _test_specific_race_old() -> None:
    """Тестирование получения конкретной расы (устаревший метод).
    """
    print("\n" + "=" * 50)
    print("🔍 Тестируем получение конкретной расы:")

    human = Race.get_race_by_name("human")
    if human:
        print("\n👤 Человек:")
        print(f"   Бонусы характеристик: {human.ability_bonuses}")
        feature_names = [f.name for f in human.features]
        print(f"   Черты: {feature_names}")

        # Тестируем подрасу
        if human.subraces:
            first_subrace = list(human.subraces.values())[0]
            print(f"\n   🔸 {first_subrace.name}:")
            subrace_feature_names = [f.name for f in first_subrace.features]
            print(f"      Черты: {subrace_feature_names}")
            # Тестируем общие бонусы
            total_bonuses = human.get_effective_ability_bonuses(first_subrace)
            print(f"      Общие бонусы: {total_bonuses}")

    # Тестируем эльфа
    elf = Race.get_race_by_name("elf")
    if elf:
        print("\n🧝 Эльф:")
        print(f"   Бонусы: {elf.ability_bonuses}")
        if elf.subraces:
            high_elf = list(elf.subraces.values())[0]
            total_bonuses = elf.get_effective_ability_bonuses(high_elf)
            print(f"   {high_elf.name} общие бонусы: {total_bonuses}")

    print("\n✅ Тест завершен успешно!")


if __name__ == "__main__":
    test_race_loading()
