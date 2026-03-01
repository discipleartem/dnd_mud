"""Пользовательский интерфейс."""

from .console import Console
from .colors import ColorName
from .screen_factory import DefaultScreenFactory

__all__ = [
    "Console",
    "ColorName",
    "DefaultScreenFactory",
]
