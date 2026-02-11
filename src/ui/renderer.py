"""Renderer - Facade паттерн над Rich."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn


class Renderer:
    """Фасад над Rich для унифицированного рендеринга.
    
    Скрывает сложность Rich и предоставляет единый интерфейс
    для всех компонентов UI: таблицы, панели, прогресс, колонки.
    """
    
    def __init__(self, console: Console) -> None:
        """Инициализация рендерера."""
        self.console = console
    
    def create_panel(self, 
                  content: str, 
                  title: str = "", 
                  border_style: str = "blue",
                  padding: tuple[int, int] = (1, 2)) -> Panel:
        """Создать стилизованную панель.
        
        Args:
            content: Содержимое панели
            title: Заголовок панели
            border_style: Стиль рамки
            padding: Отступы内容
            
        Returns:
            Panel: Готовая панель Rich
        """
        return Panel(
            content,
            title=title,
            border_style=border_style,
            padding=padding
        )
    
    def create_table(self, 
                  show_header: bool = True,
                  box_style: Any = None,
                  padding: int = 0) -> Table:
        """Создать таблицу с базовыми настройками.
        
        Args:
            show_header: Показывать заголовки колонок
            box_style: Стиль рамки таблицы
            padding: Внутренние отступы
            
        Returns:
            Table: Готовая таблица Rich
        """
        return Table(
            show_header=show_header,
            box=box_style,
            padding=padding
        )
    
    def create_progress_bar(self, 
                        description: str,
                        total: int = 100,
                        completed: int = 0) -> Progress:
        """Создать прогресс-бар.
        
        Args:
            description: Описание прогресса
            total: Максимальное значение
            completed: Текущее значение
            
        Returns:
            Progress: Прогресс-бар Rich
        """
        return Progress(
            TextColumn("[bold]{description}[/bold]"),
            BarColumn(),
            console=self.console,
            total=total
        )
    
    def create_columns(self, *columns) -> Columns:
        """Создать колонки для горизонтального расположения.
        
        Args:
            *columns: Колонки для расположения
            
        Returns:
            Columns: Горизонтальные колонки Rich
        """
        return Columns(*columns)
    
    def create_styled_text(self, 
                        text: str,
                        color: str = "white",
                        bold: bool = False,
                        italic: bool = False) -> Text:
        """Создать стилизованный текст.
        
        Args:
            text: Текст
            color: Цвет текста
            bold: Жирный шрифт
            italic: Курсивный шрифт
            
        Returns:
            Text: Стилизованный текст Rich
        """
        style = ""
        if bold:
            style += "bold "
        if italic:
            style += "italic "
        if color:
            style += color
        
        return Text(text, style=style.strip())
    
    def render_layout(self, layout: Layout) -> None:
        """Отрисовать сложный layout.
        
        Args:
            layout: Компоновка элементов
        """
        self.console.print(layout)
    
    def render_panel(self, panel: Panel) -> None:
        """Отрисовать панель.
        
        Args:
            panel: Панель для отрисовки
        """
        self.console.print(panel)
    
    def render_table(self, table: Table) -> None:
        """Отрисовать таблицу.
        
        Args:
            table: Таблица для отрисовки
        """
        self.console.print(table)
    
    def render_progress(self, progress: Progress, advance: int = 1) -> None:
        """Обновить прогресс-бар.
        
        Args:
            progress: Прогресс-бар
            advance: На сколько увеличить
        """
        progress.advance(advance)
        self.console.print(progress)
    
    def clear(self) -> None:
        """Очистить консоль."""
        self.console.clear()
    
    def print_line(self) -> None:
        """Напечатать разделительную линию."""
        self.console.print()
    
    def create_section_header(self, title: str, level: int = 1) -> Text:
        """Создать заголовок секции.
        
        Args:
            title: Заголовок секции
            level: Уровень заголовка (1-6)
            
        Returns:
            Text: Заголовок секции Rich
        """
        prefix = "#" * level
        return Text(f"{prefix} {title}", style="bold cyan")
