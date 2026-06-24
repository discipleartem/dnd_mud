"""Общие фикстуры и хелперы для тестов."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


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
