"""Локализованное отображение grants[] на экранах расы и предыстории."""

from typing import Any

from core.equipment import (
    get_tool_name,
    get_weapon_name,
    proficiency_token_label,
)
from core.grant_mechanics import normalize_armor_token
from core.grants import ABILITY_INCREASE
from core.localization import get_string
from core.types import StringsDict
from ui.menus._common import _ability_name, _skill_name
from ui.menus._display._labels import (
    _grant_pool_label,
    _grant_type_label,
)


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
        count = int(grant.get("count", 1))
        amount = int(grant.get("amount", 1))
        return get_string(
            strings,
            "character.stats_choice_bonus_subrace_info",
            count=count,
            value=amount,
        )
    if grant.get("choice"):
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
        return get_string(
            strings,
            "character.grant_choice",
            count=count,
        )
    if gtype == "tool_proficiency":
        raw_tools = grant.get("tools", [])
        if isinstance(raw_tools, list) and raw_tools:
            return ", ".join(
                get_tool_name(str(tool_id), language) for tool_id in raw_tools
            )
    if gtype == "spellcasting":
        return _format_spellcasting_grant(grant, strings)
    if gtype == "cantrip":
        source = str(grant.get("source", ""))
        ability = str(grant.get("ability", ""))
        if source and ability:
            return get_string(
                strings,
                "character.grant_cantrip_choice",
                source=source,
                ability=_ability_name(strings, ability),
            )
    if gtype == "immunity":
        effect = str(grant.get("effect", ""))
        if effect == "magical_sleep":
            return get_string(
                strings, "character.grant_immunity_magical_sleep"
            )
    if gtype == "disadvantage":
        return _format_disadvantage_grant(grant, strings)
    weapons = grant.get("weapons", [])
    if isinstance(weapons, list) and weapons:
        return ", ".join(get_weapon_name(str(w), language) for w in weapons)
    if gtype == "skill_bonus" and grant.get("expertise"):
        skill = grant.get("skill")
        if isinstance(skill, str) and skill:
            return get_string(
                strings,
                "character.grant_skill_expertise",
                skill=_skill_name(strings, skill),
            )
    if gtype == "skill_proficiency":
        skills = grant.get("skills", grant.get("skill"))
        if isinstance(skills, list) and skills:
            return _format_skill_proficiency_labels(strings, skills)
        if isinstance(skills, str) and skills:
            return get_string(
                strings,
                "character.grant_skill_proficiency",
                skill=_skill_name(strings, skills),
            )
    if gtype == "armor_proficiency":
        armor_labels = _armor_labels_from_grant(grant, strings, language)
        if armor_labels:
            return armor_labels
    if gtype == "speed_ignore_penalty":
        armor_labels = _armor_labels_from_grant(grant, strings, language)
        if armor_labels:
            return get_string(
                strings,
                "character.grant_speed_ignore",
                armors=armor_labels,
            )
    if gtype == "resistance":
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
    if gtype == "speed_bonus":
        speed = grant.get("amount")
        if speed is not None:
            return get_string(
                strings,
                "character.grant_speed_value",
                speed=speed,
            )
    if gtype == "advantage":
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
    if gtype == "rest" and grant.get("duration") is not None:
        return get_string(
            strings,
            "character.grant_rest_trance",
            duration=int(grant["duration"]),
        )
    range_ft = grant.get("range")
    if gtype == "darkvision" and range_ft is not None:
        return get_string(
            strings,
            "character.grant_darkvision",
            range=range_ft,
        )
    return ""


def _print_grant_line(
    grant: dict[str, Any],
    strings: StringsDict,
    language: str,
    *,
    inherited: bool = False,
) -> None:
    """Вывести одну строку особенности."""
    name = _grant_display_name(grant, strings)
    if inherited:
        suffix = get_string(strings, "character.grant_inherited_suffix")
        name = f"{name}{suffix}"
    desc = _grant_description(grant, strings, language)
    if desc:
        print(
            get_string(
                strings,
                "character.feature_line",
                name=name,
                desc=desc,
            )
        )
    else:
        print(
            get_string(
                strings,
                "character.feature_line_name_only",
                name=name,
            )
        )
