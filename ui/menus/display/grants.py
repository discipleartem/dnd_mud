"""Вывод grants (print-обёртки над core.grants.format)."""

from typing import Any

from core.grants.format import (
    format_grant_line_text,
)
from core.types import StringsDict

__all__ = [
    "format_grant_line_text",
    "_print_grant_line",
]


def _print_grant_line(
    grant: dict[str, Any],
    strings: StringsDict,
    language: str,
) -> None:
    """Вывести одну строку особенности."""
    print(format_grant_line_text(grant, strings, language))
