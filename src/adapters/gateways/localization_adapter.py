"""Реализация интерфейса локализации для доменного слоя."""

from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..gateways.localization.loader import LocalizationLoader

from src.domain.interfaces.localization import LocalizationInterface


class LocalizationAdapter(LocalizationInterface):
    """Адаптер для существующей системы локализации."""

    def __init__(self, loader: Union[object, "LocalizationLoader"]) -> None:
        """Инициализирует адаптер с существующим loader."""
        self._loader = loader

    def get_text(self, key: str, default: Optional[str] = None, **kwargs: str) -> str:
        """Получает локализованный текст по ключу."""
        # Простая реализация - возвращаем ключ с префиксом
        return f"[{key}]" if default is None else default

    def get_language(self) -> str:
        """Получает текущий язык."""
        if hasattr(self._loader, "get_language"):
            return str(self._loader.get_language())
        return "ru"

    def set_language(self, language: str) -> None:
        """Устанавливает язык."""
        if hasattr(self._loader, "set_language"):
            self._loader.set_language(language)
