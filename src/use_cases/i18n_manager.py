"""Менеджер интернационализации.

Следует Zen Python:
- Простое лучше сложного
- Явное лучше неявного
- Читаемость важна
"""

import locale
import os
from pathlib import Path
from typing import Any

import yaml

from entities.i18n import I18n, I18nConfig, LanguageInfo, TranslationKey
from interfaces.i18n_api import (
    I18nDetector,
    I18nLoader,
    I18nManager,
    I18nTranslator,
    I18nValidator,
)


class YamlI18nLoader(I18nLoader):
    """Загрузчик переводов из YAML файлов с поддержкой модульной архитектуры."""

    def __init__(self, data_dir: Path) -> None:
        """Инициализировать загрузчик.

        Args:
            data_dir: Директория с данными i18n
        """
        self._data_dir = data_dir
        self._i18n_dir = data_dir / "i18n"

    def load_translations(self, language_code: str) -> dict[str, Any]:
        """Загрузить переводы для языка."""
        translations = {}

        # Основной UI файл
        main_file = self._i18n_dir / f"{language_code}.yaml"
        if main_file.exists():
            translations.update(self._load_yaml_file(main_file))

        # Загружаем модульные файлы локализации
        for module_dir in self._data_dir.iterdir():
            if module_dir.is_dir() and module_dir.name != "i18n":
                module_lang_file = module_dir / f"{language_code}.yaml"
                if module_lang_file.exists():
                    module_translations = self._load_yaml_file(module_lang_file)
                    if module_translations:
                        # Используем имя модуля как корневой ключ
                        # Но убираем двойную вложенность, если она есть
                        if module_dir.name in module_translations:
                            module_translations = module_translations[module_dir.name]
                        translations[module_dir.name] = module_translations

        return translations

    def _load_yaml_file(self, file_path: Path) -> dict[str, Any]:
        """Загрузить YAML файл."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError) as e:
            print(f"Ошибка загрузки {file_path}: {e}")
            return {}

    def get_available_languages(self) -> dict[str, LanguageInfo]:
        """Получить доступные языки."""
        languages = {}

        # Базовые языки
        languages["ru"] = LanguageInfo("ru", "Russian", "Русский")
        languages["en"] = LanguageInfo("en", "English", "English")

        return languages


class SystemI18nDetector(I18nDetector):
    """Детектор языка системы."""

    def detect_system_language(self) -> str | None:
        """Определить язык системы."""
        try:
            # Получаем язык системы
            lang, encoding = locale.getdefaultlocale()
            if lang:
                # Конвертируем ru_RU -> ru
                return lang.split("_")[0].lower()
        except (ValueError, AttributeError):
            pass

        # Fallback: проверяем переменные окружения
        for env_var in ["LANG", "LC_ALL", "LC_MESSAGES"]:
            env_value = os.environ.get(env_var)
            if env_value:
                lang_code = env_value.split("_")[0].lower()
                if lang_code in ["ru", "en"]:
                    return lang_code

        return None


class DefaultI18nTranslator(I18nTranslator):
    """Реализация переводчика по умолчанию."""

    def __init__(self, i18n: I18n) -> None:
        """Инициализировать переводчик."""
        self._i18n = i18n

    def translate(
        self,
        key: str,
        context: str | None = None,
        language_code: str | None = None,
        **kwargs: Any
    ) -> str:
        """Перевести строку."""
        translation_key = TranslationKey(key=key, context=context)
        translation = self._i18n.get_translation(translation_key, language_code)

        # Форматируем с параметрами
        if kwargs:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                # Если форматирование не удалось, возвращаем как есть
                return translation

        return translation

    def translate_plural(
        self,
        key: str,
        count: int,
        context: str | None = None,
        language_code: str | None = None,
        **kwargs: Any
    ) -> str:
        """Перевести строку с учетом множественного числа."""
        # Для простоты используем базовый перевод
        # В реальной реализации здесь была бы логика множественных чисел
        kwargs.setdefault("count", count)
        return self.translate(key, context, language_code, **kwargs)

    def set_language(self, language_code: str) -> bool:
        """Установить текущий язык."""
        return self._i18n.set_language(language_code)

    def get_current_language(self) -> str:
        """Получить текущий язык."""
        return self._i18n.current_language


class DefaultI18nValidator(I18nValidator):
    """Валидатор переводов по умолчанию."""

    def validate_translations(self, translations: dict[str, Any]) -> bool:
        """Валидировать структуру переводов."""
        return isinstance(translations, dict)

    def find_missing_keys(
        self,
        base_translations: dict[str, Any],
        target_translations: dict[str, Any],
    ) -> list[str]:
        """Найти отсутствующие ключи."""
        missing: list[str] = []
        self._find_missing_recursive(base_translations, target_translations, "", missing)
        return missing

    def _find_missing_recursive(
        self,
        base: dict[str, Any],
        target: dict[str, Any],
        prefix: str,
        missing: list[str],
    ) -> None:
        """Рекурсивно найти отсутствующие ключи."""
        for key, value in base.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if key not in target:
                missing.append(full_key)
            elif isinstance(value, dict) and isinstance(target[key], dict):
                self._find_missing_recursive(value, target[key], full_key, missing)


class I18nManagerImpl(I18nManager):
    """Реализация менеджера i18n."""

    def __init__(self, data_dir: Path) -> None:
        """Инициализировать менеджер."""
        self._data_dir = data_dir
        self._i18n: I18n | None = None
        self._translator: I18nTranslator | None = None
        self._loader = YamlI18nLoader(data_dir)
        self._detector = SystemI18nDetector()
        self._validator = DefaultI18nValidator()

    def initialize(self, config: I18nConfig) -> None:
        """Инициализировать систему i18n."""
        self._i18n = I18n(config)
        self._translator = DefaultI18nTranslator(self._i18n)

        # Автоопределение языка
        if config.auto_detect_language:
            detected_lang = self._detector.detect_system_language()
            if detected_lang:
                self._i18n.set_language(detected_lang)

        # Загружаем доступные языки
        languages = self._loader.get_available_languages()
        for lang_info in languages.values():
            self._i18n.add_language(lang_info)

    def load_all_translations(self) -> None:
        """Загрузить все доступные переводы."""
        if not self._i18n:
            raise RuntimeError("I18n не инициализирован")

        languages = self._i18n.get_available_languages()
        for lang_code in languages:
            translations = self._loader.load_translations(lang_code)
            if translations:
                self._i18n.load_translations(lang_code, translations)

    def get_translator(self) -> I18nTranslator:
        """Получить интерфейс переводчика."""
        if not self._translator:
            raise RuntimeError("I18n не инициализирован")
        return self._translator

    def reload_translations(self) -> None:
        """Перезагрузить все переводы."""
        if self._i18n:
            self._i18n.clear_cache()
            self.load_all_translations()

    def get_statistics(self) -> dict[str, Any]:
        """Получить статистику системы."""
        if not self._i18n:
            return {"error": "I18n не инициализирован"}

        stats = self._i18n.get_cache_stats()
        stats.update({
            "current_language": self._i18n.current_language,
            "config": {
                "default_language": self._i18n.config.default_language,
                "fallback_language": self._i18n.config.fallback_language,
                "cache_enabled": self._i18n.config.cache_enabled,
                "auto_detect_language": self._i18n.config.auto_detect_language,
            }
        })
        return stats
