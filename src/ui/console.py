"""Консольный интерфейс.

Следует Zen Python:
- Простое лучше сложного
- Явное лучше неявного
- Читаемость важна
"""


from interfaces.user_interface import UserInterface
from ui.colors import (
    ANSI_RESET,
    BLUE,
    CYAN,
    FALLBACK_COLOR_MAP,
    GREEN,
    RED,
    WHITE,
)


class Console(UserInterface):
    """Простой консольный интерфейс с поддержкой цветов.

    Максимально простая реализация без излишеств.
    """

    def __init__(self) -> None:
        """Инициализация консоли."""
        self._has_colorama = self._init_colorama()

    def _init_colorama(self) -> bool:
        """Проверить доступность colorama."""
        try:
            import colorama
            colorama.init()
            return True
        except ImportError:
            return False

    def clear(self) -> None:
        """Очистить экран."""
        print("\033[2J\033[H", end="")

    def _get_color_code(self, color_name: str) -> str:
        """Получить код цвета."""
        if not self._has_colorama:
            return FALLBACK_COLOR_MAP.get(color_name, "") or ""

        import colorama
        color_map = {
            RED: str(getattr(colorama.Fore, 'RED', '')),
            GREEN: str(getattr(colorama.Fore, 'GREEN', '')),
            CYAN: str(getattr(colorama.Fore, 'CYAN', '')),
            WHITE: str(getattr(colorama.Fore, 'WHITE', '')),
            BLUE: str(getattr(colorama.Fore, 'BLUE', '')),
        }
        return color_map.get(color_name, "") or ""

    def _get_reset_code(self) -> str:
        """Получить код сброса цвета."""
        if not self._has_colorama:
            return ANSI_RESET  # type: ignore

        import colorama
        reset_code = getattr(colorama.Style, 'RESET_ALL', ANSI_RESET)
        return str(reset_code)

    def _print_with_color(self, text: str, color_name: str = "") -> None:
        """Напечатать текст с цветом."""
        if not color_name:
            print(text)
            return

        color = self._get_color_code(color_name)
        reset = self._get_reset_code()
        print(f"{color}{text}{reset}" if color else text)

    def print_info(self, text: str) -> None:
        """Напечатать информационное сообщение."""
        self._print_with_color(text, CYAN)

    def print_error(self, text: str) -> None:
        """Напечатать ошибку."""
        self._print_with_color(text, RED)

    def print_success(self, text: str) -> None:
        """Напечатать успешное сообщение."""
        self._print_with_color(text, GREEN)

    def print_title(self, text: str) -> None:
        """Напечатать заголовок."""
        if self._has_colorama:
            import colorama
            bright_text = f"{str(getattr(colorama.Style, 'BRIGHT', ''))}{text}"
            self._print_with_color(bright_text, CYAN)
        else:
            self._print_with_color(text, CYAN)

    def print_menu_item(self, number: int, text: str) -> None:
        """Напечатать пункт меню."""
        self._print_with_color(f"{number}. {text}", WHITE)

    def print_separator(self, length: int = 50, char: str = "=") -> None:
        """Напечатать разделитель."""
        separator = char * length
        self._print_with_color(separator, BLUE)

    def get_input(self, prompt: str = "") -> str:
        """Получить ввод пользователя."""
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            raise KeyboardInterrupt() from None
        except EOFError:
            return ""

    def get_int_input(self, prompt: str = "", min_val: int | None = None,
                   max_val: int | None = None) -> int:
        """Получить числовой ввод с валидацией."""
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
        """Проверить, что значение в допустимом диапазоне."""
        if min_val is not None and value < min_val:
            self.print_error(f"Значение должно быть не менее {min_val}")
            return False
        if max_val is not None and value > max_val:
            self.print_error(f"Значение должно быть не более {max_val}")
            return False
        return True
