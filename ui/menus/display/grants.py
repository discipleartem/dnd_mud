"""Вывод grants (print-обёртки над grants_text)."""

from typing import Any

from core.types import StringsDict
from ui.menus.display.grants_text import format_grant_line_text

__all__ = [
    "_print_grant_line",
]


def _print_grant_line(
    grant: dict[str, Any],
    strings: StringsDict,
    language: str,
) -> None:
    """Вывести одну строку особенности."""
    print(format_grant_line_text(grant, strings, language))
