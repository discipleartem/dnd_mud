"""Общие фикстуры и хелперы для тестов."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _reset_catalog_caches() -> Generator[None, None, None]:
    """Сбросить кэши каталогов между тестами."""
    from core.catalog_loader import clear_all_catalog_caches

    clear_all_catalog_caches()
    yield
    clear_all_catalog_caches()


@pytest.fixture(autouse=True)
def _reset_corrupt_save_warnings() -> Generator[None, None, None]:
    """Сбросить очередь предупреждений о битых сейвах между тестами."""
    from core.character_storage import pop_corrupt_save_warnings

    pop_corrupt_save_warnings()
    yield
    pop_corrupt_save_warnings()


@pytest.fixture
def ru_strings() -> dict[str, Any]:
    """Строки локализации ru."""
    from core.localization import load_strings

    return load_strings("ru")


@pytest.fixture
def en_strings() -> dict[str, Any]:
    """Строки локализации en."""
    from core.localization import load_strings

    return load_strings("en")


@pytest.fixture
def characters_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Временная директория сохранений персонажей."""
    import core.character_storage as storage_mod

    path = tmp_path / "characters"
    monkeypatch.setattr(storage_mod, "CHARACTERS_DIR", path)
    return path


@pytest.fixture
def settings_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Временный файл настроек."""
    import core.settings as settings_mod

    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings_mod, "SETTINGS_PATH", path)
    return path


@pytest.fixture
def human_race_with_subraces() -> dict[str, Any]:
    """Человек с подрасами standard и variant_human (тестовый YAML)."""
    return {
        "name": "Человек",
        "description": "Описание человека",
        "subraces": {
            "standard": {
                "name": "Человек (стандарт)",
                "description": "Стандартный человек",
                "ability_bonuses": {"strength": 1},
            },
            "variant_human": {
                "name": "Человек (вариант)",
                "description": "Вариант человека",
                "inherit": {"ability_bonuses": False, "grants": False},
                "grants": [],
            },
        },
    }


@pytest.fixture
def subrace_strings() -> dict[str, Any]:
    """Минимальные строки для экрана выбора подрасы."""
    return {
        "character": {
            "subrace_caption": "ОПИСАНИЕ РАСЫ И ВЫБОР ПОДРАСЫ",
            "race_description": "  {desc}",
            "features_label": "  Особенности:",
            "feature_line": "    • {name}: {desc}",
            "subraces_label": "  Подрасы:",
            "subrace_prompt": "Выберите подрасу: ",
            "back": "Назад",
        }
    }


@pytest.fixture
def patch_int_input():
    """Фабрика подмены get_int_input последовательностью значений."""

    def _patch(monkeypatch: pytest.MonkeyPatch, values: list[int]) -> None:
        iterator = iter(values)

        def fake_get_int_input(*args: object, **kwargs: object) -> int:
            return next(iterator)

        monkeypatch.setattr(
            "ui.menus._deps.get_int_input",
            fake_get_int_input,
        )

    return _patch
