"""Общие UI-хелперы для экранов меню."""

from typing import Any

from colorama import Fore, Style

from core.localization import get_string

SEPARATOR = f"{Fore.YELLOW}{'=' * 78}{Style.RESET_ALL}"


def _ability_name(strings: dict[str, Any], stat_key: str) -> str:
    """Локализованное имя характеристики."""
    return get_string(strings, f"stats.{stat_key}")


def _press_enter(strings: dict[str, Any]) -> None:
    """Ожидание нажатия Enter."""
    prompt = get_string(strings, "common.press_enter")
    input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")


def _choice_prompt(strings: dict[str, Any]) -> str:
    """Подсказка для числового выбора."""
    return get_string(strings, "common.choice_prompt")


def _print_screen_header(caption: str) -> None:
    """Заголовок экрана: разделитель, подпись по центру, разделитель."""
    print(SEPARATOR)
    print(f"{Fore.YELLOW}{caption.center(78)}{Style.RESET_ALL}")
    print(SEPARATOR)
    print()


def _stats_caption_line(strings: dict[str, Any]) -> str:
    """Заголовок экрана генерации характеристик."""
    caption = get_string(strings, "character.stats_generation_caption")
    return f"{Fore.YELLOW}{caption.center(78)}{Style.RESET_ALL}"


def _stats_total_line(strings: dict[str, Any]) -> str:
    """Заголовок итоговых характеристик."""
    total = get_string(strings, "character.stats_total")
    return f"{Fore.YELLOW}{total.center(78)}{Style.RESET_ALL}"
