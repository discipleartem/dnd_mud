"""Предупреждение о битых файлах сохранений персонажей."""

from collections.abc import Sequence

from colorama import Fore, Style

from core.localization import get_string
from core.types import StringsDict


def show_corrupt_save_warnings_if_any(
    strings: StringsDict,
    *,
    corrupt_labels: Sequence[str],
    already_shown: bool,
) -> bool:
    """Показать предупреждение один раз за визит. Вернуть обновлённый флаг."""
    if not corrupt_labels or already_shown:
        return already_shown
    names = ", ".join(corrupt_labels)
    warning = get_string(
        strings,
        "characters_menu.corrupt_save_warning",
        names=names,
    )
    print(f"  {Fore.RED}{warning}{Style.RESET_ALL}")
    print()
    return True
