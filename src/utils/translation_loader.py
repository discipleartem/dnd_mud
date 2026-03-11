"""Утилита для загрузки переводов.

Следует KISS - просто и понятно.
"""

import json
from pathlib import Path
from typing import Any, Final

# Путь к файлам переводов
TRANSLATIONS_DIR: Final[Path] = Path(__file__).parent.parent.parent / "data" / "translations"


class TranslationLoader:
    """Простой загрузчик переводов.

    Следует KISS - просто и понятно.
    """

    _translations: dict[str, Any] | None = None

    @classmethod
    def load_translations(cls) -> dict[str, Any]:
        """Загрузить все переводы.

        Returns:
            Словарь переводов вида {language_code: translations_dict}
        """
        if cls._translations is not None:
            return cls._translations

        cls._translations = {}

        # Загружаем каждый файл переводов
        for file_path in TRANSLATIONS_DIR.glob("*.json"):
            language_code = file_path.stem
            try:
                with open(file_path, encoding='utf-8') as f:
                    cls._translations[language_code] = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as error:
                print(f"Ошибка загрузки переводов {language_code}: {error}")
                continue

        return cls._translations

    @classmethod
    def get_translation(cls, language_code: str, key: str, default: str | None = None) -> str | None:
        """Получить перевод по ключу.

        Args:
            language_code: Код языка
            key: Ключ перевода (например, "welcome.title")
            default: Значение по умолчанию если ключ не найден

        Returns:
            Перевод или default
        """
        translations = cls.load_translations()

        # Разбираем вложенный ключ (например, "welcome.title")
        keys = key.split('.')
        current = translations.get(language_code, {})

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current if isinstance(current, str) else default
