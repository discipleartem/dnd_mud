"""Применение отложенных особенностей класса и подкласса у наставника."""

from colorama import Fore, Style

from core.class_features import (
    mark_class_features_applied,
    needs_class_feature_picks,
    subclass_skill_picks_pending,
)
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
from ui.menus.expertise import apply_pending_expertise
from ui.menus.proficiencies import _pick_tools
from ui.menus.skills import add_subclass_skills_from_menu


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

    _print_screen_header(get_string(strings, "class_features.caption"))
    intro = get_string(strings, "class_features.intro")
    print(f"{Fore.CYAN}{intro}{Style.RESET_ALL}")
    print()

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
                return None
            pool = choice.options or []
            if not is_valid_tool_selection(picked, pool, choice.count):
                return None
            character.tool_proficiencies = merge_proficiency_tokens(
                character.tool_proficiencies, picked
            )
            pick_offset += choice.count

    if subclass_skill_picks_pending(character):
        updated_skills = add_subclass_skills_from_menu(
            strings,
            character.class_name,
            subclass_id,
            character.level,
            character.skills,
            language,
        )
        if updated_skills is None:
            return None
        character.skills = updated_skills

    expertise_result = apply_pending_expertise(strings, character, language)
    if expertise_result is None:
        return None
    skill_expertise, tool_expertise = expertise_result
    character.skill_expertise = skill_expertise
    character.tool_expertise = tool_expertise

    character = mark_class_features_applied(character)
    _deps.update_character(character)

    msg = get_string(strings, "class_features.success")
    _print_success_and_wait(strings, msg)
    return character
