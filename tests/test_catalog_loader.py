"""Тесты единого загрузчика каталогов."""

from pathlib import Path

import pytest

from core.catalog_loader import (
    clear_all_catalog_caches,
    clear_catalog_cache,
    load_catalog,
)
from core.io import CatalogLoadError
from core.races import RACES_FILE, clear_races_cache


def test_load_catalog_returns_races() -> None:
    clear_catalog_cache()
    races = load_catalog(RACES_FILE, "races")
    assert "human" in races


def test_clear_races_cache_invalidates_catalog() -> None:
    first = load_catalog(RACES_FILE, "races")
    clear_races_cache()
    second = load_catalog(RACES_FILE, "races")
    assert first is not second


def test_clear_all_catalog_caches_resets_load_catalog() -> None:
    first = load_catalog(RACES_FILE, "races")
    clear_all_catalog_caches()
    second = load_catalog(RACES_FILE, "races")
    assert first is not second


def test_load_catalog_raises_on_corrupt_yaml(tmp_path: Path) -> None:
    path = tmp_path / "races.yaml"
    path.write_text(":\n  bad: [unclosed", encoding="utf-8")
    clear_catalog_cache()
    with pytest.raises(CatalogLoadError):
        load_catalog(path, "races")


def test_load_merged_yaml_raises_on_corrupt_json_syntax(
    tmp_path: Path,
) -> None:
    from core.mod_loader import clear_mod_loader_cache, load_merged_yaml

    path = tmp_path / "catalog.json"
    path.write_text("{not json", encoding="utf-8")
    clear_mod_loader_cache()
    with pytest.raises(CatalogLoadError):
        load_merged_yaml(path)
