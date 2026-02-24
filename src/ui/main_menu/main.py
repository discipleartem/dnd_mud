"""Главное меню D&D MUD."""

from collections.abc import Callable
from typing import Final

from i18n import t
from src.ui.entities.character import Character
from src.ui.main_menu.load_game import load_game
from src.ui.main_menu.new_game import new_game
from src.ui.main_menu.settings import settings

# Обработчики пунктов меню
MENU_HANDLERS: Final[dict[int, Callable[[], None]]] = {
    2: load_game,
    3: settings,
}

# Обработчики которые возвращают Character
CHARACTER_HANDLERS: Final[dict[int, Callable[[], Character]]] = {
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
    if not 1 <= choice_num <= max_choice:
        print(t("menu.errors.out_of_range", max=max_choice))
        return False

    return True


def _handle_menu_choice(choice_num: int) -> bool:
    """Обработать выбор пункта меню.

    Args:
        choice_num: Номер выбранного пункта.

    Returns:
        True если нужно выйти из меню, иначе False.
    """
    if choice_num in MENU_HANDLERS:
        MENU_HANDLERS[choice_num]()
        return False

    if choice_num == 4:  # Выход
        print(t("menu.goodbye"))
        return True

    return False


def show_main_menu() -> None:
    """Показать главное меню."""
    while True:
        _show_menu_header()

        # Получаем список пунктов меню
        menu_items = t("menu.items")

        # Вывод пунктов меню с нумерацией
        for i, item in enumerate(menu_items, 1):
            print(f"{i}. {item}")

        print("=" * 40)

        # Получение и валидация выбора пользователя
        choice = input(t("menu.prompt")).strip()

        if not _is_valid_choice(choice, len(menu_items)):
            input(t("main.welcome.press_enter"))
            continue

        choice_num = int(choice)

        # Обработка выбора
        if _handle_menu_choice(choice_num):
            break

        # После возврата из подменю - пауза перед показом главного меню
        input(t("menu.continue"))
