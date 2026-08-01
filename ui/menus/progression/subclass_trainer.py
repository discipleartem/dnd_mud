"""Получение подкласса у наставника (меню персонажей и сценарии)."""

from colorama import Fore, Style

from core.catalogs.classes import (
    get_subclass_choice_level,
    load_subclasses,
)
from core.character.models import Character
from core.character.storage import update_character
from core.platform.localization import get_string
from core.progression.class_progression import (
    mark_class_features_applied,
    needs_class_feature_picks,
)
from core.types import LanguageCode, StringsDict
from ui.menus.console import print_screen_header, print_success_and_wait
from ui.menus.creation.selectors import select_subclass
from ui.menus.creation.subclass_picks import apply_subclass_picks
from ui.menus.progression.class_features import apply_pending_class_features


def assign_subclass_from_menu(
    strings: StringsDict,
    character: Character,
    language: LanguageCode,
) -> Character | None:
    """Выбрать подкласс, применить владения и сохранить. None — отмена."""
    subclass_id = select_subclass(strings, character.class_id, language)
    if subclass_id is None:
        return None

    character.subclass_id = subclass_id
    updated = apply_subclass_picks(
        strings,
        character,
        subclass_id,
        language,
        apply_skills=True,
    )
    if updated is None:
        character.subclass_id = None
        return None

    updated = mark_class_features_applied(updated)
    update_character(updated)
    return updated


def run_subclass_trainer(
    strings: StringsDict,
    character: Character,
    language: LanguageCode = "ru",
) -> Character | None:
    """Экран выбора подкласса у наставника. None — отмена или без изменений."""
    if character.subclass_id is not None:
        if needs_class_feature_picks(character):
            return apply_pending_class_features(strings, character, language)
        msg = get_string(strings, "characters_menu.subclass_trainer_already")
        print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")
        print()
        return character

    choice_level = get_subclass_choice_level(character.class_id)
    if character.level < choice_level:
        msg = get_string(
            strings,
            "characters_menu.subclass_trainer_level_required",
            level=choice_level,
        )
        print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")
        print()
        return character

    print_screen_header(
        get_string(strings, "characters_menu.subclass_trainer_caption")
    )

    updated = assign_subclass_from_menu(strings, character, language)
    if updated is None:
        return None

    subclass_id = updated.subclass_id
    name = subclass_id or ""
    for sub in load_subclasses(character.class_id, language):
        if sub.get("id") == subclass_id:
            name = str(sub.get("name", subclass_id))
            break

    msg = get_string(
        strings, "characters_menu.subclass_trainer_success", name=name
    )
    print_success_and_wait(strings, msg)
    return updated
