"""Отображение карточек персонажей, рас, классов и характеристик."""

from typing import Any, Literal

from colorama import Fore, Style

from core.backgrounds import load_background_full
from core.classes import (
    get_subclass_choice_level,
    load_classes,
    load_subclasses,
)
from core.dice import ability_modifier
from core.equipment import (
    armor_equipped_hint,
    default_ammunition_pack_size,
    format_dice_for_display,
    get_armor_name,
    get_equipment_item_name,
    get_tool_name,
    get_weapon_name,
    proficiency_token_label,
    weapon_ammunition_item_id,
    weapon_damage_dice,
    weapon_property_hint,
    weapon_range,
    weapon_versatile_dice,
)
from core.grants import (
    ABILITY_INCREASE,
    grants_from_entity,
    grants_of_type,
    normalize_armor_token,
)
from core.inventory import (
    compute_ac,
    default_equipped,
    inventory_excluding_equipped,
    inventory_item_quantity,
    item_display_name,
    main_hand_uses_both_hands,
    weapon_is_two_handed,
    weapon_is_versatile,
)
from core.languages import get_language_name
from core.localization import (
    get_string,
    load_strings,
    resolve_localized_text,
)
from core.models import Character
from core.progression import (
    ASI_FEATURE_ID,
    features_up_to_level,
    subclass_is_active,
)
from core.races import (
    get_choice_ability_bonus_mechanics,
    get_race_bonuses,
    load_race_full,
)
from core.starting_equipment import (
    STARTING_EQUIPMENT_SECTION_KEYS,
    STARTING_EQUIPMENT_SECTION_ORDER,
    summarize_class_starting_equipment,
)
from core.stats import POINT_BUY_COSTS, STAT_NAMES
from core.types import (
    EquippedState,
    GameDifficulty,
    InventoryItem,
    StatMap,
    StringsDict,
)
from ui.menus._common import (
    SEPARATOR,
    _ability_name,
    _skill_name,
    _stats_caption_line,
)
from ui.menus.expertise import format_expertise_display

# ============================================================================
# Общие хелперы подписей
# ============================================================================


def _localized_string_list(value: Any, language: str) -> list[str]:
    """Локализованный список строк из YAML (ru/en или плоский list)."""
    if isinstance(value, dict):
        raw = value.get(language)
        if not isinstance(raw, list):
            for key in (language, "en", "ru"):
                candidate = value.get(key)
                if isinstance(candidate, list):
                    raw = candidate
                    break
        if isinstance(raw, list):
            return [str(item) for item in raw]
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _grant_type_label(strings: StringsDict, gtype: str) -> str:
    """Локализованное имя типа grant без поля name в YAML."""
    if not gtype:
        return ""
    return get_string(strings, f"character.grant_type_{gtype}", default=gtype)


def _grant_pool_label(
    strings: StringsDict, pool: str, *, gtype: str = ""
) -> str:
    """Локализованная подпись пула выбора (all, common, …)."""
    if not pool:
        return ""
    if pool == "all":
        if gtype == "skill_proficiency":
            return get_string(
                strings,
                "character.grant_pool_all_skills",
                default=pool,
            )
        if gtype == "feat":
            return get_string(
                strings,
                "character.grant_pool_all_feats",
                default=pool,
            )
    direct = get_string(strings, f"character.grant_pool_{pool}", default="")
    if direct:
        return direct
    return pool


def _label_from_catalog(
    catalog: list[dict[str, Any]],
    entity_id: str,
    *,
    default: str | None = None,
) -> str:
    """Имя сущности по id из списка каталога."""
    for item in catalog:
        if item.get("id") == entity_id:
            return str(item.get("name", entity_id))
    return default if default is not None else entity_id


# ============================================================================
# Отображение режима сложности
# ============================================================================


def _difficulty_label(strings: StringsDict, difficulty: GameDifficulty) -> str:
    """Локализованное название режима сложности."""
    mode_key = f"difficulty.{difficulty}"
    mode = get_string(strings, mode_key)
    if mode == mode_key:
        return difficulty
    return mode


def _difficulty_color(difficulty: GameDifficulty) -> str:
    """Цвет для отображения режима сложности."""
    match difficulty:
        case "easy":
            return str(Fore.GREEN)
        case "normal":
            return str(Fore.YELLOW)
        case "hardcore":
            return str(Fore.RED)


# ============================================================================
# Локализованное отображение grants[]
# ============================================================================


def _armor_labels_from_grant(
    grant: dict[str, Any], strings: StringsDict, language: str
) -> str:
    """Локализованные подписи типов доспехов из grant."""
    raw = grant.get("armor_types", grant.get("armors", []))
    if not isinstance(raw, list) or not raw:
        return ""
    tokens = [normalize_armor_token(str(item)) for item in raw]
    return ", ".join(
        proficiency_token_label(token, strings, language) for token in tokens
    )


def _damage_type_labels(strings: StringsDict, types: list[Any]) -> str:
    """Локализованные подписи типов урона."""
    labels: list[str] = []
    for item in types:
        token = str(item)
        labels.append(
            get_string(
                strings, f"character.grant_damage_{token}", default=token
            )
        )
    return ", ".join(labels)


def _spell_name(strings: StringsDict, spell_id: str) -> str:
    """Локализованное имя заклинания."""
    return get_string(strings, f"spells.{spell_id}", default=spell_id)


def _spell_uses_label(strings: StringsDict, spell: dict[str, Any]) -> str:
    """Подпись лимита использования заклинания."""
    uses = spell.get("uses")
    if uses == "at_will":
        return get_string(strings, "character.grant_spell_uses_at_will")
    recharge = spell.get("recharge")
    if uses is not None and recharge:
        return get_string(
            strings,
            "character.grant_spell_uses_recharge",
            uses=uses,
            recharge=recharge,
        )
    return str(uses) if uses is not None else ""


def _format_spellcasting_grant(
    grant: dict[str, Any], strings: StringsDict
) -> str:
    """Описание расовой магии (список заклинаний)."""
    raw_spells = grant.get("spells", [])
    if not isinstance(raw_spells, list) or not raw_spells:
        return ""
    entries: list[str] = []
    for spell in raw_spells:
        if not isinstance(spell, dict):
            continue
        spell_id = str(spell.get("name", ""))
        if not spell_id:
            continue
        uses = _spell_uses_label(strings, spell)
        entries.append(
            get_string(
                strings,
                "character.grant_spellcasting_entry",
                spell=_spell_name(strings, spell_id),
                uses=uses,
            )
        )
    if not entries:
        return ""
    ability = str(grant.get("ability", ""))
    ability_label = _ability_name(strings, ability) if ability else ""
    return get_string(
        strings,
        "character.grant_spellcasting_list",
        spells="; ".join(entries),
        ability=ability_label,
    )


def _format_disadvantage_grant(
    grant: dict[str, Any], strings: StringsDict
) -> str:
    """Описание помехи от условия окружения."""
    condition = str(grant.get("condition", ""))
    if condition == "direct_sunlight":
        return get_string(strings, "character.grant_disadvantage_sunlight")
    affected = grant.get("affected", [])
    affected_labels: list[str] = []
    if isinstance(affected, list):
        for item in affected:
            token = str(item)
            affected_labels.append(
                get_string(
                    strings,
                    f"character.grant_affected_{token}",
                    default=token,
                )
            )
    condition_label = get_string(
        strings,
        f"character.grant_condition_{condition}",
        default=condition,
    )
    return get_string(
        strings,
        "character.grant_disadvantage_generic",
        affected=", ".join(affected_labels),
        condition=condition_label,
    )


def _format_skill_proficiency_labels(
    strings: StringsDict, skills: list[Any]
) -> str:
    """Список навыков с префиксом владения."""
    labels = [
        get_string(
            strings,
            "character.grant_skill_proficiency",
            skill=_skill_name(strings, str(skill_id)),
        )
        for skill_id in skills
    ]
    return ", ".join(labels)


def _grant_display_name(grant: dict[str, Any], strings: StringsDict) -> str:
    """Имя особенности: name из YAML или локализованный type."""
    name = str(grant.get("name", "")).strip()
    if name:
        return name
    return _grant_type_label(strings, str(grant.get("type", "")))


def _grant_description(
    grant: dict[str, Any],
    strings: StringsDict,
    language: str = "ru",
) -> str:
    """Краткое описание grant для экрана расы или предыстории."""
    gtype = str(grant.get("type", ""))
    explicit = str(grant.get("description", "")).strip()
    if explicit:
        return explicit
    if gtype == "hit_point_bonus" and grant.get("per_level"):
        amount = int(grant.get("amount", 0))
        if amount > 0:
            return get_string(
                strings,
                "character.grant_hp_per_level",
                amount=amount,
            )
    if gtype == ABILITY_INCREASE and grant.get("choice"):
        return get_string(
            strings,
            "character.stats_choice_bonus_subrace_info",
            count=int(grant.get("count", 1)),
            value=int(grant.get("amount", 1)),
        )
    if grant.get("choice"):
        return _grant_choice_description(grant, strings, language, gtype)

    match gtype:
        case "tool_proficiency":
            raw_tools = grant.get("tools", [])
            if isinstance(raw_tools, list) and raw_tools:
                return ", ".join(
                    get_tool_name(str(tool_id), language)
                    for tool_id in raw_tools
                )
        case "spellcasting":
            return _format_spellcasting_grant(grant, strings)
        case "cantrip":
            source = str(grant.get("source", ""))
            ability = str(grant.get("ability", ""))
            if source and ability:
                return get_string(
                    strings,
                    "character.grant_cantrip_choice",
                    source=source,
                    ability=_ability_name(strings, ability),
                )
        case "immunity":
            if grant.get("effect") == "magical_sleep":
                return get_string(
                    strings, "character.grant_immunity_magical_sleep"
                )
        case "disadvantage":
            return _format_disadvantage_grant(grant, strings)
        case "skill_bonus" if grant.get("expertise"):
            skill = grant.get("skill")
            if isinstance(skill, str) and skill:
                return get_string(
                    strings,
                    "character.grant_skill_expertise",
                    skill=_skill_name(strings, skill),
                )
        case "skill_proficiency":
            return _skill_proficiency_description(grant, strings)
        case "armor_proficiency":
            return _armor_labels_from_grant(grant, strings, language) or ""
        case "speed_ignore_penalty":
            armor_labels = _armor_labels_from_grant(grant, strings, language)
            if armor_labels:
                return get_string(
                    strings,
                    "character.grant_speed_ignore",
                    armors=armor_labels,
                )
        case "resistance":
            return _resistance_description(grant, strings)
        case "speed_bonus":
            speed = grant.get("amount")
            if speed is not None:
                return get_string(
                    strings,
                    "character.grant_speed_value",
                    speed=speed,
                )
        case "advantage":
            return _advantage_description(grant, strings)
        case "rest" if grant.get("duration") is not None:
            return get_string(
                strings,
                "character.grant_rest_trance",
                duration=int(grant["duration"]),
            )
        case "darkvision" if grant.get("range") is not None:
            return get_string(
                strings,
                "character.grant_darkvision",
                range=grant["range"],
            )

    weapons = grant.get("weapons", [])
    if isinstance(weapons, list) and weapons:
        return ", ".join(get_weapon_name(str(w), language) for w in weapons)
    return ""


def _grant_choice_description(
    grant: dict[str, Any],
    strings: StringsDict,
    language: str,
    gtype: str,
) -> str:
    """Описание grant с ``choice: true``."""
    count = int(grant.get("count", 1))
    tools = grant.get("tools", [])
    if gtype == "tool_proficiency" and isinstance(tools, list) and tools:
        tool_labels = ", ".join(
            get_tool_name(str(tool_id), language) for tool_id in tools
        )
        return get_string(
            strings,
            "character.grant_choice_tools",
            count=count,
            tools=tool_labels,
        )
    pool = str(grant.get("pool", grant.get("from", "")))
    if pool:
        pool_label = _grant_pool_label(strings, pool, gtype=gtype)
        return get_string(
            strings,
            "character.grant_choice_pool",
            count=count,
            pool=pool_label,
        )
    return get_string(strings, "character.grant_choice", count=count)


def _skill_proficiency_description(
    grant: dict[str, Any],
    strings: StringsDict,
) -> str:
    """Описание grant skill_proficiency."""
    skills = grant.get("skills", grant.get("skill"))
    if isinstance(skills, list) and skills:
        return _format_skill_proficiency_labels(strings, skills)
    if isinstance(skills, str) and skills:
        return get_string(
            strings,
            "character.grant_skill_proficiency",
            skill=_skill_name(strings, skills),
        )
    return ""


def _resistance_description(
    grant: dict[str, Any],
    strings: StringsDict,
) -> str:
    """Описание grant resistance / advantage_saves."""
    damage_types = grant.get("damage_types", [])
    advantage_saves = grant.get("advantage_saves", [])
    dmg_labels = (
        _damage_type_labels(strings, damage_types)
        if isinstance(damage_types, list)
        else ""
    )
    save_labels = (
        _damage_type_labels(strings, advantage_saves)
        if isinstance(advantage_saves, list)
        else ""
    )
    if save_labels and dmg_labels:
        return get_string(
            strings,
            "character.grant_resistance_full",
            saves=save_labels,
            types=dmg_labels,
        )
    if dmg_labels:
        return get_string(
            strings,
            "character.grant_resistance",
            types=dmg_labels,
        )
    if save_labels:
        return get_string(
            strings,
            "character.grant_advantage_saves",
            types=save_labels,
        )
    return ""


def _advantage_description(
    grant: dict[str, Any],
    strings: StringsDict,
) -> str:
    """Описание grant advantage."""
    skill = grant.get("skill")
    terrain = grant.get("terrain")
    if isinstance(skill, str) and skill and terrain:
        terrain_label = get_string(
            strings,
            f"character.grant_terrain_{terrain}",
            default=str(terrain),
        )
        return get_string(
            strings,
            "character.grant_advantage_skill_terrain",
            skill=_skill_name(strings, skill),
            terrain=terrain_label,
        )
    if grant.get("save") and grant.get("effect"):
        effect_key = str(grant["effect"])
        effect_label = get_string(
            strings,
            f"character.grant_effect_{effect_key}",
            default=effect_key,
        )
        return get_string(
            strings,
            "character.grant_advantage_save",
            save=_ability_name(strings, str(grant["save"])),
            effect=effect_label,
        )
    return ""


def format_grant_line_text(
    grant: dict[str, Any],
    strings: StringsDict,
    language: str = "ru",
) -> str:
    """Локализованная строка одной особенности (без print)."""
    name = _grant_display_name(grant, strings)
    desc = _grant_description(grant, strings, language)
    if desc:
        return get_string(
            strings,
            "character.feature_line",
            name=name,
            desc=desc,
        )
    return get_string(
        strings,
        "character.feature_line_name_only",
        name=name,
    )


def format_grant_lines(
    grants: list[dict[str, Any]],
    strings: StringsDict,
    language: str = "ru",
) -> list[str]:
    """Строки особенностей для списка grants."""
    return [
        format_grant_line_text(grant, strings, language) for grant in grants
    ]


def _print_grant_line(
    grant: dict[str, Any],
    strings: StringsDict,
    language: str,
) -> None:
    """Вывести одну строку особенности."""
    print(format_grant_line_text(grant, strings, language))


# ============================================================================
# Отображение рас и расовых бонусов
# ============================================================================


def _has_choice_ability_bonuses(info: dict[str, Any]) -> bool:
    """Есть ли выборный бонус характеристик в grants без ability_bonuses."""
    if info.get("ability_bonuses"):
        return False
    for grant in grants_of_type(grants_from_entity(info), ABILITY_INCREASE):
        if grant.get("choice"):
            return True
    return False


def _choice_language_grants(
    grants: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Выборные языковые grants из списка."""
    return [
        grant
        for grant in grants_of_type(grants, "language")
        if grant.get("choice")
    ]


def _format_language_choice_extra(
    strings: StringsDict, grant: dict[str, Any]
) -> str:
    """Краткая подпись выборного языка для строки «Языки»."""
    count = int(grant.get("count", 1))
    pool = str(grant.get("pool", grant.get("from", "common")))
    pool_label = _grant_pool_label(strings, pool, gtype="language")
    return get_string(
        strings,
        "character.language_race_extra",
        count=count,
        pool=pool_label,
    )


def _print_race_grants(
    info: dict[str, Any],
    strings: StringsDict,
    language: str = "ru",
    *,
    omit_choice_languages: bool = False,
) -> None:
    """Вывести особенности из grants[] сущности (без наследования от расы)."""
    grants = grants_from_entity(info)
    visible: list[dict[str, Any]] = []
    for grant in grants:
        if (
            omit_choice_languages
            and grant.get("type") == "language"
            and grant.get("choice")
        ):
            continue
        if (
            _has_choice_ability_bonuses(info)
            and grant.get("type") == ABILITY_INCREASE
            and grant.get("choice")
        ):
            continue
        visible.append(grant)
    if not visible:
        return
    print(get_string(strings, "character.features_label"))
    for grant in visible:
        _print_grant_line(grant, strings, language)


def _print_choice_ability_from_grants(
    info: dict[str, Any], strings: StringsDict
) -> None:
    """Выборный бонус характеристик из grants, если нет ability_bonuses."""
    for grant in grants_of_type(grants_from_entity(info), ABILITY_INCREASE):
        if not grant.get("choice"):
            continue
        count = int(grant.get("count", 1))
        amount = int(grant.get("amount", 1))
        choice_info = get_string(
            strings,
            "character.stats_choice_bonus_subrace_info",
            count=count,
            value=amount,
        )
        print(
            get_string(
                strings,
                "character.ability_bonuses_label",
                bonuses=choice_info,
            )
        )
        return


def _print_race_info(
    info: dict[str, Any],
    strings: StringsDict,
    language: str = "ru",
) -> None:
    """Вывести подробности расы или подрасы."""
    desc = info.get("description", "")
    if desc:
        print(get_string(strings, "character.race_description", desc=desc))

    speed = info.get("speed")
    if speed:
        print(get_string(strings, "character.speed_label", speed=speed))

    entity_grants = grants_from_entity(info)
    choice_languages = _choice_language_grants(entity_grants)
    fixed_languages = info.get("languages", [])
    lang_parts: list[str] = []
    if isinstance(fixed_languages, list):
        lang_parts.extend(
            get_language_name(str(lang), language) for lang in fixed_languages
        )
    merge_choice_into_languages = bool(fixed_languages and choice_languages)
    if merge_choice_into_languages:
        for grant in choice_languages:
            lang_parts.append(_format_language_choice_extra(strings, grant))
    if lang_parts:
        print(
            get_string(
                strings,
                "character.languages_label",
                langs=", ".join(lang_parts),
            )
        )

    bonuses = info.get("ability_bonuses", {})
    if bonuses:
        bonus_parts = []
        for stat, val in bonuses.items():
            stat_label = _ability_name(strings, stat)
            bonus_parts.append(
                f"{Fore.CYAN}{stat_label}{Style.RESET_ALL}"
                f"+{Fore.GREEN}{val}{Style.RESET_ALL}"
            )
        bonuses_str = ", ".join(bonus_parts)
        print(
            get_string(
                strings, "character.ability_bonuses_label", bonuses=bonuses_str
            )
        )
    else:
        _print_choice_ability_from_grants(info, strings)

    _print_race_grants(
        info,
        strings,
        language,
        omit_choice_languages=merge_choice_into_languages,
    )


def _format_bonuses(bonuses: StatMap, strings: StringsDict) -> str:
    """Отформатировать расовые бонусы для отображения."""
    if not bonuses:
        return (
            f"{Fore.CYAN}"
            f"{get_string(strings, 'character.stats_no_bonuses')}"
            f"{Style.RESET_ALL}"
        )

    bonus_strs = []
    for stat, bonus in bonuses.items():
        stat_name = _ability_name(strings, stat)
        bonus_strs.append(
            get_string(
                strings,
                "character.stats_bonus_format",
                stat=stat_name,
                bonus=bonus,
            )
        )

    bonus_line = ", ".join(bonus_strs)
    race_msg = get_string(
        strings, "character.stats_race_bonuses", bonuses=bonus_line
    )
    return f"{Fore.CYAN}{race_msg}{Style.RESET_ALL}"


def _print_race_bonuses(
    strings: StringsDict,
    race_id: str,
    subrace_id: str | None,
) -> None:
    """Вывести блок расовых бонусов."""
    bonuses = get_race_bonuses(race_id, subrace_id)
    if bonuses:
        print(_format_bonuses(bonuses, strings))
        return

    mechanics = get_choice_ability_bonus_mechanics(race_id, subrace_id)
    if mechanics:
        count = int(mechanics.get("count", 1))
        value = int(mechanics.get("amount", 1))
        pending_msg = get_string(
            strings,
            "character.stats_choice_bonus_pending",
            count=count,
            value=value,
        )
        print(f"{Fore.CYAN}{pending_msg}{Style.RESET_ALL}")
        return

    print(_format_bonuses(bonuses, strings))


# ============================================================================
# Отображение предысторий
# ============================================================================


def _print_background_grants(
    info: dict[str, Any], strings: StringsDict, language: str = "ru"
) -> None:
    """Владения предыстории из grants[] (навыки, языки, инструменты)."""
    grants = grants_from_entity(info)
    if not grants:
        return
    print(get_string(strings, "character.background_proficiencies_label"))
    for grant in grants:
        name = _grant_display_name(grant, strings)
        desc = _grant_description(grant, strings, language)
        print(
            get_string(
                strings,
                "character.background_grant_line",
                name=name,
                desc=desc,
            )
        )


def _print_background_info(
    info: dict[str, Any], strings: StringsDict, language: str = "ru"
) -> None:
    """Подробности одной предыстории для экрана выбора."""
    desc = info.get("description", "")
    if desc:
        print(f"     {desc}")

    _print_background_grants(info, strings, language)

    equipment = _localized_string_list(info.get("equipment", {}), language)
    if equipment:
        equipment_line = ", ".join(equipment)
        print(
            get_string(
                strings,
                "character.background_equipment_label",
                list=equipment_line,
            )
        )

    feature = info.get("feature", {})
    if isinstance(feature, dict) and feature.get("name"):
        feat_desc = str(feature.get("description", "")).strip()
        if feat_desc:
            print(
                get_string(
                    strings,
                    "character.background_feature_full",
                    name=feature["name"],
                    desc=feat_desc,
                )
            )
        else:
            print(
                get_string(
                    strings,
                    "character.background_feature_label",
                    name=feature["name"],
                )
            )


# ============================================================================
# Отображение характеристик при генерации
# ============================================================================


def _format_ability_modifier(mod: int) -> str:
    """Модификатор для компактной строки: (+3), (-2) или пусто при 0."""
    if mod == 0:
        return ""
    sign = "+" if mod > 0 else ""
    return f"({sign}{mod})"


def _colored_ability_modifier(mod: int) -> str:
    """Модификатор с цветом: зелёный для +, красный для −."""
    text = _format_ability_modifier(mod)
    if not text:
        return ""
    color = Fore.RED if mod < 0 else Fore.GREEN
    return f"{color}{text}{Style.RESET_ALL}"


def _format_character_stats_compact(
    char: Character, strings: StringsDict
) -> str:
    """Компактная строка характеристик: значение и модификатор."""
    if not char.stats:
        return ""

    parts = []
    for stat in STAT_NAMES:
        value = char.stats.get(stat)
        if value is None:
            continue
        abbr = _ability_name(strings, stat)[:3]
        mod = ability_modifier(int(value))
        mod_part = _colored_ability_modifier(mod)
        segment = (
            f"{Fore.CYAN}{abbr}{Style.RESET_ALL} "
            f"{Fore.YELLOW}{value:>2}{Style.RESET_ALL}"
        )
        if mod_part:
            segment = f"{segment} {mod_part}"
        parts.append(segment)
    return "  ".join(parts)


def _print_final_stat_line(
    strings: StringsDict,
    stat: str,
    value: int,
    race_bonuses: StatMap,
) -> None:
    """Вывести итоговую характеристику с пометкой расового бонуса (+N)."""
    stat_name = _ability_name(strings, stat)
    bonus = race_bonuses.get(stat, 0)
    if bonus > 0:
        print(
            f"  {stat_name}: {Fore.YELLOW}{value}{Style.RESET_ALL} "
            f"{Fore.GREEN}(+{bonus}){Style.RESET_ALL}"
        )
        return
    print(f"  {stat_name}: {Fore.YELLOW}{value}{Style.RESET_ALL}")


def _print_stats_generation_header(
    strings: StringsDict,
    race_id: str | None = None,
    subrace_id: str | None = None,
) -> None:
    """Заголовок генерации характеристик и расовые бонусы."""
    print(SEPARATOR)
    print(_stats_caption_line(strings))
    print(SEPARATOR)
    print()
    if race_id is not None:
        _print_race_bonuses(strings, race_id, subrace_id)
        print()


def _print_point_buy_cost_table(strings: StringsDict) -> None:
    """Таблица стоимости значений характеристик (point-buy)."""
    title = get_string(strings, "character.stats_point_buy_price_table")
    value_hdr = get_string(strings, "character.stats_point_buy_price_value")
    cost_hdr = get_string(strings, "character.stats_point_buy_price_cost")
    print(f"{Fore.GREEN}{title}{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}{value_hdr:>5}  {cost_hdr:>5}{Style.RESET_ALL}")
    for value in sorted(POINT_BUY_COSTS):
        cost = POINT_BUY_COSTS[value]
        print(
            f"  {Fore.CYAN}{value:>5}{Style.RESET_ALL}  "
            f"{Fore.CYAN}{cost:>5}{Style.RESET_ALL}"
        )
    print()


# ============================================================================
# Подписи и поля заголовка карточки персонажа
# ============================================================================


def _format_character_feats(char: Character, language: str = "ru") -> str:
    """Список названий черт персонажа через запятую."""
    from core.feats import load_feat

    names: list[str] = []
    for feat_id in char.feat_ids:
        feat = load_feat(feat_id)
        raw_name = feat.get("name", feat_id)
        if isinstance(raw_name, dict):
            name = resolve_localized_text(raw_name, language, fallback=feat_id)
        else:
            name = str(raw_name)
        names.append(name)
    return ", ".join(names)


def _character_base_race_label(char: Character, language: str = "ru") -> str:
    """Читаемое название базовой расы персонажа."""
    race_full = load_race_full(char.race, language)
    name = race_full.get("name")
    if name:
        return str(name)
    return char.race


def _character_subrace_label(
    char: Character, language: str = "ru"
) -> str | None:
    """Читаемое название подрасы или None, если подрасы нет."""
    if not char.subrace:
        return None

    race_full = load_race_full(char.race, language)
    subraces = race_full.get("subraces", {})
    if isinstance(subraces, dict):
        subrace_info = subraces.get(char.subrace, {})
        if isinstance(subrace_info, dict):
            name = subrace_info.get("name")
            if name:
                name_str = str(name)
                if "(" in name_str and name_str.endswith(")"):
                    return name_str.split("(", maxsplit=1)[1].rstrip(")")
                return name_str
    return char.subrace


def _empty_field_value(strings: StringsDict) -> str:
    """Плейсхолдер для пустого поля карточки персонажа."""
    empty = get_string(strings, "choose_character.field_empty")
    return f"{Fore.LIGHTBLACK_EX}{empty}{Style.RESET_ALL}"


def _print_labeled_field(
    strings: StringsDict,
    label_key: str,
    value: str,
    indent: str = "     ",
) -> None:
    """Вывести строку «подпись: значение» с цветной подписью."""
    label = get_string(strings, label_key)
    print(
        f"{indent}" f"{Fore.LIGHTBLACK_EX}{label}{Style.RESET_ALL} " f"{value}"
    )


# ============================================================================
# Секции карточки персонажа
# ============================================================================


def _format_proficiency_token_list(
    strings: StringsDict,
    tokens: list[str],
    *,
    language: str = "ru",
) -> str:
    """Локализованный список токенов владений."""
    names = [proficiency_token_label(t, strings, language) for t in tokens]
    return ", ".join(names)


def _print_character_proficiencies(
    char: Character,
    strings: StringsDict,
    language: str,
    *,
    indent: str = "     ",
) -> None:
    """Владения персонажа: заголовок и категории с отступом."""
    categories: tuple[tuple[list[str], str], ...] = (
        (
            char.armor_proficiencies,
            "choose_character.field_proficiencies_armor",
        ),
        (
            char.weapon_proficiencies,
            "choose_character.field_proficiencies_weapons",
        ),
        (
            char.tool_proficiencies,
            "choose_character.field_proficiencies_tools",
        ),
    )
    has_any = any(tokens for tokens, _ in categories)
    if not has_any:
        _print_labeled_field(
            strings,
            "choose_character.field_proficiencies",
            _empty_field_value(strings),
            indent=indent,
        )
        return

    header = get_string(strings, "choose_character.field_proficiencies")
    print(f"{indent}{Fore.LIGHTBLACK_EX}{header}{Style.RESET_ALL}")
    sub_indent = f"{indent}  "
    for tokens, label_key in categories:
        if not tokens:
            continue
        value = _format_proficiency_token_list(
            strings,
            tokens,
            language=language,
        )
        cat_label = get_string(strings, label_key)
        print(
            f"{sub_indent}{Fore.LIGHTBLACK_EX}{cat_label}{Style.RESET_ALL} "
            f"{Fore.CYAN}{value}{Style.RESET_ALL}"
        )


def _print_character_skills_and_expertise(
    char: Character,
    strings: StringsDict,
    *,
    indent: str = "     ",
) -> None:
    """Навыки и компетентность на карточке персонажа."""
    if char.skills:
        skills_line = ", ".join(
            _skill_name(strings, skill_id) for skill_id in char.skills
        )
        skills_display = f"{Fore.CYAN}{skills_line}{Style.RESET_ALL}"
    else:
        skills_display = _empty_field_value(strings)
    _print_labeled_field(
        strings,
        "choose_character.field_skills",
        skills_display,
        indent=indent,
    )

    expertise_line = format_expertise_display(
        strings, char.skill_expertise, char.tool_expertise
    )
    expertise_display = (
        f"{Fore.CYAN}{expertise_line}{Style.RESET_ALL}"
        if expertise_line
        else _empty_field_value(strings)
    )
    _print_labeled_field(
        strings,
        "choose_character.field_expertise",
        expertise_display,
        indent=indent,
    )


def _print_character_saving_throws(
    char: Character,
    strings: StringsDict,
    *,
    indent: str = "     ",
) -> None:
    """Спасброски на карточке персонажа."""
    if not char.save_proficiencies:
        return
    parts: list[str] = []
    for ability_id in char.save_proficiencies:
        name = _ability_name(strings, ability_id)
        parts.append(name)
    value = f"{Fore.CYAN}{', '.join(parts)}{Style.RESET_ALL}"
    _print_labeled_field(
        strings,
        "choose_character.field_saving_throws",
        value,
        indent=indent,
    )


def _print_character_equipment(
    char: Character,
    strings: StringsDict,
    language: str,
    *,
    indent: str = "     ",
) -> None:
    """Экипировка, КД и инвентарь на карточке персонажа."""
    if char.equipped or char.inventory:
        ac = compute_ac(char)
        ac_display = f"{Fore.GREEN}{ac}{Style.RESET_ALL}"
        _print_labeled_field(
            strings,
            "choose_character.field_ac",
            ac_display,
            indent=indent,
        )
        equipped, off_hand_muted = get_equipped_display(char, language)
        header = get_string(strings, "choose_character.field_equipped")
        print(f"{indent}{Fore.LIGHTBLACK_EX}{header}{Style.RESET_ALL}")
        sub_indent = f"{indent}  "
        empty = get_string(strings, "choose_character.field_equipped_empty")
        slot_order = (
            ("armor", "choose_character.field_equipped_armor"),
            ("main_hand", "choose_character.field_equipped_main"),
            ("damage", "choose_character.field_equipped_damage"),
            ("off_hand", "choose_character.field_equipped_off"),
            ("ammunition", "choose_character.field_equipped_ammunition"),
            ("distance", "choose_character.field_equipped_range"),
        )
        hint_keys = {
            "armor": "armor_hint",
            "main_hand": "main_hand_hint",
            "off_hand": "off_hand_hint",
        }
        for key, label_key in slot_order:
            if key == "damage":
                if "damage_one_dice" not in equipped:
                    continue
            elif key not in equipped:
                continue
            cat_label = get_string(strings, label_key)
            if key == "damage":
                one = equipped["damage_one_dice"]
                two = equipped["damage_two_dice"]
                active = equipped["damage_active"]
                sep = f"{Fore.LIGHTBLACK_EX} | {Style.RESET_ALL}"
                if active == "one":
                    dice_line = (
                        f"{Fore.CYAN}{one}{Style.RESET_ALL}{sep}"
                        f"{Fore.LIGHTBLACK_EX}{two}{Style.RESET_ALL}"
                    )
                else:
                    dice_line = (
                        f"{Fore.LIGHTBLACK_EX}{one}{Style.RESET_ALL}{sep}"
                        f"{Fore.CYAN}{two}{Style.RESET_ALL}"
                    )
                print(
                    f"{sub_indent}{Fore.LIGHTBLACK_EX}"
                    f"{cat_label}{Style.RESET_ALL} {dice_line}"
                )
                continue
            value = equipped.get(key, empty)
            hint = equipped.get(hint_keys.get(key, ""), "")
            muted_off = key == "off_hand" and off_hand_muted
            if value == empty or muted_off:
                value_color = Fore.LIGHTBLACK_EX
            else:
                value_color = Fore.CYAN
            print(
                f"{sub_indent}{Fore.LIGHTBLACK_EX}"
                f"{cat_label}{Style.RESET_ALL} "
                f"{value_color}{value}{Style.RESET_ALL}",
                end="",
            )
            if hint and key in hint_keys:
                print(f" {Fore.LIGHTBLACK_EX}({hint})" f"{Style.RESET_ALL}")
            else:
                print()
    if char.inventory:
        inv_line = format_inventory_line(
            char.inventory, language, equipped=char.equipped
        )
        if inv_line:
            inv_display = f"{Fore.CYAN}{inv_line}{Style.RESET_ALL}"
            _print_labeled_field(
                strings,
                "choose_character.field_inventory",
                inv_display,
                indent=indent,
            )


# ============================================================================
# Отображение инвентаря и экипировки
# ============================================================================


def format_inventory_line(
    inventory: list[InventoryItem],
    language: str = "ru",
    *,
    equipped: EquippedState | None = None,
) -> str:
    """Сжатый список инвентаря для UI (без экипированных предметов)."""
    display_items = inventory_excluding_equipped(inventory, equipped)
    parts: list[str] = []
    for item in display_items:
        kind = str(item.get("kind", ""))
        item_id = str(item.get("id", ""))
        qty = int(item.get("qty", 1))
        name = item_display_name(kind, item_id, language)
        if qty > 1:
            parts.append(f"{name} ×{qty}")
        else:
            parts.append(name)
    return ", ".join(parts)


def _versatile_active_grip(
    equipped: EquippedState,
) -> Literal["one_handed", "two_handed"]:
    """Текущий режим универсального оружия."""
    grip = equipped.get("main_hand_grip")
    if grip == "one_handed":
        return "one_handed"
    if grip == "two_handed":
        return "two_handed"
    if main_hand_uses_both_hands(equipped):
        return "two_handed"
    return "one_handed"


def _versatile_grip_hint(
    weapon_id: str,
    equipped: EquippedState,
    strings: StringsDict,
) -> str:
    """Подсказка хвата универсального оружия (одна / две руки)."""
    if not weapon_is_versatile(weapon_id):
        return ""
    if _versatile_active_grip(equipped) == "two_handed":
        key = "choose_character.field_equipped_versatile_grip_two"
    else:
        key = "choose_character.field_equipped_versatile_grip_one"
    return get_string(strings, key)


def format_versatile_damage_dice(
    weapon_id: str,
    equipped: EquippedState,
    language: str = "ru",
) -> tuple[str, str, str] | None:
    """Кости универсального оружия и активный режим: (1к8, 1к10, one|two)."""
    if not weapon_is_versatile(weapon_id):
        return None
    one_dice = format_dice_for_display(weapon_damage_dice(weapon_id), language)
    two_dice = format_dice_for_display(
        weapon_versatile_dice(weapon_id), language
    )
    active = (
        "two" if _versatile_active_grip(equipped) == "two_handed" else "one"
    )
    return one_dice, two_dice, active


def _loaded_ammunition_qty(
    inventory: list[InventoryItem], ammo_item_id: str
) -> int:
    """Боеприпасы «под рукой»: из инвентаря, до ёмкости колчана/сумки."""
    in_inv = inventory_item_quantity(inventory, "equipment", ammo_item_id)
    pack = default_ammunition_pack_size(ammo_item_id)
    return min(in_inv, pack) if in_inv > 0 else 0


def _equipped_weapon_for_range(equipped: EquippedState) -> str | None:
    """Оружие для строки дистанции (основная рука, затем вторая)."""
    for slot in ("main_hand", "off_hand"):
        weapon_id = equipped.get(slot)
        if isinstance(weapon_id, str) and weapon_range(weapon_id):
            return weapon_id
    return None


def get_equipped_display(
    character: Character,
    language: str = "ru",
) -> tuple[dict[str, str], bool]:
    """Локализованные подписи экипировки; bool — серая подпись второй руки."""
    strings = load_strings(language)
    empty = get_string(strings, "choose_character.field_equipped_empty")
    equipped = character.equipped or default_equipped()
    result: dict[str, str] = {}
    off_hand_muted = False
    armor_id = equipped.get("armor")
    if isinstance(armor_id, str) and armor_id:
        result["armor"] = item_display_name("armor", armor_id, language)
        armor_hint = armor_equipped_hint(armor_id, strings, language)
        if armor_hint:
            result["armor_hint"] = armor_hint
    else:
        result["armor"] = empty
    main_hand = equipped.get("main_hand")
    if isinstance(main_hand, str) and main_hand:
        result["main_hand"] = item_display_name("weapon", main_hand, language)
        hint_parts: list[str] = []
        prop_hint = weapon_property_hint(main_hand, strings, language)
        if prop_hint:
            hint_parts.append(prop_hint)
        grip_hint = _versatile_grip_hint(main_hand, equipped, strings)
        if grip_hint:
            hint_parts.append(grip_hint)
        if hint_parts:
            result["main_hand_hint"] = ", ".join(hint_parts)
        damage_dice = format_versatile_damage_dice(
            main_hand, equipped, language
        )
        if damage_dice:
            one, two, active = damage_dice
            result["damage_one_dice"] = one
            result["damage_two_dice"] = two
            result["damage_active"] = active
    else:
        result["main_hand"] = empty
    if main_hand_uses_both_hands(equipped) and isinstance(main_hand, str):
        if weapon_is_two_handed(main_hand):
            label_key = "choose_character.field_equipped_off_two_handed"
        else:
            label_key = "choose_character.field_equipped_off_versatile"
        result["off_hand"] = get_string(strings, label_key)
        off_hand_muted = True
    elif equipped.get("shield"):
        result["off_hand"] = get_armor_name("shield", language)
    else:
        off_hand = equipped.get("off_hand")
        if isinstance(off_hand, str) and off_hand:
            result["off_hand"] = item_display_name(
                "weapon", off_hand, language
            )
            hint = weapon_property_hint(off_hand, strings, language)
            if hint:
                result["off_hand_hint"] = hint
        else:
            result["off_hand"] = empty
    ammo_weapon = main_hand if isinstance(main_hand, str) else None
    if ammo_weapon:
        ammo_id = weapon_ammunition_item_id(ammo_weapon)
        if ammo_id:
            qty = _loaded_ammunition_qty(character.inventory, ammo_id)
            result["ammunition"] = get_string(
                strings,
                "choose_character.field_equipped_ammunition_value",
                type=get_equipment_item_name(ammo_id, language),
                qty=qty,
            )
    range_weapon = _equipped_weapon_for_range(equipped)
    if range_weapon:
        rng = weapon_range(range_weapon)
        if rng:
            result["distance"] = get_string(
                strings,
                "choose_character.field_equipped_range_value",
                normal=rng["normal"],
                long=rng["long"],
            )
    return result, off_hand_muted


# ============================================================================
# Отображение классов и подклассов
# ============================================================================


def _character_class_label(char: Character, language: str = "ru") -> str:
    """Читаемое название класса персонажа."""
    return _label_from_catalog(
        load_classes(language), char.class_id, default=char.class_id
    )


def _character_subclass_label(
    char: Character, language: str = "ru"
) -> str | None:
    """Читаемое название подкласса или None."""
    if not char.subclass_id:
        return None
    return _label_from_catalog(
        load_subclasses(char.class_id, language),
        char.subclass_id,
        default=char.subclass_id,
    )


def _format_class_proficiencies(
    strings: StringsDict,
    class_info: dict[str, Any],
    language: str = "ru",
) -> str:
    """Сжатая строка владений класса."""
    prof = class_info.get("proficiencies", {})
    if isinstance(prof, dict):
        parts: list[str] = []
        for key in ("armor", "weapons", "tools"):
            raw = prof.get(key, [])
            if isinstance(raw, list) and raw:
                labels = [
                    proficiency_token_label(str(token), strings, language)
                    for token in raw
                ]
                parts.append(", ".join(labels))
        if parts:
            return "; ".join(parts)
    return ""


def _format_class_skills(
    strings: StringsDict,
    class_info: dict[str, Any],
) -> str:
    """Строка навыков класса с локализованными названиями."""
    skills = class_info.get("skill_choices", [])
    count = int(class_info.get("skill_choices_count", 0))
    if not isinstance(skills, list) or not skills:
        return ""
    skill_names = ", ".join(_skill_name(strings, str(s)) for s in skills)
    if count:
        return get_string(
            strings,
            "character.class_skills_summary",
            count=count,
            list=skill_names,
        )
    return skill_names


def _format_class_saving_throws(
    strings: StringsDict,
    class_info: dict[str, Any],
) -> str:
    """Строка спасбросков класса."""
    saves = class_info.get("saving_throws", [])
    if not isinstance(saves, list) or not saves:
        return ""
    names = ", ".join(_ability_name(strings, str(s)) for s in saves)
    return get_string(
        strings,
        "character.class_saving_throws_label",
        list=names,
    )


def _print_class_starting_equipment(
    class_info: dict[str, Any],
    strings: StringsDict,
    language: str,
) -> None:
    """Краткий обзор стартового снаряжения класса по категориям."""
    class_id = str(class_info.get("id", ""))
    if not class_id:
        return
    sections = summarize_class_starting_equipment(class_id, strings, language)
    if not sections:
        return
    label = get_string(strings, "character.class_starting_equipment_label")
    print(f"  {Fore.LIGHTBLACK_EX}{label.strip()}{Style.RESET_ALL}")
    for section_key in STARTING_EQUIPMENT_SECTION_ORDER:
        lines = sections.get(section_key)
        if not lines:
            continue
        heading = get_string(
            strings, STARTING_EQUIPMENT_SECTION_KEYS[section_key]
        )
        print(f"  {Fore.LIGHTBLACK_EX}{heading}{Style.RESET_ALL}")
        for line in lines:
            item_line = get_string(
                strings,
                "character.class_starting_equipment_choice",
                label=line,
            )
            print(f"  {Fore.LIGHTBLACK_EX}{item_line}{Style.RESET_ALL}")


def _print_class_description(desc: str) -> None:
    """Описание класса/подкласса с отступом."""
    if desc:
        print(f"  {Fore.WHITE}{desc}{Style.RESET_ALL}")


def _print_class_meta_line(line: str) -> None:
    """Мета-строка карточки класса (кость хитов, навыки и т.д.)."""
    print(f"{Fore.LIGHTBLACK_EX}{line}{Style.RESET_ALL}")


def _print_features_section_title(strings: StringsDict) -> None:
    """Заголовок блока особенностей."""
    title = get_string(strings, "character.features_label").strip()
    print(f"  {Fore.YELLOW}{Style.BRIGHT}{title}{Style.RESET_ALL}")


def _format_feature_uses(strings: StringsDict, feat: dict[str, Any]) -> str:
    """Дополнение к описанию умения: лимиты использования."""
    uses = ""
    if feat.get("uses_per_rest"):
        uses = get_string(
            strings,
            "character.subclass_feature_uses_rest",
            uses=feat.get("uses_per_rest"),
        )
    elif feat.get("uses_per_day"):
        uses = get_string(
            strings,
            "character.subclass_feature_uses_day",
            uses=feat.get("uses_per_day"),
        )
    if not uses:
        return ""
    return f"{Fore.GREEN}{uses}{Style.RESET_ALL}"


def _split_asi_features(
    features: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Отделить ASI от остальных умений класса."""
    asi_feats: list[dict[str, Any]] = []
    other: list[dict[str, Any]] = []
    for feat in features:
        if feat.get("id") == ASI_FEATURE_ID:
            asi_feats.append(feat)
        else:
            other.append(feat)
    return asi_feats, other


def _format_collapsed_asi_name(
    strings: StringsDict, asi_feats: list[dict[str, Any]]
) -> str:
    """Имя схлопнутого ASI с перечислением уровней."""
    levels = sorted({int(feat.get("level", 0)) for feat in asi_feats})
    levels_label = get_string(
        strings,
        "character.feature_asi_levels",
        levels=", ".join(str(level) for level in levels),
    )
    base_name = str(asi_feats[0].get("name", ""))
    return f"{base_name} ({levels_label})"


def _print_class_features(
    strings: StringsDict, features: list[Any], *, detailed: bool
) -> None:
    """Вывести классовые умения (до 10 уровня)."""
    filtered: list[dict[str, Any]] = features_up_to_level(features)
    if not filtered:
        return
    asi_feats, other_feats = _split_asi_features(filtered)
    _print_features_section_title(strings)
    if asi_feats:
        asi_name = _format_collapsed_asi_name(strings, asi_feats)
        asi_desc = str(asi_feats[0].get("description", ""))
        uses_part = _format_feature_uses(strings, asi_feats[0])
        if detailed:
            print(
                f"    {Fore.CYAN}{Style.BRIGHT}{asi_name}{Style.RESET_ALL}: "
                f"{asi_desc}{uses_part}"
            )
            print()
        else:
            print(
                f"    {Fore.LIGHTBLACK_EX}•{Style.RESET_ALL} "
                f"{Fore.CYAN}{asi_name}{Style.RESET_ALL}: {asi_desc}"
            )
    if detailed:
        by_level: dict[int, list[dict[str, Any]]] = {}
        for feat in other_feats:
            level = int(feat.get("level", 0))
            by_level.setdefault(level, []).append(feat)
        for level in sorted(by_level):
            level_heading = get_string(
                strings, "character.feature_level_heading", level=level
            )
            level_style = (
                f"{Fore.YELLOW}{Style.BRIGHT}{level_heading}"
                f"{Style.RESET_ALL}"
            )
            print(f"  {level_style}")
            for feat in by_level[level]:
                name = str(feat.get("name", ""))
                desc = str(feat.get("description", ""))
                uses_part = _format_feature_uses(strings, feat)
                print(
                    f"    {Fore.CYAN}{Style.BRIGHT}{name}{Style.RESET_ALL}: "
                    f"{desc}{uses_part}"
                )
            print()
    else:
        for feat in other_feats:
            name = str(feat.get("name", ""))
            desc = str(feat.get("description", ""))
            print(
                f"    {Fore.LIGHTBLACK_EX}•{Style.RESET_ALL} "
                f"{Fore.CYAN}{name}{Style.RESET_ALL}: {desc}"
            )


def _print_class_summary(
    class_info: dict[str, Any],
    strings: StringsDict,
    *,
    include_features: bool = True,
    skills_summary: bool = True,
    language: str = "ru",
) -> None:
    """Краткая карточка класса в списке выбора."""
    desc = class_info.get("description", "")
    _print_class_description(str(desc))

    hit_dice = class_info.get("hit_dice", 8)
    hit_line = get_string(
        strings, "character.class_hit_dice_label", hit_dice=hit_dice
    ).strip()
    if ":" in hit_line:
        label, value = hit_line.split(":", 1)
        print(
            f"  {Fore.LIGHTBLACK_EX}{label.strip()}:{Style.RESET_ALL} "
            f"{Fore.CYAN}{value.strip()}{Style.RESET_ALL}"
        )
    else:
        _print_class_meta_line(hit_line)

    prime = class_info.get("prime_ability", "")
    if prime:
        ability = _ability_name(strings, str(prime))
        prefix = get_string(strings, "character.class_prime_ability_label")
        if "{ability}" in prefix:
            prefix = prefix.split("{ability}")[0].rstrip(": ").rstrip()
        print(
            f"  {Fore.LIGHTBLACK_EX}{prefix}:{Style.RESET_ALL} "
            f"{Fore.CYAN}{ability}{Style.RESET_ALL}"
        )

    prof = _format_class_proficiencies(strings, class_info, language)
    if prof:
        label = get_string(strings, "character.class_proficiencies_label")
        if "{proficiencies}" in label:
            label = label.split("{proficiencies}")[0].rstrip(": ")
        print(
            f"  {Fore.LIGHTBLACK_EX}{label}:{Style.RESET_ALL} "
            f"{Fore.CYAN}{prof}{Style.RESET_ALL}"
        )

    skills_line = ""
    if skills_summary:
        skills_line = _format_class_skills(strings, class_info)
    if skills_line:
        label = get_string(strings, "character.class_skills_label")
        if "{skills}" in label:
            label = label.split("{skills}")[0].rstrip(": ")
        print(
            f"  {Fore.LIGHTBLACK_EX}{label}:{Style.RESET_ALL} "
            f"{Fore.CYAN}{skills_line}{Style.RESET_ALL}"
        )

    saves_line = _format_class_saving_throws(strings, class_info)
    if saves_line:
        print(f"  {Fore.LIGHTBLACK_EX}{saves_line.strip()}{Style.RESET_ALL}")

    _print_class_starting_equipment(class_info, strings, language)

    features = class_info.get("features", [])
    if include_features and isinstance(features, list):
        print()
        _print_class_features(strings, features, detailed=False)


def _print_class_info(
    class_info: dict[str, Any], strings: StringsDict
) -> None:
    """Полный обзор класса перед выбором подкласса."""
    _print_class_summary(class_info, strings, include_features=False)
    features = class_info.get("features", [])
    if isinstance(features, list):
        print()
        _print_class_features(strings, features, detailed=True)


def _print_subclass_info(
    subclass_info: dict[str, Any], strings: StringsDict
) -> None:
    """Подробные особенности подкласса."""
    desc = subclass_info.get("description", "")
    _print_class_description(str(desc))

    features = subclass_info.get("features", [])
    if isinstance(features, list) and features:
        print()
        _print_class_features(strings, features, detailed=True)


# ============================================================================
# Отображение карточек персонажей
# ============================================================================


def _print_character_card(
    idx: int,
    char: Character,
    strings: StringsDict,
    language: str = "ru",
) -> None:
    """Вывести карточку персонажа в списке выбора."""
    mode = _difficulty_label(strings, char.difficulty)
    mode_color = _difficulty_color(char.difficulty)
    base_race = _character_base_race_label(char, language)
    subrace = _character_subrace_label(char, language)
    class_label = _character_class_label(char, language)
    indent = "     "

    print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}.")

    _print_labeled_field(
        strings,
        "choose_character.field_name",
        f"{Fore.CYAN}{Style.BRIGHT}{char.name}{Style.RESET_ALL}",
        indent=indent,
    )
    _print_labeled_field(
        strings,
        "choose_character.field_race",
        f"{Fore.CYAN}{base_race}{Style.RESET_ALL}",
        indent=indent,
    )
    if subrace:
        _print_labeled_field(
            strings,
            "choose_character.field_subrace",
            f"{Fore.CYAN}{subrace}{Style.RESET_ALL}",
            indent=indent,
        )
    if char.languages:
        lang_line = ", ".join(
            get_language_name(lang_id, language) for lang_id in char.languages
        )
        lang_display = f"{Fore.CYAN}{lang_line}{Style.RESET_ALL}"
    else:
        lang_display = _empty_field_value(strings)
    _print_labeled_field(
        strings,
        "choose_character.field_languages",
        lang_display,
        indent=indent,
    )
    if char.background_id:
        bg = load_background_full(char.background_id, language)
        bg_name = bg.get("name", char.background_id)
        bg_display = f"{Fore.CYAN}{bg_name}{Style.RESET_ALL}"
    else:
        bg_display = _empty_field_value(strings)
    _print_labeled_field(
        strings,
        "choose_character.field_background",
        bg_display,
        indent=indent,
    )
    if char.feat_ids:
        feats_text = _format_character_feats(char, language)
        feats_display = f"{Fore.CYAN}{feats_text}{Style.RESET_ALL}"
        _print_labeled_field(
            strings,
            "choose_character.field_feats",
            feats_display,
            indent=indent,
        )
    _print_labeled_field(
        strings,
        "choose_character.field_class",
        f"{Fore.CYAN}{class_label}{Style.RESET_ALL}",
        indent=indent,
    )
    subclass_label = _character_subclass_label(char, language)
    if subclass_label:
        display = f"{Fore.CYAN}{subclass_label}{Style.RESET_ALL}"
        if char.subclass_id and not subclass_is_active(char):
            choice_level = get_subclass_choice_level(char.class_id)
            pending = get_string(
                strings,
                "choose_character.subclass_pending_level",
                level=choice_level,
            )
            display = (
                f"{display} {Fore.LIGHTBLACK_EX}{pending}{Style.RESET_ALL}"
            )
        _print_labeled_field(
            strings,
            "choose_character.field_subclass",
            display,
            indent=indent,
        )
    _print_labeled_field(
        strings,
        "choose_character.field_level",
        f"{Fore.YELLOW}{char.level}{Style.RESET_ALL}",
        indent=indent,
    )

    vitals_line = get_string(
        strings,
        "choose_character.vitals_line",
        hp=f"{Fore.GREEN}{char.current_hp}{Style.RESET_ALL}",
        xp=f"{Fore.MAGENTA}{char.experience}{Style.RESET_ALL}",
    )
    print(f"{indent}{vitals_line}")

    stats_compact = _format_character_stats_compact(char, strings)
    if stats_compact:
        stats_line = get_string(
            strings, "choose_character.stats_line", stats=stats_compact
        )
        print(f"{indent}{stats_line}")

    _print_character_skills_and_expertise(char, strings, indent=indent)

    _print_character_proficiencies(char, strings, language, indent=indent)

    _print_character_saving_throws(char, strings, indent=indent)

    _print_character_equipment(char, strings, language, indent=indent)

    _print_labeled_field(
        strings,
        "choose_character.field_difficulty",
        f"{mode_color}{mode}{Style.RESET_ALL}",
        indent=indent,
    )

    print()


def _print_characters_list(
    strings: StringsDict,
    characters: list[Character],
    language: str,
) -> None:
    """Вывести список сохранённых персонажей."""
    print(
        f"  {Fore.YELLOW}{Style.BRIGHT}"
        f"{get_string(strings, 'choose_character.list_header')}"
        f"{Style.RESET_ALL}"
    )
    print()
    for idx, char in enumerate(characters, 1):
        _print_character_card(idx, char, strings, language)


__all__ = [
    # Labels
    "_localized_string_list",
    "_grant_type_label",
    "_grant_pool_label",
    "_label_from_catalog",
    # Difficulty
    "_difficulty_label",
    "_difficulty_color",
    # Grants
    "_grant_display_name",
    "_grant_description",
    "format_grant_line_text",
    "format_grant_lines",
    "_print_grant_line",
    # Race
    "_print_race_info",
    "_print_race_grants",
    "_format_bonuses",
    "_print_race_bonuses",
    # Background
    "_print_background_info",
    "_print_background_grants",
    # Stats
    "_format_character_stats_compact",
    "_print_final_stat_line",
    "_print_stats_generation_header",
    "_print_point_buy_cost_table",
    # Character header
    "_format_character_feats",
    "_character_base_race_label",
    "_character_subrace_label",
    "_empty_field_value",
    "_print_labeled_field",
    # Character sections
    "_format_proficiency_token_list",
    "_print_character_proficiencies",
    "_print_character_skills_and_expertise",
    "_print_character_saving_throws",
    "_print_character_equipment",
    # Inventory
    "format_inventory_line",
    "format_versatile_damage_dice",
    "get_equipped_display",
    # Class
    "_character_class_label",
    "_character_subclass_label",
    "_format_class_proficiencies",
    "_format_class_skills",
    "_format_class_saving_throws",
    "_print_class_starting_equipment",
    "_print_class_description",
    "_print_class_meta_line",
    "_print_features_section_title",
    "_format_feature_uses",
    "_print_class_features",
    "_print_class_summary",
    "_print_class_info",
    "_print_subclass_info",
    # Character
    "_print_character_card",
    "_print_characters_list",
]
