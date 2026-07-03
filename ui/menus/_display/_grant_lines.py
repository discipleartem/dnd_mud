"""Форматирование строк grants[] для экранов UI."""

from typing import Any

from core.localization import get_string
from core.types import StringsDict
from ui.menus._display._grants import _grant_description, _grant_display_name


def format_grant_line_text(
    grant: dict[str, Any],
    strings: StringsDict,
    language: str = "ru",
) -> str:
    """Локализованная строка одной особенности (без print)."""
    name = _grant_display_name(grant, strings)
    desc = _grant_description(grant, strings, language)
    if desc:
        return get_string(
            strings,
            "character.feature_line",
            name=name,
            desc=desc,
        )
    return get_string(
        strings,
        "character.feature_line_name_only",
        name=name,
    )


def format_grant_lines(
    grants: list[dict[str, Any]],
    strings: StringsDict,
    language: str = "ru",
) -> list[str]:
    """Строки особенностей для списка grants."""
    return [
        format_grant_line_text(grant, strings, language) for grant in grants
    ]
