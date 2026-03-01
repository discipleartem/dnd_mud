"""Консольный интерфейс с цветовой схемой."""

from typing import Final

from core.constants import GameConstants
from interfaces.user_interface import UserInterface
from ui.colors import ANSI_RESET, FALLBACK_COLOR_MAP, ColorName


class Console(UserInterface):
    """Класс для работы с консольным выводом.
    
    Реализует UserInterface с поддержкой цветов.
    Следует принципу KISS - простая работа с цветами.
    """

    def __init__(self) -> None:
        """Инициализация консоли."""
        self._colorama = self._init_colorama()

    def _init_colorama(self) -> object | None:
        """Инициализировать colorama если доступен.
        
        Returns:
            Объект colorama или None если недоступен
        """
        try:
            import colorama
            colorama.init()
            return colorama
        except ImportError:
            return None

    def clear(self) -> None:
        """Очистить экран."""
        print("\033[2J\033[H", end="")

    def _get_color_code(self, color_name: str) -> str:
        """Получить код цвета.
        
        Args:
            color_name: Название цвета
            
        Returns:
            Код цвета или пустая строка
        """
        if self._colorama is None:
            return FALLBACK_COLOR_MAP.get(color_name, "")
        
        if not hasattr(self._colorama, 'Fore'):
            return ""
            
        # Простая карта цветов (KISS)
        color_map: Final[dict[str, str]] = {
            ColorName.RED: self._colorama.Fore.RED,
            ColorName.GREEN: self._colorama.Fore.GREEN,
            ColorName.CYAN: self._colorama.Fore.CYAN,
            ColorName.WHITE: self._colorama.Fore.WHITE,
            ColorName.BLUE: self._colorama.Fore.BLUE,
        }
        return color_map.get(color_name, "")

    def _get_reset_code(self) -> str:
        """Получить код сброса цвета.
        
        Returns:
            Код сброса цвета
        """
        if self._colorama is None or not hasattr(self._colorama, 'Style'):
            return ANSI_RESET
        return self._colorama.Style.RESET_ALL

    def _print_with_color(self, text: str, color_name: str = "") -> None:
        """Печатает текст с цветом.
        
        Args:
            text: Текст для вывода
            color_name: Название цвета
        """
        if not color_name:
            print(text)
            return

        color = self._get_color_code(color_name)
        reset = self._get_reset_code()
        print(f"{color}{text}{reset}" if color else text)

    def print_info(self, text: str) -> None:
        """Напечатать информационное сообщение.
        
        Args:
            text: Текст сообщения
        """
        self._print_with_color(text, ColorName.CYAN)

    def print_error(self, text: str) -> None:
        """Напечатать ошибку.
        
        Args:
            text: Текст ошибки
        """
        self._print_with_color(text, ColorName.RED)

    def print_success(self, text: str) -> None:
        """Напечатать успешное сообщение.
        
        Args:
            text: Текст успешного сообщения
        """
        self._print_with_color(text, ColorName.GREEN)

    def print_title(self, text: str) -> None:
        """Напечатать заголовок.
        
        Args:
            text: Текст заголовка
        """
        if self._colorama is None or not hasattr(self._colorama, 'Style'):
            self._print_with_color(text, ColorName.CYAN)
        else:
            bright_text = f"{self._colorama.Style.BRIGHT}{text}"
            self._print_with_color(bright_text, ColorName.CYAN)

    def print_menu_item(self, number: int, text: str) -> None:
        """Напечатать пункт меню.
        
        Args:
            number: Номер пункта меню
            text: Текст пункта меню
        """
        self._print_with_color(f"{number}. {text}", ColorName.WHITE)

    def print_separator(self, length: int = 50, char: str = "=") -> None:
        """Напечатать разделитель.
        
        Args:
            length: Длина разделителя
            char: Символ разделителя
        """
        separator = char * length
        self._print_with_color(separator, ColorName.BLUE)

    def get_input(self, prompt: str = "") -> str:
        """Получить ввод пользователя.
        
        Args:
            prompt: Приглашение для ввода
            
        Returns:
            Строка введенная пользователем
        """
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            raise KeyboardInterrupt() from None
        except EOFError:
            return ""

    def get_int_input(self, prompt: str = "", min_val: int | None = None,
                   max_val: int | None = None) -> int:
        """Получить числовой ввод с валидацией.
        
        Args:
            prompt: Приглашение для ввода
            min_val: Минимальное допустимое значение
            max_val: Максимальное допустимое значение
            
        Returns:
            Целое число введенное пользователем
            
        Raises:
            ValueError: При некорректном вводе
        """
        while True:
            try:
                value = int(self.get_input(prompt))
                if self._is_valid_range(value, min_val, max_val):
                    return value
            except ValueError:
                self.print_error("Пожалуйста, введите целое число.")
            except KeyboardInterrupt:
                raise KeyboardInterrupt() from None

    def _is_valid_range(self, value: int, min_val: int | None,
                        max_val: int | None) -> bool:
        """Проверить, что значение в допустимом диапазоне.
        
        Args:
            value: Проверяемое значение
            min_val: Минимальное допустимое значение
            max_val: Максимальное допустимое значение
            
        Returns:
            True если значение в диапазоне
        """
        if min_val is not None and value < min_val:
            self.print_error(f"Значение должно быть не менее {min_val}")
            return False
        if max_val is not None and value > max_val:
            self.print_error(f"Значение должно быть не более {max_val}")
            return False
        return True
