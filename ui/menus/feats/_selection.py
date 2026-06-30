"""Меню выбора черты из списков eligible/blocked/hidden."""

from typing import Any

from colorama import Fore, Style

from core.feats import FeatRequirementContext
from core.localization import get_string
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import SEPARATOR
from ui.menus.feats._requirements import (
    _confirm_feat_selection,
    _print_feat_details,
)


def _print_feat_selection_menu(
    strings: StringsDict,
    eligible: list[dict[str, Any]],
    blocked: list[dict[str, Any]],
    hidden: list[dict[str, Any]],
    ctx: FeatRequirementContext,
    language: str,
) -> None:
    """Список черт: доступные, с невыполненными требованиями и скрытые."""
    for idx, feat in enumerate(eligible, 1):
        if idx > 1:
            print(f"  {Fore.LIGHTBLACK_EX}{SEPARATOR}{Style.RESET_ALL}")
        print()
        print(f"  {Fore.GREEN}{idx}{Style.RESET_ALL}. ", end="")
        _print_feat_details(
            strings,
            feat,
            ctx,
            language,
            color=Fore.GREEN,
            muted=False,
        )

    if blocked:
        print()
        heading = get_string(
            strings, "character.feat_requirements_unmet_heading"
        )
        print(f"  {Fore.LIGHTBLACK_EX}" f"{heading}" f"{Style.RESET_ALL}")
        for feat in blocked:
            print()
            print(f"  {Fore.LIGHTBLACK_EX}—{Style.RESET_ALL}. ", end="")
            _print_feat_details(
                strings,
                feat,
                ctx,
                language,
                color=Fore.LIGHTBLACK_EX,
                muted=True,
            )

    if hidden:
        print()
        heading = get_string(strings, "character.feat_hidden_heading")
        print(f"  {Fore.LIGHTBLACK_EX}" f"{heading}" f"{Style.RESET_ALL}")
        for feat in hidden:
            print()
            print(f"  {Fore.LIGHTBLACK_EX}—{Style.RESET_ALL}. ", end="")
            _print_feat_details(
                strings,
                feat,
                ctx,
                language,
                color=Fore.LIGHTBLACK_EX,
                muted=True,
            )


def _pick_feat_from_lists(
    strings: StringsDict,
    eligible: list[dict[str, Any]],
    blocked: list[dict[str, Any]],
    hidden: list[dict[str, Any]],
    ctx: FeatRequirementContext,
    language: str,
) -> dict[str, Any] | None:
    """Выбор черты из списков; None — назад или нет доступных."""
    if not eligible:
        return None
    while True:
        _print_feat_selection_menu(
            strings, eligible, blocked, hidden, ctx, language
        )
        print()
        choice = _deps.get_int_input(
            get_string(strings, "character.feat_prompt", count=len(eligible)),
            0,
            len(eligible),
            strings,
        )
        if choice == 0:
            return None
        selected = eligible[choice - 1]
        if _confirm_feat_selection(strings, selected, ctx, language):
            return selected
