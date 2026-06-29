"""Отображение карточек персонажей, рас и характеристик."""

from typing import Any

from colorama import Fore, Style

from core.classes import get_subclass_choice_level
from core.equipment import proficiency_token_label
from core.localization import get_string
from core.models import Character
from core.subclasses import features_up_to_level, subclass_is_active
from core.types import GameDifficulty, StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import (
    SEPARATOR,
    _ability_name,
    _skill_name,
    _stats_caption_line,
)
from ui.menus.expertise import format_expertise_display


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


def _character_base_race_label(char: Character, language: str = "ru") -> str:
    """Читаемое название базовой расы персонажа."""
    race_full = _deps.load_race_full(char.race, language)
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

    race_full = _deps.load_race_full(char.race, language)
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


def _character_class_label(char: Character, language: str = "ru") -> str:
    """Читаемое название класса персонажа."""
    for cls in _deps.load_classes(language):
        if cls.get("id") == char.class_name:
            return str(cls.get("name", char.class_name))
    return char.class_name


def _character_subclass_label(
    char: Character, language: str = "ru"
) -> str | None:
    """Читаемое название подкласса или None."""
    if not char.subclass_id:
        return None
    for sub in _deps.load_subclasses(char.class_name, language):
        if sub.get("id") == char.subclass_id:
            return str(sub.get("name", char.subclass_id))
    return char.subclass_id


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
    equipment = class_info.get("equipment", {})
    if isinstance(equipment, dict):
        legacy: list[str] = []
        weapons = equipment.get("weapons", [])
        armor = equipment.get("armor", [])
        if isinstance(weapons, list) and weapons:
            legacy.append(", ".join(str(w) for w in weapons))
        if isinstance(armor, list) and armor:
            legacy.append(", ".join(str(a) for a in armor))
        return "; ".join(legacy)
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


def _print_class_summary(
    class_info: dict[str, Any],
    strings: StringsDict,
    *,
    include_features: bool = True,
    skills_summary: bool = True,
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


def _format_character_stats_compact(
    char: Character, strings: StringsDict
) -> str:
    """Компактная строка характеристик: аббревиатура + значение."""
    if not char.stats:
        return ""

    parts = []
    for stat in _deps.STAT_NAMES:
        value = char.stats.get(stat)
        if value is None:
            continue
        abbr = _ability_name(strings, stat)[:3]
        parts.append(
            f"{Fore.CYAN}{abbr}{Style.RESET_ALL} "
            f"{Fore.YELLOW}{value:>2}{Style.RESET_ALL}"
        )
    return "  ".join(parts)


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
            _deps.get_language_name(lang_id, language)
            for lang_id in char.languages
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
        bg = _deps.load_background_full(char.background_id, language)
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
            choice_level = get_subclass_choice_level(char.class_name)
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

    _print_character_proficiencies(char, strings, language, indent=indent)

    _print_labeled_field(
        strings,
        "choose_character.field_difficulty",
        f"{mode_color}{mode}{Style.RESET_ALL}",
        indent=indent,
    )

    print()


def _print_race_info(info: StringsDict, strings: StringsDict) -> None:
    """Вывести подробности расы или подрасы."""
    desc = info.get("description", "")
    if desc:
        print(get_string(strings, "character.race_description", desc=desc))

    speed = info.get("speed")
    if speed:
        print(get_string(strings, "character.speed_label", speed=speed))

    languages = info.get("languages", [])
    if languages:
        language_line = ", ".join(str(lang) for lang in languages)
        print(
            get_string(
                strings, "character.languages_label", langs=language_line
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
        for feat in info.get("features", []):
            if not isinstance(feat, dict):
                continue
            if feat.get("type") != "ability_bonus":
                continue
            mechanics = feat.get("mechanics", {})
            if isinstance(mechanics, dict) and mechanics.get("choice"):
                count = int(mechanics.get("count", 1))
                value = int(mechanics.get("value", 1))
                choice_info = get_string(
                    strings,
                    "character.stats_choice_bonus_subrace_info",
                    count=count,
                    value=value,
                )
                print(
                    get_string(
                        strings,
                        "character.ability_bonuses_label",
                        bonuses=choice_info,
                    )
                )
                break

    features = info.get("features", [])
    if features:
        print(get_string(strings, "character.features_label"))
        for feat in features:
            description = feat.get("description", "")
            print(
                get_string(
                    strings,
                    "character.feature_line",
                    name=feat.get("name", ""),
                    desc=description,
                )
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
    bonuses = _deps.get_race_bonuses(race_id, subrace_id)
    if bonuses:
        print(_format_bonuses(bonuses, strings))
        return

    mechanics = _deps.get_choice_ability_bonus_mechanics(race_id, subrace_id)
    if mechanics:
        count = int(mechanics.get("count", 1))
        value = int(mechanics.get("value", 1))
        pending_msg = get_string(
            strings,
            "character.stats_choice_bonus_pending",
            count=count,
            value=value,
        )
        print(f"{Fore.CYAN}{pending_msg}{Style.RESET_ALL}")
        return

    print(_format_bonuses(bonuses, strings))


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
    for value in sorted(_deps.POINT_BUY_COSTS):
        cost = _deps.POINT_BUY_COSTS[value]
        print(
            f"  {Fore.CYAN}{value:>5}{Style.RESET_ALL}  "
            f"{Fore.CYAN}{cost:>5}{Style.RESET_ALL}"
        )
    print()
