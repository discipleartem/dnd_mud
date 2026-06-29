"""Получение подкласса у наставника (меню персонажей и сценарии)."""

from colorama import Fore, Style

from core.class_features import (
    mark_class_features_applied,
    needs_class_feature_picks,
)
from core.classes import get_subclass_choice_level
from core.localization import get_string
from core.models import Character
from core.proficiencies import (
    apply_subclass_proficiencies_to_character,
    is_valid_tool_selection,
    merge_proficiency_tokens,
)
from core.types import LanguageCode, StringsDict
from ui.menus import _deps
from ui.menus._common import _print_screen_header, _print_success_and_wait
from ui.menus.character_flow import _select_subclass
from ui.menus.class_features import apply_pending_class_features
from ui.menus.expertise import apply_pending_expertise
from ui.menus.proficiencies import _pick_tools
from ui.menus.skills import add_subclass_skills_from_menu


def assign_subclass_from_menu(
    strings: StringsDict,
    character: Character,
    language: LanguageCode,
) -> Character | None:
    """Выбрать подкласс, применить владения и сохранить. None — отмена."""
    subclass_id = _select_subclass(strings, character.class_id, language)
    if subclass_id is None:
        return None

    character.subclass_id = subclass_id
    choices = apply_subclass_proficiencies_to_character(character, subclass_id)
    if choices:
        pick_total = sum(c.count for c in choices)
        pick_offset = 0
        for choice in choices:
            picked = _pick_tools(
                strings,
                choice,
                character.tool_proficiencies,
                language,
                pick_offset + 1,
                pick_total,
            )
            if picked is None:
                character.subclass_id = None
                return None
            pool = choice.options or []
            if not is_valid_tool_selection(picked, pool, choice.count):
                character.subclass_id = None
                return None
            character.tool_proficiencies = merge_proficiency_tokens(
                character.tool_proficiencies, picked
            )
            pick_offset += choice.count

    updated_skills = add_subclass_skills_from_menu(
        strings,
        character.class_id,
        subclass_id,
        character.level,
        character.skills,
        language,
    )
    if updated_skills is None:
        character.subclass_id = None
        return None
    character.skills = updated_skills

    expertise_result = apply_pending_expertise(strings, character, language)
    if expertise_result is None:
        character.subclass_id = None
        return None
    character.skill_expertise, character.tool_expertise = expertise_result

    character = mark_class_features_applied(character)
    _deps.update_character(character)
    return character


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

    _print_screen_header(
        get_string(strings, "characters_menu.subclass_trainer_caption")
    )

    updated = assign_subclass_from_menu(strings, character, language)
    if updated is None:
        return None

    subclass_id = updated.subclass_id
    name = subclass_id or ""
    for sub in _deps.load_subclasses(character.class_id, language):
        if sub.get("id") == subclass_id:
            name = str(sub.get("name", subclass_id))
            break

    msg = get_string(
        strings, "characters_menu.subclass_trainer_success", name=name
    )
    _print_success_and_wait(strings, msg)
    return updated
