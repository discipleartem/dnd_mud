"""
UI модуль D&D MUD.

Содержит компоненты пользовательского интерфейса:
- Renderer для отрисовки
- InputHandler для обработки ввода
- Меню и диалоги
"""

from .renderer import renderer
from .input_handler import input_handler

__all__ = ["renderer", "input_handler"]
