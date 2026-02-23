#!/usr/bin/env python3
"""Тестовый скрипт для проверки загрузки рас из YAML."""

import sys
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.entities.race import Race


def test_race_loading():
    """Тест загрузки рас."""
    print("🧪 Тестируем загрузку рас из YAML...\n")
    
    # Загружаем все расы
    races = Race.load_from_yaml()
    print(f"📊 Загружено рас: {len(races)}")
    
    # Показываем информацию о каждой расе
    for race_id, race in races.items():
        print(f"\n🎭 Раса: {race.name} (ID: {race_id})")
        print(f"   Описание: {race.description}")
        print(f"   Бонусы: {race.ability_bonuses_description}")
        print(f"   Размер: {race.size}, Скорость: {race.speed}")
        print(f"   Языки: {', '.join(race.languages)}")
        print(f"   Черты: {len(race.features)}")
        print(f"   Подрасы: {len(race.subraces)}")
        
        # Показываем подрасы
        for subrace_id, subrace in race.subraces.items():
            print(f"     🔸 {subrace.name} - {subrace.ability_bonuses_description}")
    
    # Тестируем получение конкретной расы
    print("\n" + "="*50)
    print("🔍 Тестируем получение конкретной расы:")
    
    human = Race.get_race("human")
    if human:
        print(f"\n👤 Человек:")
        print(f"   Бонусы характеристик: {human.ability_bonuses}")
        print(f"   Черты: {[f.name for f in human.features]}")
        
        # Тестируем подрасу
        variant_human = human.get_subrace("variant_human")
        if variant_human:
            print(f"\n   🔸 Вариантный человек:")
            print(f"      Черты: {[f.name for f in variant_human.features]}")
            
            # Тестируем общие бонусы
            total_bonuses = human.get_total_ability_bonuses("variant_human")
            print(f"      Общие бонусы: {total_bonuses}")
    
    # Тестируем эльфа
    elf = Race.get_race("elf")
    if elf:
        print(f"\n🧝 Эльф:")
        print(f"   Бонусы: {elf.ability_bonuses}")
        high_elf = elf.get_subrace("high_elf")
        if high_elf:
            total_bonuses = elf.get_total_ability_bonuses("high_elf")
            print(f"   Высший эльф общие бонусы: {total_bonuses}")
    
    print("\n✅ Тест завершен успешно!")


if __name__ == "__main__":
    test_race_loading()