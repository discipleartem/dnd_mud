"""
D&D MUD - Текстовая многопользовательская ролевая игра в мире Dungeons & Dragons.

Основная точка входа в приложение. Запускает главное меню и управляет
основным игровым циклом.
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Optional

# Добавляем src в Python path для импортов
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.menus.main_menu import show_main_menu, MenuOption
from src.ui.renderer import renderer


def setup_logging() -> None:
    """Настраивает систему логирования."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("dnd_mud.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def show_splash_screen() -> None:
    """Отображает заставку игры."""
    splash_text = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗      ║
║    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║      ║
║       ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║      ║
║       ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║      ║
║       ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████  ║
║       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝ ╚═══╝╚═╝  ╚═╝╚══════╝  ║
║                                                                      ║
║                          D&D MUD Game                                ║
║                                                                      ║
║                      Версия 0.1.0 Alpha                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝    
"""
    
    renderer.clear_screen()
    print(splash_text)
    print()
    print("Нажмите Enter для продолжения...")
    renderer.get_input()


def handle_new_game() -> None:
    """Обрабатывает создание новой игры."""
    renderer.show_info("Запуск новой игры...")
    # Здесь будет логика создания новой игры
    renderer.show_info("Функция новой игры будет реализована в следующей версии.")
    renderer.get_input("Нажмите Enter для возврата в главное меню...")


def handle_load_game() -> None:
    """Обрабатывает загрузку сохраненной игры."""
    renderer.show_info("Загрузка игры...")
    # Здесь будет логика загрузки игры
    renderer.show_info("Функция загрузки игры будет реализована в следующей версии.")
    renderer.get_input("Нажмите Enter для возврата в главное меню...")


def handle_settings() -> None:
    """Обрабатывает настройки игры."""
    renderer.show_info("Открытие настроек...")
    # Здесь будет логика настроек
    renderer.show_info("Функция настроек будет реализована в следующей версии.")
    renderer.get_input("Нажмите Enter для возврата в главное меню...")


def main() -> int:
    """Основная функция приложения."""
    try:
        # Настраиваем логирование
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("Запуск D&D MUD игры")
        
        # Отображаем заставку
        show_splash_screen()
        
        # Основной игровой цикл
        while True:
            try:
                # Показываем главное меню и получаем выбор пользователя
                choice = show_main_menu()
                
                if choice == MenuOption.NEW_GAME:
                    handle_new_game()
                
                elif choice == MenuOption.LOAD_GAME:
                    handle_load_game()
                
                elif choice == MenuOption.SETTINGS:
                    handle_settings()
                
                elif choice == MenuOption.EXIT:
                    renderer.show_success("Спасибо за игру! До встречи!")
                    logger.info("Пользователь вышел из игры")
                    break
                
            except KeyboardInterrupt:
                # Обработка Ctrl+C
                renderer.show_info("\nПрерывание игры...")
                confirm = renderer.get_input("Вы уверены, что хотите выйти? (д/н): ").lower()
                if confirm in ['д', 'y', 'yes']:
                    renderer.show_success("До встречи!")
                    logger.info("Пользователь прервал игру")
                    break
                else:
                    continue
            
            except Exception as e:
                logger.error(f"Ошибка в игровом цикле: {e}")
                renderer.show_error(f"Произошла ошибка: {e}")
                renderer.get_input("Нажмите Enter для продолжения...")
        
        return 0
        
    except Exception as e:
        # Критическая ошибка приложения
        print(f"Критическая ошибка при запуске игры: {e}")
        logging.critical(f"Критическая ошибка: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())