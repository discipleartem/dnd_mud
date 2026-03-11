"""Консольный адаптер для приветственного экрана.

Следует Clean Architecture - оркестрация UI компонента.
Содержит только координацию, без бизнес-логики.
"""

from src.frameworks.drivers.ui.console_welcome_ui import ConsoleWelcomeUI


class ConsoleWelcomeScreenAdapter:
    """Консольный адаптер приветственного экрана.

    Следует Clean Architecture - координирует работу
    UI компонента для отображения данных.
    """

    def __init__(self) -> None:
        """Инициализация адаптера."""
        self._ui = ConsoleWelcomeUI()

    def display(self, response_data: dict) -> None:
        """Отобразить приветственный экран.

        Args:
            response_data: Данные для отображения от контроллера
        """
        # Отображение через UI
        self._ui.display_welcome_screen(response_data)
