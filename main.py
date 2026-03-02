"""D&D MUD - Текстовая однопользовательская игра.

Структура приложения согласно чистой архитектуре (адаптированной для консоли):

src/
├── models/entities/          # Бизнес-сущности (Character, Race, Class)
├── use_cases/              # Сценарии использования (CreateCharacter, LoadGame)
├── interfaces/             # Интерфейсы внешних зависимостей
├── adapters/               # Адтеры интерфейсов (контроллеры)
├── repositories/           # Реализации репозиториев (файловые)
├── console/               # Консольный интерфейс
└── dtos/                  # DTO для передачи данных

Правила зависимостей:
- Entities → не зависят ни от чего
- Use Cases → зависят только от Entities
- Interface Adapters → зависят от Use Cases и Entities  
- Repositories & Console → зависят от всех внутренних слоев
"""

import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.use_cases.main_menu import MainMenuUseCase
from src.console.main_menu_adapter import MainMenuAdapter


def main():
    """Главная функция приложения."""
    try:
        # Создание Use Case главного меню
        main_menu_use_case = MainMenuUseCase()
        
        # Создание адаптера для консоли
        menu_adapter = MainMenuAdapter(main_menu_use_case)
        
        # Запуск главного меню
        menu_adapter.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 До свидания!")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("Приложение будет закрыто.")


if __name__ == "__main__":
    main()