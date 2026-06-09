"""Модуль локализации: загрузка YAML-словарей, переключение языка."""

from pathlib import Path
from typing import Any

import yaml


class Localization:
    """Загрузка и хранение строк интерфейса для выбранного языка.

    Пример использования:
        loc = Localization('ru')
        loc('menu.new_game')  # -> "Новая игра"
        loc('menu.exit')      # -> "Выход"
    """

    def __init__(self, language: str = 'ru') -> None:
        self._language: str = language
        self._strings: dict[str, Any] = {}
        self._fallback: dict[str, Any] = {}
        self.load(language)

    @property
    def language(self) -> str:
        """Текущий язык."""
        return self._language

    def load(self, language: str) -> None:
        """Загрузить YAML-словарь для указанного языка."""
        self._language = language
        strings_path = Path('database/strings') / f'{language}.yaml'
        if strings_path.exists():
            with open(strings_path, encoding='utf-8') as f:
                self._strings = yaml.safe_load(f) or {}
        else:
            self._strings = {}

        # fallback — всегда английский
        fallback_path = Path('database/strings/en.yaml')
        if fallback_path.exists():
            with open(fallback_path, encoding='utf-8') as f:
                self._fallback = yaml.safe_load(f) or {}

    def get(self, key: str, **kwargs: Any) -> str:
        """Получить строку по ключу (поддержка вложенных ключей через точку).

        Args:
            key: Ключ вида 'menu.new_game'
            **kwargs: Параметры для форматирования строки

        Returns:
            Переведённая строка или ключ, если перевод не найден
        """
        parts = key.split('.')

        # Поиск в текущем языке
        value = self._deep_get(self._strings, parts)
        if value is None:
            # Fallback на английский
            value = self._deep_get(self._fallback, parts)

        if value is None:
            return key

        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except KeyError:
                return value

        return str(value) if value is not None else key

    def __call__(self, key: str, **kwargs: Any) -> str:
        """Сокращённый вызов: loc('key', param=val)."""
        return self.get(key, **kwargs)

    @staticmethod
    def _deep_get(d: dict[str, Any], parts: list[str]) -> Any | None:
        """Достать значение из вложенного словаря по списку ключей."""
        current: Any = d
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current