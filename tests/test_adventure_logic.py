#!/usr/bin/env python3
"""
Тест новой логики выбора приключений.
"""

import sys
from pathlib import Path

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.domain.services.game_config import game_config
from src.domain.services.level_resolver import level_resolver


def test_adventure_logic():
    """Тестирует логику выбора приключений."""
    print("=== Тест логики выбора приключений ===\n")
    
    # 1. Проверяем доступные приключения
    all_adventures = game_config.get_available_adventures()
    print("Все доступные приключения:")
    for adv in all_adventures:
        print(f"  - {adv.name} (файл: {adv.file_name}) - уровень: {adv.starting_level} - активно: {adv.is_active}")
    
    # 2. Проверяем приключения кроме учебного
    non_tutorial = game_config.get_non_tutorial_adventures()
    print(f"\nПриключения кроме учебного: {len(non_tutorial)}")
    for adv in non_tutorial:
        print(f"  - {adv.name}")
    
    # 3. Проверяем активное приключение
    active_adventure = game_config.get_active_adventure_info()
    if active_adventure:
        print(f"\nАктивное приключение: {active_adventure.name} (уровень {active_adventure.starting_level})")
    else:
        print("\nНет активного приключения")
    
    # 4. Проверяем уровень
    level_info = level_resolver.get_level_info()
    print(f"\nНачальный уровень: {level_info['final_level']} (источник: {level_info['active_source']})")
    
    # 5. Проверяем логику для UI
    print(f"\n=== Логика для UI ===")
    if non_tutorial:
        print("Есть приключения кроме учебного -> показывать выбор")
    else:
        print("Нет приключений кроме учебного -> использовать настройку по умолчанию")
        if active_adventure and active_adventure.file_name == "tutorial_adventure.yaml":
            print(f"Активное приключение: Начало пути (Tutorial)")
            print(f"Начальный уровень: 1")
        else:
            print(f"Начальный уровень: {level_info['final_level']} (источник: {level_info['active_source']})")


if __name__ == "__main__":
    test_adventure_logic()
    print("\nТест завершен!")
