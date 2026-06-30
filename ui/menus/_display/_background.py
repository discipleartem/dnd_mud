"""Отображение предысторий при создании персонажа."""

from typing import Any

from core.grants import grants_from_entity
from core.localization import get_string
from core.types import StringsDict
from ui.menus._display._race import (
    _grant_description,
    _grant_display_name,
)


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
