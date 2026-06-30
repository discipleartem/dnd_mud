"""Загрузка классов персонажей из YAML."""

from pathlib import Path
from typing import Any

from core.catalog_loader import load_catalog
from core.localization import resolve_localized_text

CLASSES_FILE = Path("database/classes/classes.yaml")
DEFAULT_SUBCLASS_CHOICE_LEVEL = 3


def _load_classes_yaml() -> dict[str, Any]:
    """Загрузить данные классов из YAML."""
    return load_catalog(CLASSES_FILE, "classes")


def get_class_dict(class_id: str) -> dict[str, Any]:
    """Сырые данные класса из YAML."""
    info = _load_classes_yaml().get(class_id, {})
    return info if isinstance(info, dict) else {}


def get_class_hit_dice(class_id: str) -> int:
    """Получить кость здоровья класса."""
    hit_dice = get_class_dict(class_id).get("hit_dice", 8)
    if isinstance(hit_dice, int):
        return hit_dice
    return 8


def get_subclass_choice_level(class_id: str) -> int:
    """Уровень класса, на котором выбирается подкласс (PHB / YAML)."""
    level = get_class_dict(class_id).get(
        "subclass_choice_level", DEFAULT_SUBCLASS_CHOICE_LEVEL
    )
    if isinstance(level, int):
        return level
    return DEFAULT_SUBCLASS_CHOICE_LEVEL


def _spellcasting_from_entry(
    entry: dict[str, Any], level: int, default_start: int
) -> bool:
    """Есть ли заклинания у класса/подкласса на данном уровне."""
    if not entry.get("spellcasting"):
        return False
    start = entry.get("spellcasting_level", default_start)
    if not isinstance(start, int):
        start = default_start
    return level >= start


def character_has_spellcasting(
    class_id: str, subclass_id: str | None, level: int
) -> bool:
    """Может ли персонаж накладывать заклинания (для требований черт).

    Данные — поля ``spellcasting`` / ``spellcasting_level`` в
    ``database/classes/classes.yaml`` (PHB: «Использование заклинаний»).
    """
    class_info = get_class_dict(class_id)
    if not class_info:
        return False
    if _spellcasting_from_entry(class_info, level, 1):
        return True
    if not subclass_id:
        return False
    raw_subclasses = class_info.get("subclasses", [])
    if not isinstance(raw_subclasses, list):
        return False
    choice_level = get_subclass_choice_level(class_id)
    for entry in raw_subclasses:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("id", "")) != subclass_id:
            continue
        return _spellcasting_from_entry(entry, level, choice_level)
    return False


def _subclass_feature_ids_and_names(
    class_info: dict[str, Any],
) -> tuple[set[str], set[str]]:
    """ID и имена умений подклассов — не дублировать в карточке класса."""
    ids: set[str] = set()
    names: set[str] = set()
    raw_subclasses = class_info.get("subclasses", [])
    if not isinstance(raw_subclasses, list):
        return ids, names
    for entry in raw_subclasses:
        if not isinstance(entry, dict):
            continue
        raw_features = entry.get("class_features", [])
        if not isinstance(raw_features, list):
            continue
        for feat in raw_features:
            if not isinstance(feat, dict):
                continue
            fid = feat.get("id")
            if fid is not None:
                ids.add(str(fid))
            fname = feat.get("name")
            if fname is not None:
                names.add(str(fname))
    return ids, names


def _class_features_only(class_info: dict[str, Any]) -> list[dict[str, Any]]:
    """Умения класса без дублей из подклассов (по id или name)."""
    raw_features = class_info.get("class_features", [])
    if not isinstance(raw_features, list):
        return []
    subclass_ids, subclass_names = _subclass_feature_ids_and_names(class_info)
    result: list[dict[str, Any]] = []
    for feat in raw_features:
        if not isinstance(feat, dict):
            continue
        fid = str(feat.get("id", ""))
        fname = str(feat.get("name", ""))
        if fid in subclass_ids or fname in subclass_names:
            continue
        result.append(feat)
    return result


def _normalize_class_dict(
    class_id: str, class_info: dict[str, Any], language: str
) -> dict[str, Any]:
    """Собрать dict класса с локализованными полями для UI."""
    return {
        "id": class_id,
        "name": resolve_localized_text(
            class_info.get("name", class_id),
            language,
            fallback=class_id,
        ),
        "description": class_info.get("description", ""),
        "hit_dice": class_info.get("hit_dice", 8),
        "prime_ability": class_info.get("prime_ability", "strength"),
        "subclass_choice_level": get_subclass_choice_level(class_id),
        "saving_throws": class_info.get("saving_throws", []),
        "skill_choices": class_info.get("skill_choices", []),
        "skill_choices_count": class_info.get("skill_choices_count", 0),
        "equipment": class_info.get("equipment", {}),
        "proficiencies": class_info.get("proficiencies", {}),
        "features": _class_features_only(class_info),
        "subclasses": class_info.get("subclasses", []),
    }


def load_classes(language: str = "ru") -> list[dict[str, Any]]:
    """Загрузить список всех доступных классов."""
    result: list[dict[str, Any]] = []
    for class_id, class_info in _load_classes_yaml().items():
        if isinstance(class_info, dict):
            normalized = _normalize_class_dict(class_id, class_info, language)
            result.append(
                {
                    "id": normalized["id"],
                    "name": normalized["name"],
                    "description": normalized["description"],
                    "hit_dice": normalized["hit_dice"],
                    "prime_ability": normalized["prime_ability"],
                }
            )
    return result


def load_class_full(class_id: str, language: str = "ru") -> dict[str, Any]:
    """Загрузить полные данные класса для экрана выбора."""
    class_info = get_class_dict(class_id)
    if not class_info:
        return {"id": class_id, "name": class_id}
    return _normalize_class_dict(class_id, class_info, language)


def load_subclasses(
    class_id: str, language: str = "ru"
) -> list[dict[str, Any]]:
    """Загрузить подклассы класса с локализованными именами."""
    class_info = get_class_dict(class_id)
    if not class_info:
        return []

    raw_subclasses = class_info.get("subclasses", [])
    if not isinstance(raw_subclasses, list):
        return []

    result: list[dict[str, Any]] = []
    for entry in raw_subclasses:
        if not isinstance(entry, dict):
            continue
        sub_id = entry.get("id", "")
        name = entry.get("name", sub_id)
        if isinstance(name, dict):
            name = resolve_localized_text(name, language, fallback=str(sub_id))
        result.append(
            {
                "id": sub_id,
                "name": str(name),
                "description": entry.get("description", ""),
                "parent_class": entry.get("parent_class", class_id),
                "features": entry.get("class_features", []),
            }
        )
    return result
