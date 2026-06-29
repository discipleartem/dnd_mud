"""Шаги state machine создания персонажа."""

from dataclasses import dataclass, field
from typing import Any, Literal

from core.class_features import class_features_applied_at_creation
from core.expertise import expertise_step_required
from core.feats import get_feat_language_ids, race_feat_step_required
from core.localization import get_string
from core.models import Character
from core.subclasses import (
    start_level_for_difficulty,
    subclass_offered_at_creation,
)
from core.types import GameDifficulty, StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import (
    _print_screen_header,
    _print_success_and_wait,
    _run_numbered_menu,
)
from ui.menus._selectors import select_class, select_subclass, select_subrace
from ui.menus.backgrounds import select_creation_background
from ui.menus.expertise import select_creation_expertise
from ui.menus.feats import select_creation_feats
from ui.menus.languages import select_creation_languages
from ui.menus.proficiencies import select_creation_proficiencies
from ui.menus.skills import select_creation_skills
from ui.menus.stats import show_stats_generation_flow

CreationStep = Literal[
    "race",
    "subrace",
    "languages",
    "stats",
    "background",
    "feats",
    "class",
    "subclass",
    "proficiencies",
    "skills",
    "expertise",
]


@dataclass
class _CreationState:
    """Состояние пошагового создания персонажа."""

    name: str
    difficulty: GameDifficulty
    race_id: str | None = None
    subrace_id: str | None = None
    languages: list[str] | None = None
    stats: StatMap | None = None
    background_id: str | None = None
    background_skills: list[str] = field(default_factory=list)
    class_id: str | None = None
    subclass_id: str | None = None
    skills: list[str] | None = None
    skill_expertise: list[str] | None = None
    tool_expertise: list[str] | None = None
    weapon_proficiencies: list[str] | None = None
    armor_proficiencies: list[str] | None = None
    tool_proficiencies: list[str] | None = None
    feat_ids: list[str] = field(default_factory=list)
    feat_choices: dict[str, dict[str, Any]] = field(default_factory=dict)
    hardcore_rolls: list[int] = field(default_factory=list)


def _feats_step_required(state: _CreationState) -> bool:
    """Нужен ли шаг выбора черт (вариант человека и т.п.)."""
    if state.race_id is None:
        return False
    return race_feat_step_required(state.race_id, state.subrace_id)


def _back_step_from_skills(_state: _CreationState) -> CreationStep:
    """Куда вернуться с шага навыков."""
    return "proficiencies"


def _step_after_class_choice(state: _CreationState) -> CreationStep:
    """Следующий шаг после выбора класса/подкласса."""
    if _feats_step_required(state):
        return "feats"
    return "proficiencies"


def _back_step_from_feats(state: _CreationState) -> CreationStep:
    """Куда вернуться с шага черт (сразу после класса/подкласса)."""
    if state.class_id is None:
        return "class"
    if subclass_offered_at_creation(state.difficulty, state.class_id):
        return "subclass"
    return "class"


def _back_step_from_proficiencies(state: _CreationState) -> CreationStep:
    """Куда вернуться с шага владений."""
    if _feats_step_required(state):
        return "feats"
    if state.class_id is None:
        return "class"
    if subclass_offered_at_creation(state.difficulty, state.class_id):
        return "subclass"
    return "class"


def _merge_feat_languages(state: _CreationState) -> None:
    """Добавить языки из черт к уже выбранным."""
    feat_langs = get_feat_language_ids(state.feat_ids, state.feat_choices)
    if not feat_langs:
        return
    merged = list(state.languages or [])
    for lang_id in feat_langs:
        if lang_id not in merged:
            merged.append(lang_id)
    state.languages = merged


def _finalize_creation(
    strings: StringsDict, state: _CreationState
) -> Character | None:
    """Сохранить персонажа и показать сообщение об успехе."""
    character = _save_created_character(state)
    if character is None:
        return None
    msg = get_string(strings, "character.save_success", name=state.name)
    _print_success_and_wait(strings, msg)
    return character


def _save_created_character(state: _CreationState) -> Character | None:
    """Сохранить персонажа из состояния создания."""
    if state.race_id is None or state.stats is None or state.class_id is None:
        return None

    start_level = start_level_for_difficulty(state.difficulty)
    features_applied = class_features_applied_at_creation(
        state.class_id, state.subclass_id, start_level
    )

    return _deps.save_character(
        name=state.name,
        race_id=str(state.race_id),
        class_id=str(state.class_id),
        difficulty=state.difficulty,
        subrace_id=str(state.subrace_id) if state.subrace_id else None,
        stats=state.stats,
        subclass_id=state.subclass_id,
        languages=state.languages,
        background_id=state.background_id,
        skills=state.skills,
        skill_expertise=state.skill_expertise,
        tool_expertise=state.tool_expertise,
        weapon_proficiencies=state.weapon_proficiencies,
        armor_proficiencies=state.armor_proficiencies,
        tool_proficiencies=state.tool_proficiencies,
        feat_ids=state.feat_ids or None,
        feat_choices=state.feat_choices or None,
        class_features_applied=features_applied,
        apply_feat_stat_bonuses=False,
    )


def run_creation_steps(
    strings: StringsDict,
    state: _CreationState,
    language: str = "ru",
) -> Character | None:
    """Цикл шагов создания персонажа после ввода имени."""
    step: CreationStep = "race"

    while True:
        match step:
            case "race":
                races = _deps.load_races(language)
                _print_screen_header(
                    get_string(strings, "character.race_caption")
                )
                choice = _run_numbered_menu(
                    strings,
                    [race.get("name", "?") for race in races],
                    prompt_key="character.race_prompt",
                    back_label_key="character.back",
                )
                if choice is None:
                    return None
                selected = races[choice - 1]
                state.race_id = str(selected.get("id") or selected.get("name"))
                step = "subrace"

            case "subrace":
                if state.race_id is None:
                    step = "race"
                    continue
                subrace_selected, subrace_id = select_subrace(
                    strings, state.race_id, language
                )
                if not subrace_selected:
                    if state.difficulty == "hardcore":
                        state.hardcore_rolls.clear()
                    step = "race"
                    continue
                state.subrace_id = subrace_id
                step = "stats"

            case "stats":
                if state.race_id is None:
                    step = "race"
                    continue
                hardcore_rolls = (
                    state.hardcore_rolls
                    if state.difficulty == "hardcore"
                    else None
                )
                stats = show_stats_generation_flow(
                    strings,
                    state.race_id,
                    state.subrace_id,
                    state.difficulty,
                    hardcore_rolls=hardcore_rolls,
                )
                if stats is None:
                    step = "subrace"
                    continue
                state.stats = stats
                step = "background"

            case "background":
                bg_result = select_creation_background(strings, language)
                if bg_result is None:
                    step = "stats"
                    continue
                bg_id, bg_skills = bg_result
                state.background_id = bg_id
                state.background_skills = bg_skills
                step = "languages"

            case "languages":
                if state.race_id is None or state.background_id is None:
                    step = "background"
                    continue
                langs = select_creation_languages(
                    strings,
                    state.race_id,
                    state.subrace_id,
                    state.background_id,
                    language,
                )
                if langs is None:
                    step = "background"
                    continue
                state.languages = langs
                step = "class"

            case "class":
                if state.race_id is None or state.stats is None:
                    step = "languages"
                    continue
                cls = select_class(strings, language)
                if cls is None:
                    step = "languages"
                    continue

                state.class_id = str(cls.get("id") or cls.get("name"))
                if subclass_offered_at_creation(
                    state.difficulty, state.class_id
                ):
                    step = "subclass"
                else:
                    step = _step_after_class_choice(state)

            case "subclass":
                if state.class_id is None:
                    step = "class"
                    continue
                subclass_id = select_subclass(
                    strings, state.class_id, language
                )
                if subclass_id is None:
                    step = "class"
                    continue
                state.subclass_id = subclass_id
                step = _step_after_class_choice(state)

            case "feats":
                if (
                    state.race_id is None
                    or state.stats is None
                    or state.class_id is None
                ):
                    step = "class"
                    continue
                start_level = start_level_for_difficulty(state.difficulty)
                feat_result = select_creation_feats(
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
                    step = _back_step_from_feats(state)
                    continue
                feat_ids, feat_choices, updated_stats = feat_result
                state.feat_ids = feat_ids
                state.feat_choices = feat_choices
                state.stats = updated_stats
                _merge_feat_languages(state)
                step = "proficiencies"

            case "proficiencies":
                if state.race_id is None or state.class_id is None:
                    step = "class"
                    continue
                profs = select_creation_proficiencies(
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
                    step = _back_step_from_proficiencies(state)
                    continue
                (
                    state.weapon_proficiencies,
                    state.armor_proficiencies,
                    (state.tool_proficiencies),
                ) = profs
                step = "skills"

            case "skills":
                if state.race_id is None or state.class_id is None:
                    step = "proficiencies"
                    continue
                start_level = start_level_for_difficulty(state.difficulty)
                skills = select_creation_skills(
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
                    step = _back_step_from_skills(state)
                    continue
                state.skills = skills
                if expertise_step_required(state.class_id, start_level):
                    step = "expertise"
                else:
                    return _finalize_creation(strings, state)

            case "expertise":
                if state.class_id is None or state.skills is None:
                    step = "skills"
                    continue
                start_level = start_level_for_difficulty(state.difficulty)
                expertise_result = select_creation_expertise(
                    strings,
                    state.class_id,
                    start_level,
                    state.skills,
                    language,
                )
                if expertise_result is None:
                    step = "skills"
                    continue
                state.skill_expertise, state.tool_expertise = expertise_result
                return _finalize_creation(strings, state)
