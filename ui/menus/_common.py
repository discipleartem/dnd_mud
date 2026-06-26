"""Общие UI-хелперы для экранов меню."""

from collections.abc import Callable
from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from core.types import StringsDict
from ui.menus import _deps

SEPARATOR = f"{Fore.YELLOW}{'=' * 78}{Style.RESET_ALL}"


def _ability_name(strings: StringsDict, stat_key: str) -> str:
    """Локализованное имя характеристики."""
    return get_string(strings, f"stats.{stat_key}")


def _skill_name(strings: StringsDict, skill_key: str) -> str:
    """Локализованное имя навыка."""
    return get_string(strings, f"skills.{skill_key}")


def _press_enter(strings: StringsDict) -> None:
    """Ожидание нажатия Enter."""
    prompt = get_string(strings, "common.press_enter")
    input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")


def _confirm_yes_no(
    strings: StringsDict, prompt_key: str, **kwargs: Any
) -> bool:
    """Подтвердить действие: 1 — да, 0 — нет."""
    choice = _deps.get_int_input(
        get_string(strings, prompt_key, **kwargs),
        0,
        1,
        strings,
    )
    return choice == 1


def _print_cancelled(
    strings: StringsDict, key: str = "characters_menu.cancelled"
) -> None:
    """Сообщение об отмене действия и ожидание Enter."""
    print(
        f"{Fore.LIGHTBLACK_EX}"
        f"{get_string(strings, key)}"
        f"{Style.RESET_ALL}"
    )
    print()
    _press_enter(strings)


def _print_success_and_wait(
    strings: StringsDict,
    msg: str,
    *,
    color: str = Fore.GREEN,
) -> None:
    """Вывести сообщение об успехе и дождаться Enter."""
    print(f"{color}{msg}{Style.RESET_ALL}")
    print()
    _press_enter(strings)


def _choice_prompt(strings: StringsDict) -> str:
    """Подсказка для числового выбора."""
    return get_string(strings, "common.choice_prompt")


def _print_screen_header(caption: str) -> None:
    """Заголовок экрана: разделитель, подпись по центру, разделитель."""
    print(SEPARATOR)
    print(f"{Fore.YELLOW}{caption.center(78)}{Style.RESET_ALL}")
    print(SEPARATOR)
    print()


def _stats_caption_line(strings: StringsDict) -> str:
    """Заголовок экрана генерации характеристик."""
    caption = get_string(strings, "character.stats_generation_caption")
    return f"{Fore.YELLOW}{caption.center(78)}{Style.RESET_ALL}"


def _stats_total_line(strings: StringsDict) -> str:
    """Заголовок итоговых характеристик."""
    total = get_string(strings, "character.stats_total")
    return f"{Fore.YELLOW}{total.center(78)}{Style.RESET_ALL}"


def _run_numbered_menu(
    strings: StringsDict,
    options: list[str],
    *,
    prompt_key: str,
    back_label_key: str = "common.back",
    prompt_kwargs: dict[str, Any] | None = None,
    before_back: Callable[[], None] | None = None,
) -> int | None:
    """Нумерованное меню: 1..N — опции, 0 — назад. None при выборе 0."""
    for idx, label in enumerate(options, 1):
        print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {label}")
    if before_back is not None:
        before_back()
    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, back_label_key)}"
    )
    print()

    kwargs = dict(prompt_kwargs or {})
    kwargs.setdefault("count", len(options))
    choice = _deps.get_int_input(
        get_string(strings, prompt_key, **kwargs),
        0,
        len(options),
        strings,
    )
    if choice == 0:
        return None
    return choice
