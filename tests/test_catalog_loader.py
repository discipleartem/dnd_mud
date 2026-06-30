"""Тесты единого загрузчика каталогов."""

from core.catalog_loader import clear_catalog_cache, load_catalog
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
