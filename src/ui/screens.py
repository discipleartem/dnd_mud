"""Экраны игры."""

from core.constants import ASCIIArt, GameConstants
from ui.base_screen import BaseScreen


class WelcomeScreen(BaseScreen):
    """Экран приветствия."""

    def show(self) -> None:
        """Показать экран приветствия."""
        self.ui.clear()
        self.ui.print_title(ASCIIArt.WELCOME_SCREEN)
        self.ui.print_separator()
        self.ui.print_info("нажмите Enter для продолжения...")
        self.ui.get_input()


class MainMenuScreen(BaseScreen):
    """Экран главного меню."""

    def show(self) -> int:
        """Показать главное меню и вернуть выбор."""
        self.ui.clear()
        self.ui.print_title(GameConstants.MENU_TITLE)
        self.ui.print_separator()
        self._show_menu_items(GameConstants.MENU_ITEMS)
        self.ui.print_separator()

        return self.ui.get_int_input(
            "Ваш выбор: ", 1, len(GameConstants.MENU_ITEMS)
        )
