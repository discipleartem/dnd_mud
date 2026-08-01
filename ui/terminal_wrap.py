"""Перенос текста под ширину терминала."""

import shutil
import textwrap


def terminal_width(default: int = 80) -> int:
    """Текущая ширина терминала."""
    size = shutil.get_terminal_size(fallback=(default, 24))
    return max(40, size.columns)


def wrap_text(text: str, width: int | None = None) -> str:
    """Перенести абзац по ширине терминала."""
    wrap_at = width if width is not None else terminal_width()
    return textwrap.fill(text, width=wrap_at)
