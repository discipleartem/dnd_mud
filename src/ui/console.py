"""Консольный интерфейс.

Следует Zen Python:
- Простое лучше сложного
- Явное лучше неявного
- Читаемость важна
"""


from core.constants import (
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_WHITE,
    PRESS_ENTER,
    SEPARATOR_CHAR,
    SEPARATOR_LENGTH,
)
from interfaces.i18n_api import I18nTranslator
from interfaces.user_interface import UserInterface


class Console(UserInterface):
    """Простой консольный интерфейс."""

    def __init__(self, translator: I18nTranslator | None = None) -> None:
        """Инициализация консоли."""
        super().__init__(translator)
        self._has_colorama = self._init_colorama()
        self._colors = self._get_color_map() if self._has_colorama else {}

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

    def _get_color_map(self) -> dict[str, str]:
        """Получить словарь цветов colorama."""
        import colorama
        return {
            COLOR_RED: getattr(colorama.Fore, "RED", ""),
            COLOR_GREEN: getattr(colorama.Fore, "GREEN", ""),
            COLOR_CYAN: getattr(colorama.Fore, "CYAN", ""),
            COLOR_WHITE: getattr(colorama.Fore, "WHITE", ""),
        }

    def _print_with_color(self, text: str, color_name: str = "") -> None:
        """Напечатать текст с цветом."""
        if not self._has_colorama or not color_name:
            print(text)
            return

        import colorama
        reset = getattr(colorama.Style, "RESET_ALL", "")
        color = self._colors.get(color_name.lower(), "")
        print(f"{color}{text}{reset}" if color else text)

    def print_info(self, text: str) -> None:
        """Напечатать информационное сообщение."""
        self._print_with_color(text, COLOR_CYAN)

    def print_error(self, text: str) -> None:
        """Напечатать ошибку."""
        self._print_with_color(text, COLOR_RED)

    def print_success(self, text: str) -> None:
        """Напечатать успешное сообщение."""
        self._print_with_color(text, COLOR_GREEN)

    def print_title(self, text: str) -> None:
        """Напечатать заголовок."""
        if self._has_colorama:
            import colorama
            bright_text = f"{getattr(colorama.Style, 'BRIGHT', '')}{text}"
            self._print_with_color(bright_text, COLOR_CYAN)
        else:
            self._print_with_color(text, COLOR_CYAN)

    def print_menu_item(self, number: int, text: str) -> None:
        """Напечатать пункт меню."""
        self._print_with_color(f"{number}. {text}", COLOR_WHITE)

    def print_separator(
        self, length: int = SEPARATOR_LENGTH, char: str = SEPARATOR_CHAR
    ) -> None:
        """Напечатать разделитель."""
        separator = char * length
        self._print_with_color(separator, COLOR_CYAN)

    def show_message_and_wait(self, message: str) -> None:
        """Показать сообщение и ждать ввода (DRY - общий паттерн)."""
        self.print_info(message)
        # Используем локализованную строку или fallback
        prompt = self.t("press_enter") if self._translator else PRESS_ENTER
        self.get_input(prompt)

    def get_input(self, prompt: str = "") -> str:
        """Получить ввод пользователя."""
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            raise KeyboardInterrupt() from None
        except EOFError:
            return ""

    def get_int_input(
        self,
        prompt: str = "",
        min_val: int | None = None,
        max_val: int | None = None,
    ) -> int:
        """Получить числовой ввод с валидацией (KISS - просто)."""
        while True:
            try:
                value = int(self.get_input(prompt))
                if self._is_valid_range(value, min_val, max_val):
                    return value

                self._show_range_error(min_val, max_val)

            except ValueError:
                error_msg = self.t("errors.number_expected") if self._translator else "Пожалуйста, введите целое число."
                self.print_error(error_msg)
            except KeyboardInterrupt:
                raise KeyboardInterrupt() from None

    def _is_valid_range(
        self, value: int, min_val: int | None, max_val: int | None
    ) -> bool:
        """Проверить диапазон значения."""
        return (
            (min_val is None or value >= min_val) and
            (max_val is None or value <= max_val)
        )

    def _show_range_error(
        self, min_val: int | None, max_val: int | None
    ) -> None:
        """Показать ошибку диапазона."""
        if min_val is not None and max_val is not None:
            error_msg = self.t("errors.range_error", min=min_val, max=max_val) if self._translator else f"Значение должно быть от {min_val} до {max_val}"
            self.print_error(error_msg)
        elif min_val is not None:
            error_msg = self.t("errors.range_error", min=min_val) if self._translator else f"Значение должно быть не менее {min_val}"
            self.print_error(error_msg)
        else:
            error_msg = self.t("errors.range_error", max=max_val) if self._translator else f"Значение должно быть не более {max_val}"
            self.print_error(error_msg)
