"""Меню увеличения характеристик при левелапе."""

from colorama import Fore, Style

from core.localization import get_string
from core.stats import STAT_NAMES
from core.types import StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import (
    _ability_name,
    _choice_prompt,
    _print_screen_header,
    _run_numbered_menu,
)


def select_asi_mode(strings: StringsDict) -> str | None:
    """Выбор: ASI или черта. 'asi' | 'feat' | None."""
    labels = [
        get_string(strings, "level_up.asi_increase_stats"),
        get_string(strings, "level_up.asi_take_feat"),
    ]
    choice = _run_numbered_menu(
        strings,
        labels,
        prompt_key="level_up.asi_or_feat_prompt",
        back_label_key="character.back",
    )
    if choice is None:
        return None
    if choice == 1:
        return "asi"
    return "feat"


def select_asi_stats(
    strings: StringsDict, stats: StatMap
) -> tuple[str, str] | None:
    """+2 к одной или +1 к двум."""
    labels = [
        get_string(strings, "level_up.asi_two_one"),
        get_string(strings, "level_up.asi_one_two"),
    ]
    mode = _run_numbered_menu(
        strings,
        labels,
        prompt_key="level_up.asi_mode_prompt",
        back_label_key="character.back",
    )
    if mode is None:
        return None

    if mode == 1:
        stat = _pick_one_stat(strings, stats, amount=2)
        if stat is None:
            return None
        return stat, stat

    stat_a = _pick_one_stat(strings, stats, amount=1)
    if stat_a is None:
        return None
    stat_b = _pick_one_stat(
        strings,
        stats,
        amount=1,
        exclude=[stat_a],
    )
    if stat_b is None:
        return None
    return stat_a, stat_b


def _pick_one_stat(
    strings: StringsDict,
    stats: StatMap,
    *,
    amount: int,
    exclude: list[str] | None = None,
) -> str | None:
    """Выбор одной характеристики для ASI."""
    exclude = exclude or []
    available = [s for s in STAT_NAMES if s not in exclude]
    _print_screen_header(get_string(strings, "level_up.asi_pick_stat"))
    print(
        f"{Fore.CYAN}{get_string(strings, 'level_up.asi_cap_warning')}"
        f"{Style.RESET_ALL}"
    )
    print()
    for idx, stat in enumerate(available, 1):
        current = stats.get(stat, 10)
        capped = current + amount > 20
        cap_note = ""
        if capped:
            cap_note = f" ({get_string(strings, 'level_up.asi_at_cap')})"
        print(
            f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            f"{_ability_name(strings, stat)}: {current}{cap_note}"
        )
    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
        f"{get_string(strings, 'character.back')}"
    )
    print()
    choice = _deps.get_int_input(
        _choice_prompt(strings), 0, len(available), strings
    )
    if choice == 0:
        return None
    return available[choice - 1]
