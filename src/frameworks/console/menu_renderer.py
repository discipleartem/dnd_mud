"""Рендерер меню для консоли.

Следует Clean Architecture - Framework Layer для отображения меню.
Использует colorama для цветного вывода.
"""

import os
import sys
from typing import Any

# Импортируем colorama с обработкой ошибок
try:
    import colorama
    from colorama import Back, Fore, Style

    colorama.init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

    # Создаем заглушки
    class Back:  # type: ignore
        RESET = ""
        BLACK = ""
        LIGHTGRAY_EX = ""

    class Fore:  # type: ignore
        RESET = ""
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""
        GRAY = ""

    class Style:  # type: ignore
        RESET_ALL = ""
        BRIGHT = ""
        DIM = ""


class MenuRenderer:
    """Рендерер меню для консольного вывода.

    Следует Clean Architecture - преобразует данные меню
    в консольный вывод с цветовой схемой.
    """

    def __init__(self, use_colors: bool = True) -> None:
        """Инициализация рендерера.

        Args:
            use_colors: Использовать цветовой вывод
        """
        self.use_colors = use_colors and COLORAMA_AVAILABLE
        self.terminal_width = self._get_terminal_width()

    def render_menu(self, context: dict[str, Any]) -> str:
        """Отрендерить меню.

        Args:
            context: Контекст меню для рендеринга

        Returns:
            Готовый текст меню для вывода
        """
        lines = []

        # Очистка экрана
        lines.append(self._clear_screen())

        # Заголовок меню
        title = context.get("title", "Меню")
        lines.append(self._render_title(title))
        lines.append("")

        # Пункты меню
        items = context.get("items", [])
        current_item = context.get("current_item")
        context.get("selectable_items", [])

        for i, item in enumerate(items):
            if not item.is_visible:
                continue

            is_current = current_item and item.id == current_item.id
            is_enabled = item.is_enabled

            line = self._render_menu_item(
                item, bool(is_current), bool(is_enabled), i + 1
            )
            lines.append(line)

        lines.append("")

        # Подсказки по навигации
        if context.get("has_navigation", False):
            lines.append(self._render_help())

        # Дополнительные опции
        help_lines = []
        if context.get("allow_back", True):
            help_lines.append("ESC - Выход")

        if help_lines:
            lines.append(self._render_help(", ".join(help_lines)))

        return "\n".join(lines)

    def render_message(self, message: str, message_type: str = "info") -> str:
        """Отрендерить сообщение.

        Args:
            message: Текст сообщения
            message_type: Тип сообщения (info, error, success, warning)

        Returns:
            Отформатированное сообщение
        """
        if not self.use_colors:
            return message

        colors = {
            "info": Fore.CYAN,
            "error": Fore.RED,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
        }

        color = colors.get(message_type, Fore.WHITE)
        return f"{color}{message}{Style.RESET_ALL}"

    def render_input_prompt(self, prompt: str = "Ваш выбор: ") -> str:
        """Отрендерить приглашение к вводу.

        Args:
            prompt: Текст приглашения

        Returns:
            Отформатированное приглашение
        """
        if self.use_colors:
            return f"{Fore.CYAN}{prompt}{Style.RESET_ALL}"
        return prompt

    def _render_title(self, title: str) -> str:
        """Отрендерить заголовок меню.

        Args:
            title: Заголовок

        Returns:
            Отформатированный заголовок
        """
        if not self.use_colors:
            border = "=" * len(title)
            return f"{border}\n{title}\n{border}"

        title_line = f"{Fore.YELLOW}{Style.BRIGHT}{title}{Style.RESET_ALL}"
        border_line = f"{Fore.YELLOW}{'=' * len(title)}{Style.RESET_ALL}"

        return f"{border_line}\n{title_line}\n{border_line}"

    def _render_menu_item(
        self, item, is_current: bool, is_enabled: bool, index: int
    ) -> str:
        """Отрендерить пункт меню.

        Args:
            item: Пункт меню
            is_current: Текущий ли пункт
            is_enabled: Доступен ли пункт
            index: Порядковый номер

        Returns:
            Отформатированный пункт меню
        """
        # Базовый текст пункта (без описания)
        display_text = item.get_display_text()
        line = f"{index}. {display_text}"

        # Цветовая схема
        if not self.use_colors:
            return line

        if not is_enabled:
            # Недоступный пункт
            return f"{Fore.LIGHTBLACK_EX}{line}{Style.RESET_ALL}"
        else:
            # Обычный пункт (без выделения)
            return f"{Fore.WHITE}{line}{Style.RESET_ALL}"

    def _render_help(self, help_text: str = "Введите номер пункта") -> str:
        """Отрендерить текст помощи.

        Args:
            help_text: Текст помощи

        Returns:
            Отформатированный текст помощи
        """
        if not self.use_colors:
            return f"[{help_text}]"

        return f"{Style.RESET_ALL}[{help_text}]{Style.RESET_ALL}"

    def _clear_screen(self) -> str:
        """Очистить экран.

        Returns:
            ANSI последовательность очистки экрана
        """
        if sys.platform == "win32":
            return "\n" * 50  # Простая очистка для Windows
        else:
            return "\033[2J\033[H"  # ANSI очистка для Unix

    def _get_terminal_width(self) -> int:
        """Получить ширину терминала.

        Returns:
            Ширина терминала в символах
        """
        try:
            return os.get_terminal_size().columns
        except OSError:
            return 80  # Значение по умолчанию

    def update_terminal_size(self) -> None:
        """Обновить информацию о размере терминала."""
        self.terminal_width = self._get_terminal_width()

    def wrap_text(self, text: str, max_width: int | None = None) -> list[str]:
        """Разбить длинный текст на строки.

        Args:
            text: Текст для разбивки
            max_width: Максимальная ширина строки

        Returns:
            Список строк
        """
        if max_width is None:
            max_width = min(self.terminal_width - 4, 79)

        if len(text) <= max_width:
            return [text]

        lines = []
        current_line = ""

        for word in text.split():
            if len(current_line + word) <= max_width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return lines
