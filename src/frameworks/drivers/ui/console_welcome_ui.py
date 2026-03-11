"""UI слой для консольного приветственного экрана.

Следует Clean Architecture - содержит только UI логику.
Не зависит от бизнес-логики, только отображение данных.
"""

import os
from typing import Any, Final

from colorama import Fore, Style, init

# Инициализация colorama
init(autoreset=True)

# Явные константы цветов (Zen Python: явное лучше неявного)
COLOR_ASCII_ART: Final[str] = Fore.CYAN
COLOR_TITLE: Final[str] = f"{Fore.YELLOW}{Style.BRIGHT}"
COLOR_SUBTITLE: Final[str] = Fore.GREEN
COLOR_DESCRIPTION: Final[str] = Fore.WHITE
COLOR_SEPARATOR: Final[str] = Fore.BLUE
COLOR_PRESS_ENTER: Final[str] = Fore.CYAN
SEPARATOR_LENGTH: Final[int] = 60


class ConsoleWelcomeUI:
    """UI компонент для отображения приветственного экрана.

    Следует Clean Architecture - только UI логика отображения.
    Не содержит бизнес-правил или преобразований данных.
    """

    def display_welcome_screen(self, display_data: dict[str, Any]) -> None:
        """Отобразить приветственный экран.

        Args:
            display_data: Данные для отображения от адаптера
        """
        # Очищаем экран
        self._clear_screen()

        # Отображаем содержимое
        self._display_content(display_data)

    def _clear_screen(self) -> None:
        """Очистить экран."""
        os.system("cls" if os.name == "nt" else "clear")

    def _display_content(self, display_data: dict[str, Any]) -> None:
        """Отобразить содержимое приветственного экрана.

        Args:
            display_data: Данные для отображения
        """
        # ASCII-арт (если есть)
        if display_data.get("has_ascii_art") and display_data.get("ascii_art"):
            print(
                f"{COLOR_ASCII_ART}{display_data['ascii_art']}{Style.RESET_ALL}"
            )
            print()

        # Заголовок
        title = display_data.get("title", "")
        if title:
            print(f"{COLOR_TITLE}=== {title} ==={Style.RESET_ALL}")
            print()

        # Подзаголовок
        subtitle = display_data.get("subtitle", "")
        if subtitle:
            print(f"{COLOR_SUBTITLE}{subtitle}{Style.RESET_ALL}")
            print()

        # Описание
        description = display_data.get("description", "")
        if description:
            print(f"{COLOR_DESCRIPTION}{description}{Style.RESET_ALL}")
            print()

        # Разделитель
        print(f"{COLOR_SEPARATOR}{'=' * SEPARATOR_LENGTH}{Style.RESET_ALL}")
        print()

        # Текст для продолжения
        press_enter_text = display_data.get("press_enter_text", "")
        if press_enter_text:
            print(f"{COLOR_PRESS_ENTER}{press_enter_text}{Style.RESET_ALL}")

        # Ждем ввода
        input()
