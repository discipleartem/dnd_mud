"""Обработчики шагов создания персонажа."""

from collections.abc import Callable
from dataclasses import dataclass

from core.expertise import expertise_step_required
from core.localization import get_string
from core.models import Character
from core.subclasses import subclass_offered_at_creation
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import _print_screen_header, _run_numbered_menu
from ui.menus._creation_state import CreationStep, _CreationState


@dataclass
class StepResult:
    """Результат одного шага: следующий шаг, готовый персонаж или отмена."""

    next_step: CreationStep | None = None
    character: Character | None = None


def _advance(step: CreationStep) -> StepResult:
    return StepResult(next_step=step)


def _abort() -> StepResult:
    return StepResult()


def _done(strings: StringsDict, state: _CreationState) -> StepResult:
    from ui.menus import _creation_steps as flow

    return StepResult(character=flow.finalize_creation(strings, state))


def _handle_race(
    strings: StringsDict, state: _CreationState, language: str
) -> StepResult:
    races = _deps.load_races(language)
    _print_screen_header(get_string(strings, "character.race_caption"))
    choice = _run_numbered_menu(
        strings,
        [race.get("name", "?") for race in races],
        prompt_key="character.race_prompt",
        back_label_key="character.back",
    )
    if choice is None:
        return _abort()
    selected = races[choice - 1]
    state.race_id = str(selected.get("id") or selected.get("name"))
    return _advance("subrace")


def _handle_subrace(
    strings: StringsDict, state: _CreationState, language: str
) -> StepResult:
    from ui.menus import _creation_steps as flow

    if state.race_id is None:
        return _advance("race")
    subrace_selected, subrace_id = flow.select_subrace(
        strings, state.race_id, language
    )
    if not subrace_selected:
        if state.difficulty == "hardcore":
            state.hardcore_rolls.clear()
        return _advance("race")
    state.subrace_id = subrace_id
    return _advance("stats")


def _handle_stats(
    strings: StringsDict, state: _CreationState, _language: str
) -> StepResult:
    from ui.menus import _creation_steps as flow

    if state.race_id is None:
        return _advance("race")
    hardcore_rolls = (
        state.hardcore_rolls if state.difficulty == "hardcore" else None
    )
    stats = flow.show_stats_generation_flow(
        strings,
        state.race_id,
        state.subrace_id,
        state.difficulty,
        hardcore_rolls=hardcore_rolls,
    )
    if stats is None:
        return _advance("subrace")
    state.stats = stats
    return _advance("background")


def _handle_background(
    strings: StringsDict, state: _CreationState, language: str
) -> StepResult:
    from ui.menus import _creation_steps as flow

    bg_result = flow.select_creation_background(strings, language)
    if bg_result is None:
        return _advance("stats")
    bg_id, bg_skills = bg_result
    state.background_id = bg_id
    state.background_skills = bg_skills
    return _advance("languages")


def _handle_languages(
    strings: StringsDict, state: _CreationState, language: str
) -> StepResult:
    from ui.menus import _creation_steps as flow

    if state.race_id is None or state.background_id is None:
        return _advance("background")
    langs = flow.select_creation_languages(
        strings,
        state.race_id,
        state.subrace_id,
        state.background_id,
        language,
    )
    if langs is None:
        return _advance("background")
    state.languages = langs
    return _advance("class")


def _handle_class(
    strings: StringsDict, state: _CreationState, language: str
) -> StepResult:
    from ui.menus import _creation_steps as flow

    if state.race_id is None or state.stats is None:
        return _advance("languages")
    cls = flow.select_class(strings, language)
    if cls is None:
        return _advance("languages")
    state.class_id = str(cls.get("id") or cls.get("name"))
    if subclass_offered_at_creation(state.difficulty, state.class_id):
        return _advance("subclass")
    return _advance(flow.step_after_class_choice(state))


def _handle_subclass(
    strings: StringsDict, state: _CreationState, language: str
) -> StepResult:
    from ui.menus import _creation_steps as flow

    if state.class_id is None:
        return _advance("class")
    subclass_id = flow.select_subclass(strings, state.class_id, language)
    if subclass_id is None:
        return _advance("class")
    state.subclass_id = subclass_id
    return _advance(flow.step_after_class_choice(state))


def _handle_feats(
    strings: StringsDict, state: _CreationState, language: str
) -> StepResult:
    from ui.menus import _creation_steps as flow

    if state.race_id is None or state.stats is None or state.class_id is None:
        return _advance("class")
    start_level = state.start_level
    feat_result = flow.select_creation_feats(
        strings,
        state.race_id,
        state.subrace_id,
        state.stats,
        state.background_id,
        language,
        class_id=state.class_id,
        subclass_id=state.subclass_id,
        start_level=start_level,
        known_languages=state.languages,
    )
    if feat_result is None:
        return _advance(flow.back_step_from_feats(state))
    feat_ids, feat_choices, updated_stats = feat_result
    state.feat_ids = feat_ids
    state.feat_choices = feat_choices
    state.stats = updated_stats
    flow.merge_feat_languages(state)
    return _advance("proficiencies")


def _handle_proficiencies(
    strings: StringsDict, state: _CreationState, language: str
) -> StepResult:
    from ui.menus import _creation_steps as flow

    if state.race_id is None or state.class_id is None:
        return _advance("class")
    profs = flow.select_creation_proficiencies(
        strings,
        state.race_id,
        state.subrace_id,
        state.class_id,
        state.background_id,
        state.subclass_id,
        state.difficulty,
        language,
        feat_ids=state.feat_ids,
        feat_choices=state.feat_choices,
    )
    if profs is None:
        return _advance(flow.back_step_from_proficiencies(state))
    (
        state.weapon_proficiencies,
        state.armor_proficiencies,
        state.tool_proficiencies,
    ) = profs
    return _advance("skills")


def _handle_skills(
    strings: StringsDict, state: _CreationState, language: str
) -> StepResult:
    from ui.menus import _creation_steps as flow

    if state.race_id is None or state.class_id is None:
        return _advance("proficiencies")
    start_level = state.start_level
    skills = flow.select_creation_skills(
        strings,
        state.race_id,
        state.subrace_id,
        state.class_id,
        language,
        background_skills=state.background_skills,
        subclass_id=state.subclass_id,
        start_level=start_level,
        feat_ids=state.feat_ids,
        feat_choices=state.feat_choices,
    )
    if skills is None:
        return _advance(flow.back_step_from_skills(state))
    state.skills = skills
    if expertise_step_required(state.class_id, start_level):
        return _advance("expertise")
    return _done(strings, state)


def _handle_expertise(
    strings: StringsDict, state: _CreationState, language: str
) -> StepResult:
    from ui.menus import _creation_steps as flow

    if state.class_id is None or state.skills is None:
        return _advance("skills")
    start_level = state.start_level
    expertise_result = flow.select_creation_expertise(
        strings,
        state.class_id,
        start_level,
        state.skills,
        language,
    )
    if expertise_result is None:
        return _advance("skills")
    state.skill_expertise, state.tool_expertise = expertise_result
    return _done(strings, state)


_STEP_HANDLERS: dict[
    CreationStep,
    Callable[[StringsDict, _CreationState, str], StepResult],
] = {
    "race": _handle_race,
    "subrace": _handle_subrace,
    "stats": _handle_stats,
    "background": _handle_background,
    "languages": _handle_languages,
    "class": _handle_class,
    "subclass": _handle_subclass,
    "feats": _handle_feats,
    "proficiencies": _handle_proficiencies,
    "skills": _handle_skills,
    "expertise": _handle_expertise,
}
