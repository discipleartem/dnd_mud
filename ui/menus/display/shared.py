"""Общие label/field хелперы отображения."""

from typing import Any

from colorama import Fore, Style

from core.equipment import (
    proficiency_token_label,
)
from core.localization import (
    get_string,
)
from core.types import (
    GameDifficulty,
    StringsDict,
)

# ============================================================================
# Общие хелперы подписей
# ============================================================================


def _localized_string_list(value: Any, language: str) -> list[str]:
    """Локализованный список строк из YAML (ru/en или плоский list)."""
    if isinstance(value, dict):
        raw = value.get(language)
        if not isinstance(raw, list):
            for key in (language, "en", "ru"):
                candidate = value.get(key)
                if isinstance(candidate, list):
                    raw = candidate
                    break
        if isinstance(raw, list):
            return [str(item) for item in raw]
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _label_from_catalog(
    catalog: list[dict[str, Any]],
    entity_id: str,
    *,
    default: str | None = None,
) -> str:
    """Имя сущности по id из списка каталога."""
    for item in catalog:
        if item.get("id") == entity_id:
            return str(item.get("name", entity_id))
    return default if default is not None else entity_id


# ============================================================================
# Отображение режима сложности
# ============================================================================


def _difficulty_label(strings: StringsDict, difficulty: GameDifficulty) -> str:
    """Локализованное название режима сложности."""
    mode_key = f"difficulty.{difficulty}"
    mode = get_string(strings, mode_key)
    if mode == mode_key:
        return difficulty
    return mode


def _difficulty_color(difficulty: GameDifficulty) -> str:
    """Цвет для отображения режима сложности."""
    match difficulty:
        case "easy":
            return str(Fore.GREEN)
        case "normal":
            return str(Fore.YELLOW)
        case "hardcore":
            return str(Fore.RED)


# ============================================================================
# Локализованное отображение grants[]
# ============================================================================


def _empty_field_value(strings: StringsDict) -> str:
    """Плейсхолдер для пустого поля карточки персонажа."""
    empty = get_string(strings, "choose_character.field_empty")
    return f"{Fore.LIGHTBLACK_EX}{empty}{Style.RESET_ALL}"


def _print_labeled_field(
    strings: StringsDict,
    label_key: str,
    value: str,
    indent: str = "     ",
) -> None:
    """Вывести строку «подпись: значение» с цветной подписью."""
    label = get_string(strings, label_key)
    print(
        f"{indent}" f"{Fore.LIGHTBLACK_EX}{label}{Style.RESET_ALL} " f"{value}"
    )


# ============================================================================
# Секции карточки персонажа
# ============================================================================


def _format_proficiency_token_list(
    strings: StringsDict,
    tokens: list[str],
    *,
    language: str = "ru",
) -> str:
    """Локализованный список токенов владений."""
    names = [proficiency_token_label(t, strings, language) for t in tokens]
    return ", ".join(names)
