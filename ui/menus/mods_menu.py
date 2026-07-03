"""Меню управления модификациями."""

from colorama import Fore, Style

from core.catalog_loader import reload_catalogs
from core.io import load_json
from core.localization import get_string, resolve_localized_text
from core.mod_loader import (
    MODS_STATE_FILE,
    list_available_mods,
    set_mod_enabled,
)
from core.types import StringsDict
from ui.menus._common import (
    _press_enter,
    _print_screen_header,
    _run_numbered_menu,
)


def _enabled_mod_set() -> set[str]:
    state = load_json(MODS_STATE_FILE, default={"enabled": []})
    enabled = state.get("enabled", [])
    if isinstance(enabled, list):
        return {str(item) for item in enabled}
    return set()


def show_mods_menu(strings: StringsDict, language: str = "ru") -> None:
    """Список модов: включить / выключить."""
    mods = list_available_mods()
    if not mods:
        _print_screen_header(get_string(strings, "mods.caption"))
        print(
            f"{Fore.YELLOW}{get_string(strings, 'mods.none')}{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return

    enabled = _enabled_mod_set()
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

        _print_screen_header(get_string(strings, "mods.caption"))
        choice = _run_numbered_menu(
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
        set_mod_enabled(mod_id, new_state)
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
        _press_enter(strings)
