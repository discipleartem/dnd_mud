"""Основной Use Case игры.

Следует принципам:
- KISS: Максимально простой класс
- SRP: Одна ответственность - управление меню
- YAGNI: Только необходимая функциональность
- DRY: Использует общие константы
"""

from core.constants import (
    CHARACTER_CREATED,
    CHARACTER_NAME_PROMPT,
    ERROR_CREATING_CHARACTER,
    ERROR_EMPTY_NAME,
    MAIN_MENU_TITLE,
    MENU_ITEMS,
    MENU_PROMPT,
    NOT_AVAILABLE,
    THANKS_FOR_PLAYING,
)
from entities.character import Character
from interfaces.user_interface import UserInterface


class GameUseCase:
    """Основной Use Case для управления игрой (KISS - максимально простой)."""

    def __init__(self, ui: UserInterface) -> None:
        """Инициализация Use Case."""
        self.ui = ui
        self._character: Character | None = None
        self._menu_handlers = {
            1: self._create_new_character,
            len(MENU_ITEMS): self._handle_exit,
        }

    def show_and_handle_menu(self) -> bool:
        """Показать меню и обработать выбор (KISS - просто)."""
        self.ui.clear()
        self.ui.print_title(MAIN_MENU_TITLE)
        self.ui.print_separator()

        # Показываем пункты меню
        for number, text in enumerate(MENU_ITEMS, 1):
            self.ui.print_menu_item(number, text)

        self.ui.print_separator()
        choice = self.ui.get_int_input(MENU_PROMPT, 1, len(MENU_ITEMS))

        return self._handle_menu_choice(choice)

    def _handle_menu_choice(self, choice: int) -> bool:
        """Обработать выбор меню (KISS - просто)."""
        handler = self._menu_handlers.get(choice, self._show_not_available)
        return handler()

    def _handle_exit(self) -> bool:
        """Обработать выход из игры."""
        self.ui.print_success(THANKS_FOR_PLAYING)
        return False

    def _show_not_available(self) -> bool:
        """Показать сообщение о недоступности функции."""
        self.ui.show_message_and_wait(NOT_AVAILABLE)
        return True

    def _create_new_character(self) -> bool:
        """Создать нового персонажа (KISS - просто)."""
        try:
            name = self.ui.get_input(CHARACTER_NAME_PROMPT).strip()
            if not name:
                raise ValueError(ERROR_EMPTY_NAME)

            self._character = Character(name=name)

            self.ui.print_success(CHARACTER_CREATED.format(name=name))
            self.ui.print_info(f"{self._character}")
            self.ui.print_info(f"Статус: {self._character.get_status()}")
        except ValueError as e:
            self.ui.print_error(ERROR_CREATING_CHARACTER.format(error=e))

        return True

    def get_current_character(self) -> Character | None:
        """Получить текущего персонажа."""
        return self._character

    def has_active_character(self) -> bool:
        """Проверить, есть ли активный персонаж."""
        return self._character is not None
