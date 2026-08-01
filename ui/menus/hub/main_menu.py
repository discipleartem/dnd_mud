"""Приветствие, главное меню и заглушка загрузки игры."""

from colorama import Fore, Style

from core.platform.localization import get_string
from core.types import StringsDict
from ui.menus.console import (
    SCREEN_WIDTH,
    SEPARATOR,
    print_screen_header,
    run_numbered_menu,
)

MainMenuAction = str


def show_welcome_screen(version: str, strings: StringsDict) -> None:
    """Показать приветственный экран."""
    print()
    print_screen_header(get_string(strings, "welcome.title"))
    print(
        f"{Fore.GREEN}{get_string(strings, 'welcome.subtitle')}"
        f"{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}"
        f"{get_string(strings, 'welcome.version', version=version)}"
        f"{Style.RESET_ALL}"
    )
    print()


def show_main_menu(
    strings: StringsDict, *, has_creation_draft: bool = False
) -> MainMenuAction:
    """Показать главное меню и вернуть action id."""
    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'menu.caption').center(SCREEN_WIDTH)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()

    entries: list[tuple[str, str]] = []
    if has_creation_draft:
        entries.append(
            ("continue", get_string(strings, "menu.continue_creation"))
        )
    entries.extend(
        [
            ("new_game", get_string(strings, "menu.new_game")),
            ("load_game", get_string(strings, "menu.load_game")),
            ("characters", get_string(strings, "menu.characters")),
            ("settings", get_string(strings, "menu.settings")),
            ("languages", get_string(strings, "menu.languages")),
            ("mods", get_string(strings, "menu.mods")),
        ]
    )
    options = [label for _, label in entries]
    actions = [action for action, _ in entries]

    def _separator_before_back() -> None:
        print()
        print(SEPARATOR)

    choice = run_numbered_menu(
        strings,
        options,
        prompt_key="menu.prompt",
        back_label_key="menu.exit",
        prompt_kwargs={"max": len(options)},
        before_back=_separator_before_back,
    )
    if choice is None or choice == 0:
        return "exit"
    return actions[choice - 1]
