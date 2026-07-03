"""Перенос текста под ширину терминала."""

import shutil
import textwrap
from collections.abc import Iterable


def terminal_width(default: int = 80) -> int:
    """Текущая ширина терминала."""
    size = shutil.get_terminal_size(fallback=(default, 24))
    return max(40, size.columns)


def wrap_text(text: str, width: int | None = None) -> str:
    """Перенести абзац по ширине терминала."""
    wrap_at = width if width is not None else terminal_width()
    return textwrap.fill(text, width=wrap_at)


def wrap_lines(lines: Iterable[str], width: int | None = None) -> list[str]:
    """Перенести каждую строку отдельно."""
    wrap_at = width if width is not None else terminal_width()
    result: list[str] = []
    for line in lines:
        if not line.strip():
            result.append(line)
            continue
        result.extend(textwrap.wrap(line, width=wrap_at) or [""])
    return result


def print_wrapped(text: str, width: int | None = None) -> None:
    """Вывести текст с переносом."""
    print(wrap_text(text, width=width))
