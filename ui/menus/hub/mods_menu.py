"""Меню управления модификациями."""

from colorama import Fore, Style

from core.platform.catalog_loader import reload_catalogs
from core.platform.localization import get_string, resolve_localized_text
from core.platform.mod_loader import (
    get_enabled_mod_ids,
    list_available_mods,
    set_mod_enabled,
)
from core.types import StringsDict
from ui.menus.console import (
    press_enter,
    print_screen_header,
    run_numbered_menu,
)


def show_mods_menu(strings: StringsDict, language: str = "ru") -> None:
    """Список модов: включить / выключить."""
    mods = list_available_mods()
    if not mods:
        print_screen_header(get_string(strings, "mods.caption"))
        print(
            f"{Fore.YELLOW}{get_string(strings, 'mods.none')}{Style.RESET_ALL}"
        )
        print()
        press_enter(strings)
        return

    enabled = set(get_enabled_mod_ids())
    while True:
        options: list[str] = []
        for mod in mods:
            mod_id = str(mod.get("id", ""))
            name = resolve_localized_text(mod.get("name", mod_id), language)
            status_key = (
                "mods.status_on" if mod_id in enabled else "mods.status_off"
            )
            status = get_string(strings, status_key)
            options.append(
                get_string(
                    strings,
                    "mods.line",
                    name=name,
                    version=str(mod.get("version", "")),
                    status=status,
                )
            )

        print_screen_header(get_string(strings, "mods.caption"))
        choice = run_numbered_menu(
            strings,
            options,
            prompt_key="mods.prompt",
            back_label_key="mods.back",
        )
        if choice is None:
            return

        selected = mods[choice - 1]
        mod_id = str(selected.get("id", ""))
        new_state = mod_id not in enabled
        error = set_mod_enabled(mod_id, new_state)
        if error is not None:
            msg_key = str(error.get("key", "mods.error_missing"))
            params = {k: v for k, v in error.items() if k != "key"}
            print(
                f"{Fore.RED}"
                f"{get_string(strings, msg_key, **params)}"
                f"{Style.RESET_ALL}"
            )
            print()
            press_enter(strings)
            continue
        reload_catalogs()
        if new_state:
            enabled.add(mod_id)
        else:
            enabled.discard(mod_id)
        print(
            f"{Fore.GREEN}"
            f"{get_string(strings, 'mods.toggled', name=mod_id)}"
            f"{Style.RESET_ALL}"
        )
        print()
        press_enter(strings)
