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

from src.infrastructure.ui.menus.main_menu import show_main_menu, MenuOption
from src.infrastructure.ui.renderer import renderer
from src.infrastructure.ui.input_handler import input_handler
from src.infrastructure.ui.menus.character_creation import CharacterCreationController
from src.adapters.repositories.character_repository import CharacterManager

# Инициализация локализации
from src.adapters.gateways.localization.loader import localization as localization_loader
from src.adapters.gateways.localization_adapter import LocalizationAdapter
from src.domain.interfaces.localization import set_localization_service

# Устанавливаем адаптер локализации для домена
localization_adapter = LocalizationAdapter(localization_loader)
set_localization_service(localization_adapter)


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


def display_character_info(character) -> None:
    """Отображает информацию о персонаже."""
    print(f"\n=== {character.name} ===")
    print(f"Раса: {character.race.name}")
    print(f"Класс: {character.character_class.name}")
    print(f"Уровень: {character.level}")
    print(f"HP: {character.hp_current}/{character.hp_max}")
    print(f"AC: {character.ac}")
    if hasattr(character, 'gold'):
        print(f"Золото: {character.gold}")
    
    print(f"\nХарактеристики:")
    modifiers = character.get_all_modifiers()
    for attr_name in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
        from src.domain.value_objects.attributes import StandardAttributes
        attr_info = StandardAttributes.get_attribute(attr_name)
        value = getattr(character, attr_name).value
        modifier = modifiers[attr_name]
        try:
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            print(f"  {attr_info.short_name}: {value} ({mod_str})")
        except TypeError:
            print(f"  {attr_info.short_name}: {value} (недоступно)")
def handle_new_game() -> None:
    """Обрабатывает создание новой игры."""
    renderer.clear_screen()
    renderer.render_title("Новая игра")
    
    character_controller = CharacterCreationController(input_handler, renderer)
    character = character_controller.create_character()
    
    if character:
        manager = CharacterManager.get_instance()
        if manager.save_character(character):
            renderer.show_success(f"Персонаж {character.name} успешно создан и сохранен!")
            display_character_info(character)
        else:
            renderer.show_error("Ошибка при сохранении персонажа")
    else:
        renderer.show_info("Создание персонажа отменено")
    
    input_handler.wait_for_enter()


def handle_load_game() -> None:
    """Обрабатывает загрузку сохраненной игры."""
    renderer.clear_screen()
    renderer.render_title("Загрузка персонажа")
    
    manager = CharacterManager.get_instance()
    characters = manager.list_characters()
    
    if not characters:
        renderer.show_info("Сохраненные персонажи не найдены")
        input_handler.wait_for_enter()
        return
    
    print("\nСохраненные персонажи:")
    for i, filename in enumerate(characters, 1):
        info = manager.get_character_info(filename)
        if info:
            print(f"{i}. {info['name']} - {info['race']} {info['class']} {info['level']} уровня")
    
    choice = input_handler.get_int(
        "\nВыберите персонажа для загрузки (0 для отмены): ",
        min_value=0,
        max_value=len(characters)
    )
    
    if choice == 0:
        return
    
    selected_filename = characters[choice - 1]
    character = manager.load_character(selected_filename)
    
    if character:
        renderer.show_success(f"Персонаж {character.name} успешно загружен!")
        display_character_info(character)
        renderer.show_info("\n(Здесь начнется игра с загруженным персонажем)")
    else:
        renderer.show_error("Ошибка при загрузке персонажа")
    
    input_handler.wait_for_enter()


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