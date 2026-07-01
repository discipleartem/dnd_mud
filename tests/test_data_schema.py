"""Валидация YAML-каталогов против JSON Schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import jsonschema
import pytest
import yaml

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "database" / "schema" / "v1"


def _load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / name
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert isinstance(data, dict)
    return data


@pytest.fixture(scope="module")
def grant_schema() -> dict[str, Any]:
    return _load_schema("grant.json")


@pytest.fixture(scope="module")
def background_schema(grant_schema: dict[str, Any]) -> dict[str, Any]:
    raw = json.dumps(_load_schema("background.json"))
    store = cast(dict[str, Any], json.loads(raw))
    store["properties"]["grants"]["items"] = grant_schema
    return store


@pytest.fixture(scope="module")
def adventure_schema() -> dict[str, Any]:
    return _load_schema("adventure.json")


@pytest.fixture(scope="module")
def class_progression_schema() -> dict[str, Any]:
    return _load_schema("class_progression.json")


def test_backgrounds_yaml_matches_schema(
    background_schema: dict[str, Any],
) -> None:
    """PHB-предыстории соответствуют background.json."""
    data = _load_yaml(ROOT / "database/backgrounds/backgrounds.yaml")
    for _bg_id, bg in data.get("backgrounds", {}).items():
        jsonschema.validate(bg, background_schema)


def test_adventures_yaml_matches_schema(
    adventure_schema: dict[str, Any],
) -> None:
    """Каталог приключений соответствует adventure.json."""
    data = _load_yaml(ROOT / "database/content/adventures.yaml")
    for entry in data.get("adventures", []):
        jsonschema.validate(entry, adventure_schema)


def _normalize_progression(progression: Any) -> dict[str, Any]:
    """YAML может загрузить ключи уровней как int — привести к str."""
    if not isinstance(progression, dict):
        return {}
    return {str(level): data for level, data in progression.items()}


def test_classes_progression_matches_schema(
    class_progression_schema: dict[str, Any],
) -> None:
    """Классы и подклассы используют progression.<level>.grants."""
    data = _load_yaml(ROOT / "database/classes/classes.yaml")
    for _class_id, class_info in data.get("classes", {}).items():
        jsonschema.validate(
            {
                "progression": _normalize_progression(
                    class_info.get("progression", {})
                )
            },
            class_progression_schema,
        )
        for sub in class_info.get("subclasses", []) or []:
            if isinstance(sub, dict) and sub.get("progression"):
                jsonschema.validate(
                    {
                        "progression": _normalize_progression(
                            sub["progression"]
                        )
                    },
                    class_progression_schema,
                )


def test_race_grants_match_grant_schema(
    grant_schema: dict[str, Any],
) -> None:
    """Grants рас и подрас соответствуют grant.json."""
    data = _load_yaml(ROOT / "database/races/races.yaml")

    def check_grants(grants: Any, _source: str) -> None:
        if not isinstance(grants, list):
            return
        for grant in grants:
            if isinstance(grant, dict):
                jsonschema.validate(grant, grant_schema)

    for race_id, race in data.get("races", {}).items():
        check_grants(race.get("grants"), f"race:{race_id}")
        for sub_id, sub in (race.get("subraces") or {}).items():
            if isinstance(sub, dict):
                check_grants(sub.get("grants"), f"race:{race_id}:{sub_id}")
