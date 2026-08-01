"""Общие фикстуры и хелперы для тестов."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def catalog_caches_cleared() -> Generator[None, None, None]:
    """Сбросить кэши каталогов до и после теста."""
    from core.platform.catalog_loader import reload_catalogs

    reload_catalogs()
    yield
    reload_catalogs()


@pytest.fixture
def ru_strings() -> dict[str, Any]:
    """Строки локализации ru."""
    from core.platform.localization import load_strings

    return load_strings("ru")


@pytest.fixture
def en_strings() -> dict[str, Any]:
    """Строки локализации en."""
    from core.platform.localization import load_strings

    return load_strings("en")


@pytest.fixture
def characters_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Временная директория сохранений персонажей."""
    import core.character.storage as storage_mod

    path = tmp_path / "characters"
    monkeypatch.setattr(storage_mod, "CHARACTERS_DIR", path)
    return path


@pytest.fixture
def settings_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Временный файл настроек."""
    import core.platform.settings as settings_mod

    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings_mod, "SETTINGS_PATH", path)
    return path


@pytest.fixture
def human_race_with_subraces() -> dict[str, Any]:
    """Человек с подрасами standard и variant_human (тестовый YAML)."""
    return {
        "name": "Человек",
        "description": "Описание человека",
        "grants": [
            {
                "type": "language",
                "count": 1,
                "choice": True,
                "pool": "common",
                "name": "Дополнительный язык",
            }
        ],
        "subraces": {
            "standard": {
                "name": "Человек (стандарт)",
                "description": "Стандартный человек",
                "ability_bonuses": {"strength": 1},
            },
            "variant_human": {
                "name": "Человек (вариант)",
                "description": "Вариант человека",
                "inherit": {"ability_bonuses": False},
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

        # Прямые импорты get_int_input — патчим точки использования.
        for target in (
            "ui.menus.console.get_int_input",
            "ui.menus.stats.stats_methods.get_int_input",
            "ui.menus.stats.stats_shared.get_int_input",
            "ui.menus.creation.expertise.get_int_input",
        ):
            monkeypatch.setattr(target, fake_get_int_input)

    return _patch


@pytest.fixture
def patch_press_enter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Заглушка press_enter для UI smoke-тестов."""
    from ui.menus import console

    monkeypatch.setattr(console, "press_enter", lambda strings: None)


@pytest.fixture
def minimal_character() -> Any:
    """Минимальный сохранённый персонаж для hub-тестов."""
    from tests.creation_helpers import minimal_character as _minimal

    return _minimal()


@pytest.fixture
def fighter_l3() -> Any:
    """Боец 3 уровня для progression/level-up."""
    from core.character.models import Character
    from core.types import CharacterClass

    return Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
        level=3,
        stats={"constitution": 14, "strength": 16},
        current_hp=28,
        max_hp=28,
        experience=2700,
        difficulty="normal",
    )


@pytest.fixture
def fighter_l1_hardcore() -> Any:
    """Боец 1 уровня HardCore."""
    from core.character.models import Character
    from core.types import CharacterClass

    return Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
        level=1,
        stats={"constitution": 14},
        current_hp=7,
        max_hp=7,
        experience=0,
        difficulty="hardcore",
    )


@pytest.fixture
def patch_level_up_ui(monkeypatch: pytest.MonkeyPatch) -> None:
    """Заглушки UI повышения уровня."""
    from ui.menus.progression import level_up as level_up_menu

    monkeypatch.setattr(level_up_menu, "press_enter", lambda strings: None)
    monkeypatch.setattr(
        level_up_menu, "print_screen_header", lambda strings: None
    )
