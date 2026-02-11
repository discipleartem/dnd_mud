# src/core/window_manager.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text


class FontSize(Enum):
    """Размеры шрифта (количество символов на дюйм)."""
    TINY = 16      # 16x32
    SMALL = 24     # 24x48  
    MEDIUM = 32     # 32x64
    LARGE = 48      # 48x96
    HUGE = 64       # 64x128


@dataclass
class TextSettings:
    """Настройки текста."""
    font_size: FontSize = FontSize.MEDIUM
    color: str = "white"
    background_color: str = "black"
    bold: bool = False
    italic: bool = False


@dataclass
class TerminalSize:
    """Размеры терминала с учетом шрифта."""
    width: int
    height: int
    font_size: FontSize = FontSize.MEDIUM
    
    @property
    def effective_width(self) -> int:
        """Эффективная ширина с учетом границ."""
        return self.width - 4  # 2 символа с каждой стороны
    
    @property
    def is_minimal(self) -> bool:
        """Проверяет минимальный размер."""
        return self.width >= 80 and self.height >= 24
    
    @property
    def max_text_width(self) -> int:
        """Максимальная ширина текста."""
        return self.effective_width


class WindowManager:
    """Улучшенный фасад для работы с терминалом.
    
    Особенности:
    - Умный перенос текста с учетом границ и шрифта
    - Настройка размера шрифта
    - Динамическое изменение цвета текста
    """
    
    MIN_WIDTH = 80
    MIN_HEIGHT = 24
    
    def __init__(self, console: Console) -> None:
        """Инициализация фасада."""
        self.console = console
        self._text_settings = TextSettings()
        self._size = self._get_terminal_size()
        
    def _get_terminal_size(self) -> TerminalSize:
        """Получить текущий размер терминала."""
        size = self.console.size
        return TerminalSize(
            width=size.width, 
            height=size.height,
            font_size=self._text_settings.font_size
        )
    
    def _create_style(self, overrides: dict[str, Any] | None = None) -> Style:
        """Создать стиль Rich с текущими настройками."""
        base_style = {
            "color": self._text_settings.color,
            "bold": self._text_settings.bold,
            "italic": self._text_settings.italic
        }
        
        if overrides:
            base_style.update(overrides)
            
        return Style(**base_style)

    
    
    def _fallback_wrap(self, text: str, width: int) -> list[str]:
        """Простой перенос слов, если Rich не справился."""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.rstrip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.rstrip())
        
        return lines if lines else [text]
    

    def set_font_size(self, font_size: FontSize) -> None:
        """Установить размер шрифта."""
        self._text_settings.font_size = font_size
        self._size.font_size = font_size
    
   
    def set_text_color(self, color: str) -> None:
        """Установить цвет текста по умолчанию."""
        self._text_settings.color = color
    
    
    def set_text_style(self, *, 
                   color: str | None = None,
                   bold: bool | None = None,
                   italic: bool | None = None) -> None:
        """Установить стиль текста."""
        if color is not None:
            self._text_settings.color = color
        if bold is not None:
            self._text_settings.bold = bold
        if italic is not None:
            self._text_settings.italic = italic

    def wrap_text(self, text: str, width: int | None = None) -> list[str]:
        """Умный перенос текста с учетом границ и длинных слов."""
        if width is None:
            width = self._size.effective_width
        
        if width <= 0:
            return [text]  # Нечего переносить
        
        try:
            rich_text = Text(text, style=self._create_style())
            wrapped = rich_text.wrap(self.console, width)
            return wrapped.splitlines() if wrapped else [text]
        except Exception:
            # Fallback на простой перенос
            return self._fallback_wrap(text, width)


    def print_text(self, text: str,  color: str | None = None,
             bold: bool = False, italic: bool = False,
             wrap: bool = True) -> None:

        """Печать текста с текущими или кастомными настройками."""
        style_overrides = {}
        if color is not None:
            style_overrides["color"] = color
        if bold:
            style_overrides["bold"] = True
        if italic:
            style_overrides["italic"] = True
        
        style = self._create_style(style_overrides)
        
        if wrap:
            lines = self.wrap_text(text)
            text_to_print = "\n".join(lines)
        else:
            text_to_print = text
        
        self.console.print(text_to_print, style=style)

    def show_menu(self, items: list[str], selected: int = 0) -> None:
        """Показать меню с учетом текущих настроек текста."""
        table = Table(show_header=False, box=None, padding=0)
        table.add_column("menu", style=self._text_settings.color)
        
        for i, item in enumerate(items):
            if i == selected:
                selected_style = self._create_style({"color": "yellow"})
                table.add_row(f"▶ {item}", style=selected_style)
            else:
                table.add_row(f"  {item}")
        
        panel = Panel(table, border_style="green")
        self.console.print(panel)


    def clear_screen(self) -> None:
        """Очистить экран."""
        self.console.clear()


    def show_title(self, title: str, subtitle: str = "") -> None:
        """Показать заголовок."""
        if subtitle:
            content = f"[bold blue]{title}[/bold blue]\n{subtitle}"
        else:
            content = f"[bold blue]{title}[/bold blue]"
        
        panel = Panel(content, border_style="blue", padding=(1, 2))
        self.console.print(panel)


    def show_error(self, message: str) -> None:
        """Показать ошибку."""
        panel = Panel(
            f"[red]{message}[/red]",
            title="Ошибка",
            border_style="red"
        )
        self.console.print(panel)


    def show_info(self, message: str) -> None:
        """Показать информационное сообщение."""
        panel = Panel(
            f"[cyan]{message}[/cyan]",
            border_style="cyan"
        )
        self.console.print(panel)


    def check_terminal_size(self) -> bool:
        """Проверить минимальный размер терминала."""
        self._size = self._get_terminal_size()
        return self._size.is_minimal