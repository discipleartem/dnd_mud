"""Общие хелперы подписей из каталогов."""

from typing import Any

from core.localization import get_string
from core.types import StringsDict


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
