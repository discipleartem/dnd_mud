"""Подвыборы внутри черты при создании и левелапе."""

from typing import Any

from core.equipment import (
    all_tool_ids,
    all_weapon_ids,
    proficiency_token_label,
)
from core.feats import load_feat
from core.localization import get_string
from core.skills import PHB_SKILL_IDS
from core.types import StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import (
    _ability_name,
    _print_screen_header,
    _run_numbered_menu,
    _skill_name,
)
from ui.menus.feats._constants import (
    ELEMENTAL_DAMAGE_TYPES,
    MAGIC_INITIATE_CLASSES,
)


def _pick_ability_for_feat(
    strings: StringsDict,
    feat: dict[str, Any],
    stats: StatMap,
) -> str | None:
    """Выбор характеристики для черты с ability_bonuses_choice."""
    choice_list = feat.get("ability_bonuses_choice", [])
    if not isinstance(choice_list, list) or not choice_list:
        return None
    amount = int(feat.get("ability_bonuses_amount", 1))
    labels = [f"{_ability_name(strings, s)} +{amount}" for s in choice_list]
    _print_screen_header(get_string(strings, "character.feat_pick_ability"))
    choice = _run_numbered_menu(
        strings,
        labels,
        prompt_key="character.feat_pick_ability_prompt",
        back_label_key="character.back",
    )
    if choice is None:
        return None
    return str(choice_list[choice - 1])


def _pick_weapons_for_feat(
    strings: StringsDict,
    count: int,
    language: str,
    *,
    weapon_proficiencies: list[str] | None = None,
) -> list[str] | None:
    """Выбор видов оружия для weapon_master."""
    from core.proficiencies import has_weapon_proficiency

    proficiencies = weapon_proficiencies or []
    pool = [
        w
        for w in all_weapon_ids()
        if not has_weapon_proficiency(proficiencies, w)
    ]
    picked: list[str] = []
    for pick_num in range(1, count + 1):
        _print_screen_header(get_string(strings, "character.feat_caption"))
        available = [w for w in pool if w not in picked]
        if not available:
            return None
        labels = [
            proficiency_token_label(w, strings, language) for w in available
        ]
        choice = _run_numbered_menu(
            strings,
            labels,
            prompt_key="character.feat_pick_weapon",
            back_label_key="character.back",
            prompt_kwargs={"current": pick_num, "total": count},
        )
        if choice is None:
            return None
        picked.append(available[choice - 1])
    return picked


def _pick_skills_or_tools(
    strings: StringsDict,
    count: int,
    language: str,
    *,
    known_skills: list[str] | None = None,
    known_tools: list[str] | None = None,
) -> list[dict[str, str]] | None:
    """Выбор навыков или инструментов для skilled."""
    from core.proficiencies import has_tool_proficiency

    known_skills = known_skills or []
    known_tools = known_tools or []
    picked: list[dict[str, str]] = []
    skill_pool = [s for s in PHB_SKILL_IDS if s not in known_skills]
    tool_pool = [
        t for t in all_tool_ids() if not has_tool_proficiency(known_tools, t)
    ]

    for pick_num in range(1, count + 1):
        _print_screen_header(get_string(strings, "character.feat_caption"))
        options: list[tuple[str, str, str]] = []
        for sid in skill_pool:
            if any(p.get("id") == sid for p in picked):
                continue
            options.append(("skill", sid, _skill_name(strings, sid)))
        for tid in tool_pool:
            if any(p.get("id") == tid for p in picked):
                continue
            options.append(
                (
                    "tool",
                    tid,
                    proficiency_token_label(tid, strings, language),
                )
            )
        if not options:
            return None
        labels = [label for _, _, label in options]
        choice = _run_numbered_menu(
            strings,
            labels,
            prompt_key="character.feat_pick_skill_tool",
            back_label_key="character.back",
            prompt_kwargs={"current": pick_num, "total": count},
        )
        if choice is None:
            return None
        kind, item_id, _ = options[choice - 1]
        picked.append({"type": kind, "id": item_id})
    return picked


def _pick_elemental_damage(strings: StringsDict) -> str | None:
    """Выбор стихии для elemental_adept."""
    labels = [
        get_string(strings, f"character.feat_element_{dtype}")
        for dtype in ELEMENTAL_DAMAGE_TYPES
    ]
    _print_screen_header(get_string(strings, "character.feat_caption"))
    choice = _run_numbered_menu(
        strings,
        labels,
        prompt_key="character.feat_pick_element",
        back_label_key="character.back",
    )
    if choice is None:
        return None
    return ELEMENTAL_DAMAGE_TYPES[choice - 1]


def _pick_spell_class(strings: StringsDict) -> str | None:
    """Выбор класса заклинателя для magic_initiate / ritual_caster."""
    labels = [
        get_string(strings, f"classes.{cls_id}.name", default=cls_id)
        for cls_id in MAGIC_INITIATE_CLASSES
    ]
    _print_screen_header(get_string(strings, "character.feat_caption"))
    choice = _run_numbered_menu(
        strings,
        labels,
        prompt_key="character.feat_pick_caster_class",
        back_label_key="character.back",
    )
    if choice is None:
        return None
    return MAGIC_INITIATE_CLASSES[choice - 1]


def _pick_languages_for_feat(
    strings: StringsDict,
    count: int,
    language: str,
    *,
    known: list[str] | None = None,
) -> list[str] | None:
    """Выбор языков для linguist."""
    known = known or []
    all_langs = _deps.load_languages(language)
    pool = [
        str(entry.get("id", ""))
        for entry in all_langs
        if str(entry.get("id", "")) not in known
    ]
    picked: list[str] = []
    for pick_num in range(1, count + 1):
        available = [lang for lang in pool if lang not in picked]
        labels = [
            _deps.get_language_name(lang_id, language) for lang_id in available
        ]
        _print_screen_header(get_string(strings, "character.feat_caption"))
        choice = _run_numbered_menu(
            strings,
            labels,
            prompt_key="character.feat_pick_language",
            back_label_key="character.back",
            prompt_kwargs={"current": pick_num, "total": count},
        )
        if choice is None:
            return None
        picked.append(available[choice - 1])
    return picked


def _pick_expertise_skills(
    strings: StringsDict,
    count: int,
) -> list[str] | None:
    """Выбор навыков для skill_expert (экспертное владение)."""
    picked: list[str] = []
    pool = list(PHB_SKILL_IDS)
    for pick_num in range(1, count + 1):
        available = [s for s in pool if s not in picked]
        labels = [_skill_name(strings, sid) for sid in available]
        _print_screen_header(get_string(strings, "character.feat_caption"))
        choice = _run_numbered_menu(
            strings,
            labels,
            prompt_key="character.feat_pick_expertise",
            back_label_key="character.back",
            prompt_kwargs={"current": pick_num, "total": count},
        )
        if choice is None:
            return None
        picked.append(available[choice - 1])
    return picked


def _resolve_feat_subchoices(
    strings: StringsDict,
    feat_id: str,
    stats: StatMap,
    language: str,
    *,
    known_languages: list[str] | None = None,
    known_skills: list[str] | None = None,
    known_tools: list[str] | None = None,
    weapon_proficiencies: list[str] | None = None,
) -> dict[str, Any] | None:
    """Подвыборы внутри одной черты."""
    feat = load_feat(feat_id)
    choices: dict[str, Any] = {}

    if feat.get("ability_bonuses_choice"):
        ability = _pick_ability_for_feat(strings, feat, stats)
        if ability is None:
            return None
        choices["ability"] = ability

    for grant in feat.get("grants", []):
        if not isinstance(grant, dict):
            continue
        mtype = grant.get("type", "")
        if mtype == "weapon_proficiency" and grant.get("choice"):
            count = int(grant.get("count", 1))
            weapons = _pick_weapons_for_feat(
                strings,
                count,
                language,
                weapon_proficiencies=weapon_proficiencies,
            )
            if weapons is None:
                return None
            choices["weapons"] = weapons
        elif mtype == "multiple_proficiency" and grant.get("choice"):
            count = int(grant.get("count", 1))
            picks = _pick_skills_or_tools(
                strings,
                count,
                language,
                known_skills=known_skills,
                known_tools=known_tools,
            )
            if picks is None:
                return None
            choices["skills_tools"] = picks
        elif mtype == "resistance" and grant.get("choice"):
            element = _pick_elemental_damage(strings)
            if element is None:
                return None
            choices["damage_type"] = element
        elif mtype in ("magic_initiate", "ritual_caster"):
            cls = _pick_spell_class(strings)
            if cls is None:
                return None
            choices["caster_class"] = cls
        elif mtype == "skill_expertise" and grant.get("choice"):
            count = int(grant.get("count", 2))
            expertise = _pick_expertise_skills(strings, count)
            if expertise is None:
                return None
            choices["expertise"] = expertise
        elif mtype == "language" and grant.get("choice"):
            count = int(grant.get("count", 3))
            langs = _pick_languages_for_feat(
                strings, count, language, known=known_languages
            )
            if langs is None:
                return None
            choices["languages"] = langs

    return choices
