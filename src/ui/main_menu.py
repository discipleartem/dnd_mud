"""
Главное меню игры.

Простое и понятное меню following KISS principle.
"""

from src.ui.character_creator import CharacterCreator
from src.ui.user_choice import get_user_choice


def show_main_menu() -> None:
    """Отобразить главное меню."""
    while True:
        choice = get_user_choice(
            ["Создать персонажа", "Выход"],
            "D&D MUD - ГЛАВНОЕ МЕНЮ",
            allow_cancel=False
        )
        
        if choice == 1:
            handle_create_character()
        elif choice == 2:
            handle_exit()
            break


def handle_create_character() -> None:
    """Обработать создание персонажа."""
    creator = CharacterCreator()
    character = creator.create_character()
    
    if character:
        print(f"\n✅ Персонаж '{character.name}' успешно создан!")
    else:
        print("\n❌ Создание персонажа отменено.")
    
    input("\nНажмите Enter для продолжения...")


def handle_exit() -> None:
    """Обработать выход."""
    print("\n👋 Спасибо за игру! До встречи!")
