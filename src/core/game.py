"""Основной класс игры.

Следует принципам:
- KISS: Максимально простой класс
- SRP: Только координация компонентов
- DIP: Зависит от абстракций
"""

from core.config import Config
from interfaces.user_interface import UserInterface
from use_cases.game import GameUseCase


class Game:
    """Главный класс игры.

    Максимально простой координатор.
    Вся логика вынесена в Use Cases.
    """

    def __init__(self, ui: UserInterface) -> None:
        """Инициализация игры."""
        self.config = Config()
        self.ui = ui
        self.running = False
        self.game_use_case = GameUseCase(ui)

    def run(self) -> None:
        """Запустить игровой цикл."""
        self.running = True

        # Показываем приветственный экран
        self.ui.clear()
        self.ui.print_info("Добро пожаловать в D&D Text MUD!")
        self.ui.get_input("Нажмите Enter для продолжения...")

        # Главный игровой цикл (KISS - максимально простой)
        while self.running:
            try:
                self.running = self.game_use_case.show_and_handle_menu()

            except KeyboardInterrupt:
                self.ui.print_success("\nДо свидания!")
                break
            except Exception as e:
                self.ui.print_error(f"Ошибка: {e}")
                self.ui.get_input("Нажмите Enter для продолжения...")
