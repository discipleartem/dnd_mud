"""Выбор языков расы/подрасы и предыстории при создании персонажа."""

from typing import Any

from colorama import Fore, Style

from core.backgrounds import get_background_language_choice
from core.languages import (
    get_fixed_racial_languages,
    get_language_name,
    get_racial_language_choices,
    resolve_language_pool,
)
from core.localization import get_string
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import _print_screen_header


def _print_language_list(
    strings: StringsDict,
    pool: list[str],
    known: list[str],
    language: str,
) -> list[str]:
    """Показать пул языков; известные — серым."""
    taken_suffix = get_string(strings, "character.languages_taken_suffix")
    selectable: list[str] = []
    for lang_id in pool:
        name = get_language_name(lang_id, language)
        if lang_id in known:
            print(
                f"  {Fore.LIGHTBLACK_EX}{name} {taken_suffix}"
                f"{Style.RESET_ALL}"
            )
        else:
            selectable.append(lang_id)
            idx = len(selectable)
            print(
                f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
                f"{Fore.CYAN}{name}{Style.RESET_ALL}"
            )
    return selectable


def _pick_language_choices(
    strings: StringsDict,
    mechanics: dict[str, Any],
    known_languages: list[str],
    language: str,
    *,
    prompt_key: str,
    pick_offset: int = 0,
    pick_total: int | None = None,
) -> list[str] | None:
    """Выбор N языков из пула; None — назад."""
    count = int(mechanics.get("count", 0))
    pool_spec = mechanics.get("pool", "common")
    total = pick_total if pick_total is not None else count
    added: list[str] = []
    current = list(known_languages)

    for pick_idx in range(1, count + 1):
        while True:
            _print_screen_header(
                get_string(strings, "character.languages_caption")
            )
            if current:
                names = ", ".join(
                    get_language_name(lang_id, language) for lang_id in current
                )
                known_line = get_string(
                    strings,
                    "character.languages_known",
                    list=names,
                )
                print(f"{Fore.CYAN}{known_line}{Style.RESET_ALL}")
                print()
            prompt = get_string(
                strings,
                prompt_key,
                current=pick_offset + pick_idx,
                total=total,
            )
            lang_pool = resolve_language_pool(pool_spec, current)
            selectable = _print_language_list(
                strings, lang_pool, current, language
            )
            print()
            if not selectable:
                empty_msg = get_string(
                    strings, "character.languages_pool_empty"
                )
                print(f"{Fore.RED}{empty_msg}{Style.RESET_ALL}")
                print()
                print(
                    f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
                    f"{get_string(strings, 'character.back')}"
                )
                print()
                if _deps.get_int_input(prompt, 0, 0, strings) == 0:
                    return None
                continue

            print(
                f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
                f"{get_string(strings, 'character.back')}"
            )
            print()
            choice = _deps.get_int_input(prompt, 0, len(selectable), strings)
            if choice == 0:
                return None
            picked = selectable[choice - 1]
            added.append(picked)
            current.append(picked)
            break

    return added


def select_creation_languages(
    strings: StringsDict,
    race_id: str,
    subrace_id: str | None,
    background_id: str,
    language: str = "ru",
) -> list[str] | None:
    """Языки расы и предыстории после выбора background."""
    known = get_fixed_racial_languages(race_id, subrace_id)
    racial_choices = get_racial_language_choices(race_id, subrace_id)
    bg_mechanics = get_background_language_choice(background_id)

    racial_pick_total = sum(int(m.get("count", 0)) for m, _ in racial_choices)

    _print_screen_header(get_string(strings, "character.languages_caption"))

    if known:
        names = ", ".join(
            get_language_name(lang_id, language) for lang_id in known
        )
        print(
            f"{Fore.YELLOW}{Style.BRIGHT}"
            f"{get_string(strings, 'character.languages_fixed', list=names)}"
            f"{Style.RESET_ALL}"
        )
        print()

    result = list(known)
    pick_offset = 0

    for mechanics, _source in racial_choices:
        count = int(mechanics.get("count", 0))
        if count <= 0:
            continue
        picked = _pick_language_choices(
            strings,
            mechanics,
            result,
            language,
            prompt_key="character.languages_pick_prompt",
            pick_offset=pick_offset,
            pick_total=racial_pick_total,
        )
        if picked is None:
            return None
        result.extend(picked)
        pick_offset += count

    if bg_mechanics is not None:
        bg_count = int(bg_mechanics.get("count", 0))
        if bg_count > 0:
            picked = _pick_language_choices(
                strings,
                bg_mechanics,
                result,
                language,
                prompt_key="character.background_languages_prompt",
            )
            if picked is None:
                return None
            result.extend(picked)

    return result
