"""Упрощённый менеджер локализации для D&D MUD.

Использует YAML файлы вместо gettext .po/.mo для простоты.
Следует принципам KISS и DRY.
"""

from pathlib import Path
from typing import Any

import yaml


class I18nError(Exception):
    """Исключение для ошибок локализации."""


class SimpleI18nManager:
    """Упрощённый менеджер локализации.

    Использует YAML файлы для хранения переводов.
    Реализует паттерн Singleton через module-level экземпляр.
    """

    def __init__(self) -> None:
        """Инициализация менеджера локализации."""
        self._default_language = "ru"
        self._current_language = self._default_language
        self._locales_dir = Path(__file__).parent / "localization"
        self._translations: dict[str, Any] = {}

        self.load_translations(self._default_language)

    def load_translations(self, language_code: str) -> None:
        """Загрузка переводов из YAML файла.

        Args:
            language_code: Код языка (например, 'ru', 'en').

        Raises:
            I18nError: При ошибке загрузки файла локализации.
        """
        yaml_file = self._locales_dir / f"{language_code}.yaml"

        if not yaml_file.exists():
            raise I18nError(f"Файл локализации не найден: {yaml_file}")

        try:
            self._translations = self._load_yaml_file(yaml_file)
            self._current_language = language_code
        except yaml.YAMLError as e:
            raise I18nError(
                f"Ошибка парсинга YAML в файле {yaml_file}: {e}"
            ) from e
        except Exception as e:
            raise I18nError(
                f"Ошибка загрузки локализации из {yaml_file}: {e}"
            ) from e

    def _load_yaml_file(self, yaml_file: Path) -> dict[str, Any]:
        """Загрузить и распарсить YAML файл.

        Args:
            yaml_file: Путь к YAML файлу

        Returns:
            Распарсенные данные из файла

        Raises:
            yaml.YAMLError: При ошибке парсинга YAML
        """
        with open(yaml_file, encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    def get(self, key: str, **kwargs: Any) -> str | list[str]:
        """Получение переведённой строки по ключу.

        Args:
            key: Ключ строки в формате 'section.subsection.key'
            **kwargs: Параметры для форматирования строки

        Returns:
            Переведённая строка, список строк или ключ, если перевод не найден.
        """
        value = self._navigate_to_key(key)

        if isinstance(value, str) and kwargs:
            return self._format_string(value, **kwargs)

        return str(value) if not isinstance(value, list) else value

    def _navigate_to_key(self, key: str) -> Any:
        """Навигация по вложенной структуре ключей."""
        keys = key.split(".")
        value = self._translations

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return key

    def _format_string(self, value: str, **kwargs: Any) -> str:
        """Форматирование строки с параметрами.

        Args:
            value: Строка для форматирования
            **kwargs: Параметры для форматирования

        Returns:
            Отформатированная строка или исходная строка при ошибке.
        """
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            return value

    def get_current_language(self) -> str:
        """Получение текущего языка."""
        return self._current_language

    def get_available_languages(self) -> list[str]:
        """Получение списка доступных языков.

        Returns:
            Список кодов доступных языков.
        """
        if not self._locales_dir.exists():
            return []

        return [
            item.stem
            for item in self._locales_dir.iterdir()
            if item.is_file() and item.suffix == ".yaml"
        ]


    def set_language(self, language_code: str) -> None:
        """Установка языка интерфейса.

        Args:
            language_code: Код языка.
        """
        self.load_translations(language_code)


# Глобальный экземпляр менеджера (простой Singleton)
_i18n_manager = SimpleI18nManager()


# Удобные функции для использования
def t(key: str, **kwargs: Any) -> str | list[str]:
    """Глобальная функция перевода.

    Args:
        key: Ключ строки
        **kwargs: Параметры для форматирования

    Returns:
        Переведённая строка или список строк.
    """
    return _i18n_manager.get(key, **kwargs)


def set_language(language_code: str) -> None:
    """Установка языка интерфейса.

    Args:
        language_code: Код языка.
    """
    _i18n_manager.set_language(language_code)


def get_current_language() -> str:
    """Получение текущего языка."""
    return _i18n_manager.get_current_language()


def get_available_languages() -> list[str]:
    """Получение списка доступных языков.

    Returns:
        Список кодов доступных языков.
    """
    return _i18n_manager.get_available_languages()
