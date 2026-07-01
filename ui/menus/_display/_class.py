"""Отображение классов и подклассов."""

from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from core.models import Character
from core.starting_equipment import (
    STARTING_EQUIPMENT_SECTION_KEYS,
    STARTING_EQUIPMENT_SECTION_ORDER,
    summarize_class_starting_equipment,
)
from core.subclasses import features_up_to_level
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import _ability_name, _skill_name
from ui.menus._display._labels import _label_from_catalog


def _character_class_label(char: Character, language: str = "ru") -> str:
    """Читаемое название класса персонажа."""
    return _label_from_catalog(
        _deps.load_classes(language), char.class_id, default=char.class_id
    )


def _character_subclass_label(
    char: Character, language: str = "ru"
) -> str | None:
    """Читаемое название подкласса или None."""
    if not char.subclass_id:
        return None
    return _label_from_catalog(
        _deps.load_subclasses(char.class_id, language),
        char.subclass_id,
        default=char.subclass_id,
    )


def _format_class_proficiencies(
    strings: StringsDict,
    class_info: dict[str, Any],
) -> str:
    """Сжатая строка владений класса."""
    prof = class_info.get("proficiencies", {})
    if isinstance(prof, dict):
        parts: list[str] = []
        for key, label_key in (
            ("armor", "proficiency"),
            ("weapons", "proficiency"),
            ("tools", "proficiency"),
        ):
            raw = prof.get(key, [])
            if isinstance(raw, list) and raw:
                labels = [
                    get_string(strings, f"{label_key}.{token}", default=token)
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


def _print_class_features(
    strings: StringsDict, features: list[Any], *, detailed: bool
) -> None:
    """Вывести классовые умения (до 10 уровня)."""
    filtered = features_up_to_level(features)
    if not filtered:
        return
    _print_features_section_title(strings)
    if detailed:
        by_level: dict[int, list[dict[str, Any]]] = {}
        for feat in filtered:
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
        for feat in filtered:
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

    prof = _format_class_proficiencies(strings, class_info)
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
