"""Сессия каталогов: gating модов и сброс кэшей."""

from __future__ import annotations

from core.platform.localization import clear_strings_cache
from core.platform.mod_loader import clear_mod_loader_cache
from core.types import GameDifficulty


class CatalogSession:
    """Явное состояние каталогов для сессии игры / тестов.

    Владеет ``difficulty`` для mod gating; кэши сбрасываются через
    ``clear_caches`` / ``bootstrap`` / ``reset``.
    """

    def __init__(self) -> None:
        self.difficulty: GameDifficulty | None = None

    def set_difficulty(self, difficulty: GameDifficulty | None) -> None:
        """Задать режим gating модов."""
        self.difficulty = difficulty

    def clear_caches(self) -> None:
        """Сбросить кэши каталогов и строк."""
        clear_mod_loader_cache()
        clear_strings_cache()

    def bootstrap(self, difficulty: GameDifficulty) -> None:
        """Синхронизировать mod overlay перед сессией приключения."""
        self.set_difficulty(difficulty)
        self.clear_caches()

    def reset(self) -> None:
        """Вернуть gating к normal после сессии приключения."""
        self.set_difficulty("normal")
        self.clear_caches()


_SESSION = CatalogSession()


def get_catalog_session() -> CatalogSession:
    """Процессный экземпляр сессии каталогов."""
    return _SESSION
