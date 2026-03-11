"""Простой консольный адаптер для приветственного экрана.

Следует принципам KISS и YAGNI.
Простое отображение с цветовым форматированием.
"""

import os
from typing import Final

from colorama import Fore, Style, init

from ..welcome_dto import WelcomeScreenResponse

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


class WelcomeScreenAdapter:
    """Простой консольный адаптер.

    Следует принципу KISS - просто и понятно.
    Минимум зависимостей, но с цветовым форматированием.
    """

    def display(self, response: WelcomeScreenResponse) -> None:
        """Отобразить приветственный экран.

        Args:
            response: Данные для отображения
        """
        # Очищаем экран
        self.clear_screen()

        # Отображаем содержимое
        self._display_content(response)

    def clear_screen(self) -> None:
        """Очистить экран."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _display_content(self, response: WelcomeScreenResponse) -> None:
        """Отобразить содержимое приветственного экрана.

        Args:
            response: Данные для отображения
        """
        # ASCII-арт (если есть)
        if response.ascii_art:
            print(f"{COLOR_ASCII_ART}{response.ascii_art}{Style.RESET_ALL}")
            print()

        # Заголовок
        print(f"{COLOR_TITLE}{response.title}{Style.RESET_ALL}")
        print()

        # Подзаголовок
        if response.subtitle:
            print(f"{COLOR_SUBTITLE}{response.subtitle}{Style.RESET_ALL}")
            print()

        # Описание
        if response.description:
            print(f"{COLOR_DESCRIPTION}{response.description}{Style.RESET_ALL}")
            print()

        # Разделитель
        print(f"{COLOR_SEPARATOR}{'=' * SEPARATOR_LENGTH}{Style.RESET_ALL}")
        print()

        # Текст для продолжения
        if response.press_enter_text:
            print(f"{COLOR_PRESS_ENTER}{response.press_enter_text}{Style.RESET_ALL}")

        # Ждем ввода
        input()
