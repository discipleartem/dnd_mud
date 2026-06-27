"""Загрузка предысторий из YAML."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from core.io import load_yaml
from core.localization import resolve_localized_text

BACKGROUNDS_FILE = Path("database/backgrounds/backgrounds.yaml")


@lru_cache(maxsize=1)
def _load_backgrounds_yaml() -> dict[str, Any]:
    """Загрузить данные предысторий."""
    data = load_yaml(BACKGROUNDS_FILE)
    backgrounds = data.get("backgrounds", {})
    if isinstance(backgrounds, dict):
        return backgrounds
    return {}


def _normalize_background(
    background_id: str, info: dict[str, Any], language: str
) -> dict[str, Any]:
    """Локализовать поля одной предыстории."""
    result = dict(info)
    result["id"] = background_id
    result["name"] = resolve_localized_text(info.get("name", {}), language)
    result["description"] = resolve_localized_text(
        info.get("description", {}), language
    )
    feature = info.get("feature", {})
    if isinstance(feature, dict):
        result["feature"] = {
            "name": resolve_localized_text(feature.get("name", {}), language),
            "description": resolve_localized_text(
                feature.get("description", {}), language
            ),
        }
    return result


def load_backgrounds(language: str = "ru") -> list[dict[str, Any]]:
    """Список предысторий для UI."""
    result: list[dict[str, Any]] = []
    for bg_id, info in _load_backgrounds_yaml().items():
        if isinstance(info, dict):
            result.append(_normalize_background(bg_id, info, language))
    return result


def load_background_full(
    background_id: str, language: str = "ru"
) -> dict[str, Any]:
    """Полные данные одной предыстории."""
    info = _load_backgrounds_yaml().get(background_id, {})
    if not isinstance(info, dict):
        return {"id": background_id, "name": background_id}
    return _normalize_background(background_id, info, language)


def get_background_skills(background_id: str) -> list[str]:
    """Два навыка предыстории."""
    info = _load_backgrounds_yaml().get(background_id, {})
    if not isinstance(info, dict):
        return []
    raw = info.get("skills", [])
    if isinstance(raw, list):
        return [str(s) for s in raw]
    return []


def get_background_language_choice(
    background_id: str,
) -> dict[str, Any] | None:
    """Механика выбора языков предыстории или None."""
    info = _load_backgrounds_yaml().get(background_id, {})
    if not isinstance(info, dict):
        return None
    langs = info.get("languages", {})
    if not isinstance(langs, dict) or not langs.get("choice"):
        return None
    count = int(langs.get("count", 0))
    if count <= 0:
        return None
    return langs
