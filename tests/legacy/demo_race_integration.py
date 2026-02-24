#!/usr/bin/env python3
"""Пример использования Race в основном приложении."""

import sys
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.entities.race import Race


def demonstrate_race_usage():
    """Демонстрация использования рас в игре."""
    print("🎮 D&D MUD - Демонстрация работы с расами\n")

    # Загружаем все доступные расы
    races = Race.load_from_yaml()

    # Показываем меню выбора расы
    print("📋 Доступные расы:")
    race_list = list(races.keys())
    for i, race_id in enumerate(race_list, 1):
        race = races[race_id]
        print(f"{i}. {race.name} - {race.description[:50]}...")

    # Симуляция выбора расы (для примера выберем эльфа)
    selected_race_id = "elf"
    selected_race = races[selected_race_id]

    print(f"\n🎯 Выбрана раса: {selected_race.name}")
    print(f"📝 Описание: {selected_race.description}")
    print(
        f"💪 Бонусы характеристик: {selected_race.ability_bonuses_description}"
    )
    print(f"📏 Размер: {selected_race.size}")
    print(f"🏃 Скорость: {selected_race.speed} футов")
    print(f"🗣️ Языки: {', '.join(selected_race.languages)}")

    # Показываем черты расы
    print("\n✨ Черты расы:")
    for feature in selected_race.features:
        print(f"  • {feature.name}: {feature.description}")

    # Показываем доступные подрасы
    if selected_race.subraces:
        print("\n🔸 Доступные подрасы:")
        for _subrace_id, subrace in selected_race.subraces.items():
            print(f"  • {subrace.name}: {subrace.ability_bonuses_description}")

        # Симуляция выбора подрасы
        selected_subrace_id = "high_elf"
        selected_subrace = selected_race.get_subrace(selected_subrace_id)

        if selected_subrace:
            print(f"\n🎯 Выбрана подраса: {selected_subrace.name}")

            # Показываем общие бонусы
            total_bonuses = selected_race.get_total_ability_bonuses(
                selected_subrace_id
            )
            print("💪 Общие бонусы характеристик:")
            for ability, bonus in total_bonuses.items():
                print(f"  • {ability}: +{bonus}")

            # Показываем дополнительные черты подрасы
            if selected_subrace.features:
                print("\n✨ Дополнительные черты подрасы:")
                for feature in selected_subrace.features:
                    print(f"  • {feature.name}: {feature.description}")

    print(f"\n🎮 Раса {selected_race.name} готова к использованию в игре!")


if __name__ == "__main__":
    demonstrate_race_usage()
