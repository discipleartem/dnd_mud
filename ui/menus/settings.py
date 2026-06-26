"""Настройки, языки и выбор сложности."""

from colorama import Fore, Style

from core.localization import get_string
from core.types import (
    GameDifficulty,
    LanguageCode,
    RuntimeSettings,
    StringsDict,
)
from ui.menus import _deps
from ui.menus._common import (
    _press_enter,
    _print_screen_header,
    _run_numbered_menu,
)


def select_difficulty(strings: StringsDict) -> GameDifficulty | None:
    """Экран выбора сложности при создании персонажа."""
    _print_screen_header(get_string(strings, "difficulty.caption"))

    options: list[tuple[GameDifficulty, str, str]] = [
        ("easy", get_string(strings, "difficulty.easy"), str(Fore.GREEN)),
        ("normal", get_string(strings, "difficulty.normal"), str(Fore.YELLOW)),
        (
            "hardcore",
            get_string(strings, "difficulty.hardcore"),
            str(Fore.RED),
        ),
    ]
    for idx, (_, label, color) in enumerate(options, 1):
        marker = f"{Fore.GREEN}* {Style.RESET_ALL}" if idx == 1 else "  "
        print(
            f"{marker}{Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            f"{color}{label}{Style.RESET_ALL}"
        )
    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'difficulty.back')}"
    )
    print()

    choice = _deps.get_int_input(
        get_string(strings, "difficulty.prompt", count=len(options)),
        0,
        len(options),
        strings,
    )

    if choice == 0:
        return None

    return options[choice - 1][0]


def show_languages_menu(
    strings: StringsDict, settings: RuntimeSettings
) -> RuntimeSettings:
    """Меню выбора языка."""
    while True:
        _print_screen_header(get_string(strings, "languages.caption"))

        current = settings["language"]
        lang_name = get_string(
            strings, f"languages.lang_{current}", default=current
        )
        print(f"  {get_string(strings, 'languages.current')} {lang_name}")
        print()

        lang_codes: list[LanguageCode] = (
            ["en", "ru"] if current == "ru" else ["ru", "en"]
        )
        options = [
            get_string(strings, f"languages.lang_{code}")
            for code in lang_codes
        ]
        choice = _run_numbered_menu(
            strings,
            options,
            prompt_key="languages.prompt",
            back_label_key="languages.back",
        )

        if choice is None:
            break

        new_lang = lang_codes[choice - 1]
        settings = {"language": new_lang}
        strings = _deps.load_strings(new_lang)
        msg = get_string(
            strings,
            "languages.changed",
            name=get_string(strings, f"languages.lang_{new_lang}"),
        )
        print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
        print()
        _press_enter(strings)

    return settings


def show_settings(
    strings: StringsDict, settings: RuntimeSettings
) -> RuntimeSettings:
    """Экран настроек."""
    while True:
        _print_screen_header(get_string(strings, "settings.caption"))
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'settings.back')}"
        )
        print()

        choice = _deps.get_int_input(
            get_string(strings, "settings.prompt", count=0),
            0,
            0,
            strings,
        )

        if choice == 0:
            break

    return settings
