"""Форматирование и вывод grants."""

from typing import Any

from core.equipment import (
    get_tool_name,
    get_weapon_name,
    proficiency_token_label,
)
from core.grants import (
    ABILITY_INCREASE,
    normalize_armor_token,
)
from core.localization import (
    get_string,
)
from core.types import (
    StringsDict,
)
from ui.menus.console import (
    ability_name,
    skill_name,
)

# ============================================================================
# Общие хелперы подписей
# ============================================================================


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
    ability_label = ability_name(strings, ability) if ability else ""
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
            skill=skill_name(strings, str(skill_id)),
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
                    ability=ability_name(strings, ability),
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
                    skill=skill_name(strings, skill),
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
            skill=skill_name(strings, skills),
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
            skill=skill_name(strings, skill),
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
            save=ability_name(strings, str(grant["save"])),
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
