"""Загрузка языков и пулов выбора при создании персонажа."""

from pathlib import Path
from typing import Any, Literal

from core.catalog_loader import load_catalog
from core.grants import grants_from_entity, grants_of_type, inherit_flags
from core.localization import resolve_localized_text
from core.races import collect_race_grants, get_race_and_subrace

LANGUAGES_FILE = Path("database/core/languages.yaml")
LanguagePool = Literal["common", "exotic", "any"]


def _load_languages_yaml() -> dict[str, Any]:
    """Загрузить каталог языков."""
    return load_catalog(LANGUAGES_FILE, "languages")


def load_languages(language: str = "ru") -> list[dict[str, Any]]:
    """Список языков с локализованными полями."""
    result: list[dict[str, Any]] = []
    for lang_id, info in _load_languages_yaml().items():
        if not isinstance(info, dict):
            continue
        result.append(
            {
                "id": lang_id,
                "name": resolve_localized_text(info.get("name", {}), language),
                "category": info.get("category", "common"),
            }
        )
    return result


def get_language_name(lang_id: str, language: str = "ru") -> str:
    """Локализованное имя языка."""
    info = _load_languages_yaml().get(lang_id, {})
    if isinstance(info, dict):
        return resolve_localized_text(
            info.get("name", {}), language, fallback=lang_id
        )
    return lang_id


def get_fixed_racial_languages(
    race_id: str, subrace_id: str | None = None
) -> list[str]:
    """Фиксированные языки расы/подрасы из YAML."""
    race_info, subrace_info = get_race_and_subrace(race_id, subrace_id)
    if not race_info:
        return []

    result: list[str] = []
    if subrace_info:
        for lang in race_info.get("languages", []):
            lang_id = str(lang)
            if lang_id not in result:
                result.append(lang_id)
        for lang in subrace_info.get("languages", []):
            lang_id = str(lang)
            if lang_id not in result:
                result.append(lang_id)
    else:
        for lang in race_info.get("languages", []):
            lang_id = str(lang)
            if lang_id not in result:
                result.append(lang_id)
    return result


def get_racial_language_choices(
    race_id: str, subrace_id: str | None = None
) -> list[tuple[dict[str, Any], str]]:
    """Выборные языки из grants: (grant, source)."""
    choices: list[tuple[dict[str, Any], str]] = []
    race_info, subrace_info = get_race_and_subrace(race_id, subrace_id)

    if not race_info:
        return []

    def scan(grants: list[dict[str, Any]], source: str) -> None:
        for grant in grants_of_type(grants, "language"):
            if grant.get("choice"):
                choices.append((grant, source))

    if subrace_info:
        _, inherit_grants = inherit_flags(subrace_info)
        if inherit_grants:
            scan(grants_from_entity(race_info), "race")
        scan(grants_from_entity(subrace_info), "subrace")
    else:
        scan(collect_race_grants(race_id, subrace_id), "race")
    return choices


def _language_ids_by_category(category: str) -> list[str]:
    """ID языков заданной категории."""
    return [
        lang_id
        for lang_id, info in _load_languages_yaml().items()
        if isinstance(info, dict) and info.get("category") == category
    ]


def resolve_language_pool(
    pool_spec: str | dict[str, Any] | None,
    known_languages: list[str],
) -> list[str]:
    """Пул языков для выбора с учётом common/exotic и уже известных."""
    known = set(known_languages)
    pool_key = "common"
    explicit: list[str] | None = None

    if isinstance(pool_spec, dict):
        pool_key = str(pool_spec.get("pool", "common"))
        raw_list = pool_spec.get("from_list")
        if isinstance(raw_list, list):
            explicit = [str(x) for x in raw_list]
    elif isinstance(pool_spec, str):
        pool_key = pool_spec

    if explicit is not None:
        candidates = explicit
    elif pool_key == "exotic":
        candidates = _language_ids_by_category("exotic")
    elif pool_key == "any":
        common = _language_ids_by_category("common")
        exotic = _language_ids_by_category("exotic")
        candidates = common + exotic
    else:
        candidates = _language_ids_by_category("common")

    return [lang_id for lang_id in candidates if lang_id not in known]


def racial_languages_step_required(
    race_id: str, subrace_id: str | None = None
) -> bool:
    """Нужен ли экран языков (фиксированные или выборные)."""
    fixed = get_fixed_racial_languages(race_id, subrace_id)
    choices = get_racial_language_choices(race_id, subrace_id)
    return bool(fixed) or bool(choices)
