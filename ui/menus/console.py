"""Общие UI-хелперы для экранов меню."""

from collections.abc import Callable
from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from core.types import StringsDict
from ui.input_handler import get_int_input

SEPARATOR = f"{Fore.YELLOW}{'=' * 78}{Style.RESET_ALL}"


def ability_name(strings: StringsDict, stat_key: str) -> str:
    """Локализованное имя характеристики."""
    return get_string(strings, f"stats.{stat_key}")


def skill_name(strings: StringsDict, skill_key: str) -> str:
    """Локализованное имя навыка."""
    return get_string(strings, f"skills.{skill_key}")


def press_enter(strings: StringsDict) -> None:
    """Ожидание нажатия Enter."""
    prompt = get_string(strings, "common.press_enter")
    input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")


def confirm_yes_no(
    strings: StringsDict, prompt_key: str, **kwargs: Any
) -> bool:
    """Подтвердить действие: 1 — да, 0 — нет."""
    choice = get_int_input(
        get_string(strings, prompt_key, **kwargs),
        0,
        1,
        strings,
    )
    return choice == 1


def print_cancelled(
    strings: StringsDict, key: str = "characters_menu.cancelled"
) -> None:
    """Сообщение об отмене действия и ожидание Enter."""
    print(
        f"{Fore.LIGHTBLACK_EX}"
        f"{get_string(strings, key)}"
        f"{Style.RESET_ALL}"
    )
    print()
    press_enter(strings)


def print_success_and_wait(
    strings: StringsDict,
    msg: str,
    *,
    color: str = Fore.GREEN,
) -> None:
    """Вывести сообщение об успехе и дождаться Enter."""
    print(f"{color}{msg}{Style.RESET_ALL}")
    print()
    press_enter(strings)


def choice_prompt(strings: StringsDict) -> str:
    """Подсказка для числового выбора."""
    return get_string(strings, "common.choice_prompt")


def print_screen_header(caption: str) -> None:
    """Заголовок экрана: разделитель, подпись по центру, разделитель."""
    from ui.terminal_wrap import terminal_width, wrap_text

    width = min(78, terminal_width())
    print(SEPARATOR)
    for line in wrap_text(caption, width=width).splitlines():
        print(f"{Fore.YELLOW}{line.center(width)}{Style.RESET_ALL}")
    print(SEPARATOR)
    print()


def stats_caption_line(strings: StringsDict) -> str:
    """Заголовок экрана генерации характеристик."""
    caption = get_string(strings, "character.stats_generation_caption")
    return f"{Fore.YELLOW}{caption.center(78)}{Style.RESET_ALL}"


def stats_total_line(strings: StringsDict) -> str:
    """Заголовок итоговых характеристик."""
    total = get_string(strings, "character.stats_total")
    return f"{Fore.YELLOW}{total.center(78)}{Style.RESET_ALL}"


def print_numbered_row(idx: int, label: str, *, prefix: str = "  ") -> None:
    """Строка нумерованного меню: жёлтый индекс и подпись."""
    print(f"{prefix}{Fore.YELLOW}{idx}{Style.RESET_ALL}. {label}")


def run_numbered_menu(
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
        print_numbered_row(idx, label)
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
    choice = get_int_input(
        get_string(strings, prompt_key, **kwargs),
        0,
        len(options),
        strings,
    )
    if choice == 0:
        return None
    return choice


def pick_n_from_pool(
    strings: StringsDict,
    pool: list[str],
    count: int,
    *,
    header: str,
    label_for: Callable[[str], str],
    prompt_key: str,
    back_label_key: str = "character.back",
) -> list[str] | None:
    """Выбрать count id из pool через нумерованное меню (0 — назад)."""
    picked: list[str] = []
    for pick_num in range(1, count + 1):
        available = [item for item in pool if item not in picked]
        if not available:
            return None
        print_screen_header(header)
        labels = [label_for(item) for item in available]
        choice = run_numbered_menu(
            strings,
            labels,
            prompt_key=prompt_key,
            back_label_key=back_label_key,
            prompt_kwargs={"current": pick_num, "total": count},
        )
        if choice is None:
            return None
        picked.append(available[choice - 1])
    return picked


def read_numbered_choice(
    strings: StringsDict,
    count: int,
    *,
    prompt_key: str,
    back_label_key: str = "character.back",
    prompt_kwargs: dict[str, Any] | None = None,
) -> int | None:
    """Ввод номера после кастомного рендера списка (0 — назад)."""
    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, back_label_key)}"
    )
    print()
    kwargs = dict(prompt_kwargs or {})
    kwargs.setdefault("count", count)
    choice = get_int_input(
        get_string(strings, prompt_key, **kwargs),
        0,
        count,
        strings,
    )
    if choice == 0:
        return None
    return choice


def _proficiency_menu_marker(proficient: bool) -> str:
    """Зелёная «*» для пунктов меню с владением."""
    if proficient:
        return f"{Fore.GREEN}*{Style.RESET_ALL} "
    return ""


def sort_ids_by_proficiency(
    item_ids: list[str],
    proficiencies: list[str],
    has_proficiency: Callable[[list[str], str], bool],
    *,
    name_key: Callable[[str], str],
) -> list[str]:
    """Сначала предметы с владением, внутри группы — по имени."""
    return sorted(
        item_ids,
        key=lambda item_id: (
            0 if has_proficiency(proficiencies, item_id) else 1,
            name_key(item_id),
        ),
    )


def format_pick_menu_label(name: str, proficient: bool) -> str:
    """Подпись пункта меню выбора с опциональной «*» владения."""
    marker = _proficiency_menu_marker(proficient)
    return f"{marker}{Fore.CYAN}{name}{Style.RESET_ALL}"


def print_pick_list(
    pool: list[str],
    taken: set[str],
    *,
    label_for: Callable[[str], str],
    taken_suffix: str,
    format_selectable: Callable[[int, str, str], None] | None = None,
) -> list[str]:
    """Показать пул; занятые — серым. Вернуть доступные id в порядке вывода."""
    selectable: list[str] = []
    for item_id in pool:
        name = label_for(item_id)
        if item_id in taken:
            print(
                f"  {Fore.LIGHTBLACK_EX}{name} {taken_suffix}"
                f"{Style.RESET_ALL}"
            )
        else:
            selectable.append(item_id)
            idx = len(selectable)
            if format_selectable is not None:
                format_selectable(idx, item_id, name)
            else:
                print_numbered_row(idx, f"{Fore.CYAN}{name}{Style.RESET_ALL}")
    return selectable


def read_pool_pick(
    strings: StringsDict,
    selectable: list[str],
    *,
    prompt: str,
    empty_key: str,
    back_label_key: str = "character.back",
) -> str | None:
    """Ввод выбора из пула после print_pick_list; None — «Назад»."""
    print()
    if not selectable:
        print(f"{Fore.RED}{get_string(strings, empty_key)}{Style.RESET_ALL}")
        print()
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
            f"{get_string(strings, back_label_key)}"
        )
        print()
        if get_int_input(prompt, 0, 0, strings) == 0:
            return None
        return ""

    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
        f"{get_string(strings, back_label_key)}"
    )
    print()
    choice = get_int_input(prompt, 0, len(selectable), strings)
    if choice == 0:
        return None
    return selectable[choice - 1]
