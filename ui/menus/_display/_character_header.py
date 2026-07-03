"""Подписи и поля заголовка карточки персонажа."""

from colorama import Fore, Style

from core.localization import get_string, resolve_localized_text
from core.models import Character
from core.types import StringsDict
from ui.menus import _deps


def _format_character_feats(char: Character, language: str = "ru") -> str:
    """Список названий черт персонажа через запятую."""
    from core.feats.feats_loader import load_feat

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
