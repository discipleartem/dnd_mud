"""Проверка и текст требований черт — реестр обработчиков по type."""

from collections.abc import Callable
from typing import Any

from core.catalogs.equipment import proficiency_token_label
from core.feats.requirements import FeatRequirementContext
from core.platform.localization import get_string
from core.types import StringsDict

_RequirementCheckFn = Callable[[dict[str, Any], FeatRequirementContext], bool]
_RequirementTextFn = Callable[
    [StringsDict, dict[str, Any], FeatRequirementContext, str], str
]


def _armor_requirement_met(
    required: list[str], armor_tokens: list[str]
) -> bool:
    """Проверка владения доспехом для требования черты."""
    return any(armor in armor_tokens for armor in required)


def _check_ability_score(
    req: dict[str, Any],
    ctx: FeatRequirementContext,
) -> bool:
    """Требование по значению характеристики."""
    target = str(req.get("target", ""))
    value = int(req.get("value", 0))
    if target not in ctx.stats:
        return False
    return int(ctx.stats[target]) >= value


def _check_armor_proficiency(
    req: dict[str, Any],
    ctx: FeatRequirementContext,
) -> bool:
    """Требование владения доспехом."""
    raw = req.get("armors", [])
    if isinstance(raw, list):
        return _armor_requirement_met([str(a) for a in raw], ctx.armor_tokens)
    return False


def _check_spellcasting(
    req: dict[str, Any],
    ctx: FeatRequirementContext,
) -> bool:
    """Требование умения накладывать заклинания."""
    return ctx.has_spellcasting


def _text_ability_score(
    strings: StringsDict,
    req: dict[str, Any],
    ctx: FeatRequirementContext,
    language: str,
) -> str:
    """Текст требования по характеристике."""
    target = str(req.get("target", ""))
    value = int(req.get("value", 0))
    current = int(ctx.stats.get(target, 0))
    return get_string(
        strings,
        "character.feat_req_ability",
        ability=get_string(strings, f"stats.{target}"),
        value=value,
        current=current,
    )


def _text_armor_proficiency(
    strings: StringsDict,
    req: dict[str, Any],
    ctx: FeatRequirementContext,
    language: str,
) -> str:
    """Текст требования владения доспехом."""
    raw = req.get("armors", [])
    armors = [str(a) for a in raw] if isinstance(raw, list) else []
    labels = [
        proficiency_token_label(armor, strings, language) for armor in armors
    ]
    return get_string(
        strings,
        "character.feat_req_armor",
        armors=", ".join(labels),
    )


def _text_spellcasting(
    strings: StringsDict,
    req: dict[str, Any],
    ctx: FeatRequirementContext,
    language: str,
) -> str:
    """Текст требования умения накладывать заклинания."""
    return get_string(strings, "character.feat_req_spellcasting")


REQUIREMENT_HANDLERS: dict[
    str, tuple[_RequirementCheckFn, _RequirementTextFn]
] = {
    "ability_score": (_check_ability_score, _text_ability_score),
    "armor_proficiency": (_check_armor_proficiency, _text_armor_proficiency),
    "spellcasting": (_check_spellcasting, _text_spellcasting),
}


def check_requirement(
    req: dict[str, Any],
    ctx: FeatRequirementContext,
) -> bool:
    """Выполнено ли одно требование черты (диспетчер по type)."""
    rtype = str(req.get("type", ""))
    handlers = REQUIREMENT_HANDLERS.get(rtype)
    if handlers is None:
        return True
    return handlers[0](req, ctx)


def format_requirement_text(
    strings: StringsDict,
    req: dict[str, Any],
    ctx: FeatRequirementContext,
    language: str,
) -> str:
    """Текст одного требования для экрана выбора (диспетчер по type)."""
    rtype = str(req.get("type", ""))
    handlers = REQUIREMENT_HANDLERS.get(rtype)
    if handlers is None:
        return ""
    return handlers[1](strings, req, ctx, language)
