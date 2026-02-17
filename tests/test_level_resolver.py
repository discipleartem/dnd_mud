#!/usr/bin/env python3
"""
Тестирование системы определения начального уровня.
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.domain.services.level_resolver import level_resolver


def test_level_resolver():
    """Тестируем резолвер уровней."""
    print("=== Тестирование системы определения начального уровня ===\n")
    
    # Получаем информацию об определении уровня
    info = level_resolver.get_level_info()
    
    print(f"Финальный уровень: {info['final_level']}")
    print(f"Активный источник: {info['active_source']}")
    
    print("\nВсе источники (по приоритету):")
    for source in info['all_sources']:
        status = "✓ Активен" if source['is_active'] else "○ Не используется"
        print(f"  {source['priority']}. {source['name']}: уровень {source['level']} {status}")
    
    print(f"\nИтоговый начальный уровень: {level_resolver.get_starting_level()}")


if __name__ == "__main__":
    test_level_resolver()
