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
    import core.character as character_mod

    path = tmp_path / "characters"
    monkeypatch.setattr(character_mod, "CHARACTERS_DIR", path)
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

    def _patch(
        monkeypatch: pytest.MonkeyPatch,
        module: Any,
        values: list[int],
    ) -> None:
        iterator = iter(values)
        monkeypatch.setattr(
            module,
            "get_int_input",
            lambda *args, **kwargs: next(iterator),
        )

    return _patch
