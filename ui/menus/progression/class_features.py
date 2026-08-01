"""Применение отложенных особенностей класса и подкласса у наставника."""

from colorama import Fore, Style

from core.character.models import Character
from core.character.storage import update_character
from core.platform.localization import get_string
from core.progression.class_progression import (
    mark_class_features_applied,
    needs_class_feature_picks,
)
from core.types import LanguageCode, StringsDict
from ui.menus.console import print_screen_header, print_success_and_wait
from ui.menus.creation.subclass_picks import apply_subclass_picks


def apply_pending_class_features(
    strings: StringsDict,
    character: Character,
    language: LanguageCode = "ru",
) -> Character | None:
    """Выбор и применение особенностей подкласса. None — отмена."""
    if not needs_class_feature_picks(character):
        return character

    subclass_id = character.subclass_id
    if not subclass_id:
        return character

    print_screen_header(get_string(strings, "class_features.caption"))
    intro = get_string(strings, "class_features.intro")
    print(f"{Fore.CYAN}{intro}{Style.RESET_ALL}")
    print()

    updated = apply_subclass_picks(strings, character, subclass_id, language)
    if updated is None:
        return None

    updated = mark_class_features_applied(updated)
    update_character(updated)

    msg = get_string(strings, "class_features.success")
    print_success_and_wait(strings, msg)
    return updated
