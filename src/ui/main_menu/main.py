"""Главное меню D&D MUD.

Предоставляет основной интерфейс для навигации
по функциям приложения.
"""

from collections.abc import Callable
from typing import Final

from i18n import t
from src.ui.adapters.updated_adapters import Character as UICharacter
from src.ui.main_menu.load_game import load_game
from src.ui.main_menu.new_game import new_game
from src.ui.main_menu.settings import settings

# Обработчики пунктов меню
MENU_HANDLERS: Final[dict[int, Callable[[], None]]] = {
    2: load_game,
    3: settings,
}

# Обработчики которые возвращают Character
CHARACTER_HANDLERS: Final[dict[int, Callable[[], UICharacter]]] = {
    1: new_game,
}


def _show_menu_header() -> None:
    """Показать заголовок меню."""
    print("\n" + "=" * 40)
    menu_title = t("menu.title")
    title_str = menu_title if isinstance(menu_title, str) else str(menu_title)
    print(title_str.center(40))
    print("=" * 40)


def _is_valid_choice(choice: str, max_choice: int) -> bool:
    """Проверить валидность выбора пользователя.

    Args:
        choice: Выбор пользователя.
        max_choice: Максимально допустимый номер.

    Returns:
        True если выбор валиден, иначе False.
    """
    if not choice.isdigit():
        print(t("menu.errors.invalid_number"))
        return False

    choice_num = int(choice)
    if choice_num < 1:
        print(t("menu.errors.invalid_range"))
        return False

    if choice_num > max_choice:
        print(t("menu.errors.invalid_range"))
        return False

    return True


def main_menu() -> None:
    """Главное меню приложения."""
    import sys

    while True:
        _show_menu_header()
        menu_items = t("menu.items")
        if isinstance(menu_items, str):
            menu_items = [menu_items]
        _display_menu_items(menu_items)

        choice = input(t("menu.prompt")).strip()

        if choice.lower() == "exit":
            print(t("menu.goodbye"))
            sys.exit(0)

        if not _is_valid_choice(choice, len(menu_items)):
            input(t("main.welcome.press_enter"))
            continue

        choice_num = int(choice)

        if _handle_character_creation(choice_num):
            sys.exit(0)

        if _handle_regular_menu(choice_num):
            input(t("menu.continue"))
            continue

        if choice_num == 4:  # Выход
            print(t("menu.goodbye"))
            sys.exit(0)

        input(t("menu.continue"))


def _display_menu_items(menu_items: list[str]) -> None:
    """Отобразить пункты меню."""
    for i, item in enumerate(menu_items, 1):
        print(f"{i}. {item}")
    print("=" * 40)


def _handle_character_creation(choice_num: int) -> bool:
    """Обработать создание персонажа.

    Returns:
        True если был создан персонаж
    """
    if choice_num in CHARACTER_HANDLERS:
        CHARACTER_HANDLERS[choice_num]()
        return True
    return False


def _handle_regular_menu(choice_num: int) -> bool:
    """Обработать обычные пункты меню.

    Returns:
        True если был обработан пункт меню
    """
    if choice_num in MENU_HANDLERS:
        MENU_HANDLERS[choice_num]()
        return True
    return False


def show_main_menu() -> None:
    """Показать главное меню."""
    main_menu()
