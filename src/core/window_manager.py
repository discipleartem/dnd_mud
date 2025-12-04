"""
Window Manager - управление окном терминала.

Отвечает за:
- Определение размера терминала
- Обработку изменения размера
- Автоматический перенос текста
- Проверку минимального размера
"""

import os
import sys
import shutil
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class TerminalSize:
    """Размер терминала."""
    width: int
    height: int

    def is_valid(self, min_width: int = 80, min_height: int = 24) -> bool:
        """Проверка минимального размера."""
        return self.width >= min_width and self.height >= min_height


class WindowManager:
    """
    Singleton класс для управления окном терминала.

    Паттерн: Singleton
    Принцип: SRP - отвечает только за управление окном
    """

    _instance: Optional['WindowManager'] = None

    MIN_WIDTH = 80
    MIN_HEIGHT = 24

    def __new__(cls) -> 'WindowManager':
        """Реализация Singleton паттерна."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Инициализация менеджера окна."""
        if self._initialized:
            return

        self._current_size: Optional[TerminalSize] = None
        self._initialized = True

    def get_terminal_size(self) -> TerminalSize:
        """
        Получение размера терминала.

        Работает в PyInstaller сборках и обычном терминале.

        Returns:
            TerminalSize: текущий размер терминала
        """
        try:
            # Попытка получить размер через shutil (работает в PyInstaller)
            size = shutil.get_terminal_size(fallback=(self.MIN_WIDTH, self.MIN_HEIGHT))
            self._current_size = TerminalSize(width=size.columns, height=size.lines)
        except Exception:
            # Резервный вариант для специфичных окружений
            try:
                # Windows
                if sys.platform == 'win32':
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    h = kernel32.GetStdHandle(-12)
                    csbi = ctypes.create_string_buffer(22)
                    res = kernel32.GetConsoleScreenBufferInfo(h, csbi)
                    if res:
                        import struct
                        (_, _, _, _, _, left, top, right, bottom, _, _) = struct.unpack("hhhhHhhhhhh", csbi.raw)
                        width = right - left + 1
                        height = bottom - top + 1
                        self._current_size = TerminalSize(width=width, height=height)
                    else:
                        self._current_size = TerminalSize(
                            width=self.MIN_WIDTH,
                            height=self.MIN_HEIGHT
                        )
                # Linux/Unix
                else:
                    import fcntl
                    import termios
                    import struct
                    h, w = struct.unpack('hh', fcntl.ioctl(0, termios.TIOCGWINSZ, '1234'))
                    self._current_size = TerminalSize(width=w, height=h)
            except Exception:
                # Финальный fallback
                self._current_size = TerminalSize(
                    width=self.MIN_WIDTH,
                    height=self.MIN_HEIGHT
                )

        return self._current_size

    def check_minimum_size(self) -> Tuple[bool, str]:
        """
        Проверка минимального размера терминала.

        Returns:
            Tuple[bool, str]: (результат проверки, сообщение об ошибке)
        """
        size = self.get_terminal_size()

        if not size.is_valid(self.MIN_WIDTH, self.MIN_HEIGHT):
            message = (
                f"Размер терминала {size.width}x{size.height} слишком мал.\n"
                f"Минимальный размер: {self.MIN_WIDTH}x{self.MIN_HEIGHT}.\n"
                f"Пожалуйста, увеличьте окно терминала."
            )
            return False, message

        return True, ""

    def wrap_text(self, text: str, width: Optional[int] = None,
                  indent: int = 0) -> List[str]:
        """
        Автоматический перенос текста по ширине.

        Args:
            text: текст для переноса
            width: ширина (по умолчанию - ширина терминала)
            indent: отступ слева

        Returns:
            List[str]: список строк с переносами
        """
        if width is None:
            size = self.get_terminal_size()
            width = size.width - indent - 2  # -2 для рамок

        # Разбиваем по существующим переносам строк
        paragraphs = text.split('\n')
        wrapped_lines = []

        for paragraph in paragraphs:
            if not paragraph.strip():
                wrapped_lines.append('')
                continue

            # Разбиваем на слова
            words = paragraph.split()
            current_line = ' ' * indent

            for word in words:
                # Если слово слишком длинное, разбиваем его
                if len(word) > width:
                    if current_line.strip():
                        wrapped_lines.append(current_line)
                        current_line = ' ' * indent

                    # Разбиваем длинное слово
                    for i in range(0, len(word), width - indent):
                        wrapped_lines.append(' ' * indent + word[i:i + width - indent])
                    continue

                # Проверяем, поместится ли слово в текущей строке
                test_line = current_line + (' ' if current_line.strip() else '') + word

                if len(test_line) <= width:
                    current_line = test_line
                else:
                    # Начинаем новую строку
                    wrapped_lines.append(current_line)
                    current_line = ' ' * indent + word

            # Добавляем последнюю строку параграфа
            if current_line.strip():
                wrapped_lines.append(current_line)

        return wrapped_lines

    def clear_screen(self) -> None:
        """Очистка экрана терминала."""
        os.system('cls' if sys.platform == 'win32' else 'clear')

    def center_text(self, text: str, width: Optional[int] = None) -> str:
        """
        Центрирование текста.

        Args:
            text: текст для центрирования
            width: ширина (по умолчанию - ширина терминала)

        Returns:
            str: отцентрированный текст
        """
        if width is None:
            size = self.get_terminal_size()
            width = size.width

        text_length = len(text)
        if text_length >= width:
            return text

        padding = (width - text_length) // 2
        return ' ' * padding + text

    def get_content_width(self, border: int = 2) -> int:
        """
        Получение ширины для контента (с учётом рамок).

        Args:
            border: ширина рамок с обеих сторон

        Returns:
            int: доступная ширина для контента
        """
        size = self.get_terminal_size()
        return max(size.width - border * 2, 40)  # минимум 40 символов

    def get_content_height(self, border: int = 2) -> int:
        """
        Получение высоты для контента (с учётом рамок).

        Args:
            border: высота рамок сверху и снизу

        Returns:
            int: доступная высота для контента
        """
        size = self.get_terminal_size()
        return max(size.height - border * 2, 20)  # минимум 20 строк


# Глобальный экземпляр для удобного доступа
window_manager = WindowManager()