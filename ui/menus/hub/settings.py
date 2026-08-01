"""Настройки, языки и выбор сложности."""

from colorama import Fore, Style

from core.platform.localization import get_string, load_strings
from core.types import (
    GameDifficulty,
    LanguageCode,
    RuntimeSettings,
    StringsDict,
)
from ui.menus.console import (
    press_enter,
    print_screen_header,
    run_numbered_menu,
)
from ui.menus.hub.mods_menu import show_mods_menu


def select_difficulty(strings: StringsDict) -> GameDifficulty | None:
    """Экран выбора сложности при создании персонажа."""
    print_screen_header(get_string(strings, "difficulty.caption"))

    options_data: list[tuple[GameDifficulty, str, str]] = [
        ("easy", get_string(strings, "difficulty.easy"), str(Fore.GREEN)),
        ("normal", get_string(strings, "difficulty.normal"), str(Fore.YELLOW)),
        (
            "hardcore",
            get_string(strings, "difficulty.hardcore"),
            str(Fore.RED),
        ),
    ]
    labels = [label for _, label, _ in options_data]
    choice = run_numbered_menu(
        strings,
        labels,
        prompt_key="difficulty.prompt",
        back_label_key="difficulty.back",
        row_formatter=lambda idx, label: (
            f"{options_data[idx - 1][2]}{label}{Style.RESET_ALL}"
        ),
        row_marker=lambda idx: (
            f"{Fore.GREEN}* {Style.RESET_ALL}" if idx == 1 else "  "
        ),
    )

    if choice is None:
        return None

    return options_data[choice - 1][0]


def show_languages_menu(
    strings: StringsDict, settings: RuntimeSettings
) -> RuntimeSettings:
    """Меню выбора языка."""
    while True:
        print_screen_header(get_string(strings, "languages.caption"))

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
        choice = run_numbered_menu(
            strings,
            options,
            prompt_key="languages.prompt",
            back_label_key="languages.back",
        )

        if choice is None:
            break

        new_lang = lang_codes[choice - 1]
        settings = {"language": new_lang}
        strings = load_strings(new_lang)
        msg = get_string(
            strings,
            "languages.changed",
            name=get_string(strings, f"languages.lang_{new_lang}"),
        )
        print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
        print()
        press_enter(strings)

    return settings


def show_settings(
    strings: StringsDict, settings: RuntimeSettings
) -> RuntimeSettings:
    """Экран настроек."""
    while True:
        options = [get_string(strings, "settings.option_mods")]
        print_screen_header(get_string(strings, "settings.caption"))
        choice = run_numbered_menu(
            strings,
            options,
            prompt_key="settings.prompt",
            back_label_key="settings.back",
        )

        if choice is None:
            break

        if choice == 1:
            show_mods_menu(strings, settings["language"])

    return settings
