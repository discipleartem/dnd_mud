"""Выбор черт при создании персонажа и при левелапе."""

from typing import Any

from colorama import Fore, Style

from core.equipment import (
    all_tool_ids,
    all_weapon_ids,
    proficiency_token_label,
)
from core.feats import (
    FeatRequirementContext,
    apply_feats_to_stats,
    character_has_spellcasting,
    get_race_feat_grants,
    list_available_feats,
    load_feat,
    resolve_feat_ability_bonuses,
)
from core.localization import get_string
from core.proficiencies import (
    get_background_tool_proficiencies,
    get_racial_proficiency_tokens,
)
from core.skills import PHB_SKILL_IDS
from core.types import StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import (
    SEPARATOR,
    _ability_name,
    _print_screen_header,
    _run_numbered_menu,
    _skill_name,
)

ELEMENTAL_DAMAGE_TYPES = [
    "acid",
    "cold",
    "fire",
    "lightning",
    "thunder",
]

MAGIC_INITIATE_CLASSES = [
    "bard",
    "cleric",
    "druid",
    "sorcerer",
    "warlock",
    "wizard",
]


def _feat_ctx_at_creation(
    stats: StatMap,
    race_id: str,
    subrace_id: str | None,
    background_id: str | None,
) -> FeatRequirementContext:
    """Контекст требований черт на шаге создания (до класса)."""
    rw, ra, rt, _ = get_racial_proficiency_tokens(race_id, subrace_id)
    bg_tools: list[str] = []
    if background_id:
        bg_tools, _ = get_background_tool_proficiencies(background_id)
    return FeatRequirementContext(
        stats=stats,
        weapon_tokens=list(rw),
        armor_tokens=list(ra),
        tool_tokens=list(rt) + list(bg_tools),
        has_spellcasting=False,
    )


def _feat_ctx_for_character(character: Any) -> FeatRequirementContext:
    """Контекст требований при левелапе."""
    return FeatRequirementContext(
        stats=character.stats,
        weapon_tokens=list(character.weapon_proficiencies),
        armor_tokens=list(character.armor_proficiencies),
        tool_tokens=list(character.tool_proficiencies),
        class_id=character.class_name,
        subclass_id=character.subclass_id,
        level=character.level + 1,
        has_spellcasting=character_has_spellcasting(
            character.class_name,
            character.subclass_id,
            character.level + 1,
        ),
    )


def _print_feat_details(strings: StringsDict, feat: dict[str, Any]) -> None:
    """Имя и описание черты."""
    print(
        f"  {Fore.CYAN}{Style.BRIGHT}{feat.get('name', '?')}{Style.RESET_ALL}"
    )
    desc = feat.get("description", "")
    if desc:
        print(f"     {desc}")


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
) -> list[str] | None:
    """Выбор видов оружия для weapon_master."""
    pool = all_weapon_ids()
    picked: list[str] = []
    for pick_num in range(1, count + 1):
        _print_screen_header(get_string(strings, "character.feat_caption"))
        available = [w for w in pool if w not in picked]
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
    known_skills = known_skills or []
    known_tools = known_tools or []
    picked: list[dict[str, str]] = []
    skill_pool = [s for s in PHB_SKILL_IDS if s not in known_skills]
    tool_pool = [t for t in all_tool_ids() if t not in known_tools]

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
) -> dict[str, Any] | None:
    """Подвыборы внутри одной черты."""
    feat = load_feat(feat_id)
    choices: dict[str, Any] = {}

    if feat.get("ability_bonuses_choice"):
        ability = _pick_ability_for_feat(strings, feat, stats)
        if ability is None:
            return None
        choices["ability"] = ability

    for feature in feat.get("features", []):
        if not isinstance(feature, dict):
            continue
        mechanics = feature.get("mechanics", {})
        if not isinstance(mechanics, dict):
            continue
        mtype = mechanics.get("type", "")
        if mtype == "weapon_proficiency" and mechanics.get("choice"):
            count = int(mechanics.get("count", 1))
            weapons = _pick_weapons_for_feat(strings, count, language)
            if weapons is None:
                return None
            choices["weapons"] = weapons
        elif mtype == "multiple_proficiency" and mechanics.get("choice"):
            count = int(mechanics.get("count", 1))
            picks = _pick_skills_or_tools(strings, count, language)
            if picks is None:
                return None
            choices["skills_tools"] = picks
        elif mtype == "resistance" and mechanics.get("choice"):
            element = _pick_elemental_damage(strings)
            if element is None:
                return None
            choices["damage_type"] = element
        elif mtype == "magic_initiate" or mtype == "ritual_caster":
            cls = _pick_spell_class(strings)
            if cls is None:
                return None
            choices["caster_class"] = cls
        elif mtype == "skill_expertise" and mechanics.get("choice"):
            count = int(mechanics.get("count", 2))
            expertise = _pick_expertise_skills(strings, count)
            if expertise is None:
                return None
            choices["expertise"] = expertise
        elif mtype == "language" and mechanics.get("choice"):
            count = int(mechanics.get("count", 3))
            langs = _pick_languages_for_feat(
                strings, count, language, known=known_languages
            )
            if langs is None:
                return None
            choices["languages"] = langs

    return choices


def select_creation_feats(
    strings: StringsDict,
    race_id: str,
    subrace_id: str | None,
    stats: StatMap,
    background_id: str | None,
    language: str = "ru",
    *,
    known_languages: list[str] | None = None,
) -> tuple[list[str], dict[str, dict[str, Any]], StatMap] | None:
    """Выбор расовых черт; None — назад."""
    grants = get_race_feat_grants(race_id, subrace_id)
    if not grants:
        return [], {}, stats

    feat_ids: list[str] = []
    feat_choices: dict[str, dict[str, Any]] = {}
    working_stats = stats.copy()
    pick_total = sum(g.count for g in grants)
    pick_current = 0

    for grant in grants:
        for _ in range(grant.count):
            pick_current += 1
            ctx = _feat_ctx_at_creation(
                working_stats, race_id, subrace_id, background_id
            )
            available = list_available_feats(ctx, feat_ids)
            if not available:
                _print_screen_header(
                    get_string(strings, "character.feat_caption")
                )
                print(get_string(strings, "character.feat_none_available"))
                print()
                return None

            _print_screen_header(get_string(strings, "character.feat_caption"))
            print(
                get_string(
                    strings,
                    "character.feat_pick_heading",
                    current=pick_current,
                    total=pick_total,
                )
            )
            print()
            for idx, feat in enumerate(available, 1):
                if idx > 1:
                    print(
                        f"  {Fore.LIGHTBLACK_EX}{SEPARATOR}{Style.RESET_ALL}"
                    )
                print()
                print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. ", end="")
                _print_feat_details(strings, feat)

            print()
            choice = _deps.get_int_input(
                get_string(
                    strings, "character.feat_prompt", count=len(available)
                ),
                0,
                len(available),
                strings,
            )
            if choice == 0:
                return None

            selected = available[choice - 1]
            feat_id = str(selected.get("id", ""))
            sub = _resolve_feat_subchoices(
                strings,
                feat_id,
                working_stats,
                language,
                known_languages=known_languages,
            )
            if sub is None:
                return None

            feat_choices[feat_id] = sub
            feat_ids.append(feat_id)
            bonuses = resolve_feat_ability_bonuses(feat_id, sub)
            working_stats = _deps.apply_bonuses_to_stats(
                working_stats, bonuses
            )

    final_stats = apply_feats_to_stats(stats, feat_ids, feat_choices)
    return feat_ids, feat_choices, final_stats


def select_level_up_feat_or_asi(
    strings: StringsDict,
    character: Any,
    new_level: int,
    language: str = "ru",
) -> tuple[Any, StatMap, list[str], dict[str, dict[str, Any]], str] | None:
    """Выбор ASI или черты при левелапе.

    Возвращает (character, stats, feat_ids, feat_choices, asi_choice_value)
    или None при отмене.
    """
    from dataclasses import replace

    from core.asi import apply_asi_one_two, apply_asi_two_one, cap_stats
    from ui.menus.asi import select_asi_mode, select_asi_stats

    _print_screen_header(
        get_string(
            strings,
            "level_up.asi_feature_heading",
            level=new_level,
        )
    )
    mode = select_asi_mode(strings)
    if mode is None:
        return None

    stats = character.stats.copy()
    feat_ids = list(character.feat_ids)
    feat_choices = dict(character.feat_choices)

    if mode == "asi":
        picks = select_asi_stats(strings, stats)
        if picks is None:
            return None
        if picks[0] == picks[1]:
            stats = apply_asi_two_one(stats, picks[0])
        else:
            stats = apply_asi_one_two(stats, picks[0], picks[1])
        stats = cap_stats(stats)
        updated = replace(character, stats=stats)
        return updated, stats, feat_ids, feat_choices, "asi"

    ctx = _feat_ctx_for_character(character)
    available = list_available_feats(ctx, feat_ids)
    if not available:
        print(get_string(strings, "character.feat_none_available"))
        print()
        return None

    labels = [str(f.get("name", "?")) for f in available]
    choice = _run_numbered_menu(
        strings,
        labels,
        prompt_key="character.feat_prompt",
        back_label_key="character.back",
    )
    if choice is None:
        return None

    selected = available[choice - 1]
    feat_id = str(selected.get("id", ""))
    sub = _resolve_feat_subchoices(
        strings, feat_id, stats, language, known_languages=character.languages
    )
    if sub is None:
        return None

    feat_choices[feat_id] = sub
    feat_ids.append(feat_id)
    bonuses = resolve_feat_ability_bonuses(feat_id, sub)
    stats = cap_stats(_deps.apply_bonuses_to_stats(stats, bonuses))
    updated = replace(
        character,
        stats=stats,
        feat_ids=feat_ids,
        feat_choices=feat_choices,
    )
    asi_value = f"feat:{feat_id}"
    return updated, stats, feat_ids, feat_choices, asi_value
