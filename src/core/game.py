"""Основной класс игры."""

from core.config import Config
from interfaces.user_interface import UserInterface
from ui.screen_factory import DefaultScreenFactory
from use_cases.menu_navigation import HandleMenuChoiceUseCase, ShowMenuUseCase


class Game:
    """Главный класс игры."""

    def __init__(self, ui: UserInterface) -> None:
        """Инициализация игры."""
        self.config = Config()
        self.ui = ui
        self.running = False
        self.screen_factory = DefaultScreenFactory()
        self.show_menu = ShowMenuUseCase(ui, self.screen_factory)
        self.handle_choice = HandleMenuChoiceUseCase(ui)

    def run(self) -> None:
        """Запустить игровой цикл."""
        self.running = True

        # Показываем приветственный экран
        self.ui.clear()
        self.ui.print_info("Добро пожаловать в D&D Text MUD!")
        self.ui.get_input("Нажмите Enter для продолжения...")

        # Главный игровой цикл
        while self.running:
            try:
                choice = self.show_menu.execute()
                self.running = self.handle_choice.execute(choice)

            except KeyboardInterrupt:
                self.ui.print_success("\nДо свидания!")
                break
            except Exception as e:
                self.ui.print_error(f"Ошибка: {e}")
