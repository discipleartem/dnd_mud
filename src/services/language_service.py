"""
Сервис для централизованной работы с языками в D&D MUD.

Реализует паттерн Service для унификации доступа к данным языков
и их локализации. Использует существующий i18n менеджер.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from i18n import t
from src.core.yaml_utils import BaseYamlLoader


@dataclass
class LanguageMechanics:
    """Игровые механики языка."""

    script: str = ""
    is_default: bool = False
    learnable_by_all: bool = False
    learnable_by: list[str] = field(default_factory=list)
    race_bonus: list[str] = field(default_factory=list)
    learnable_by_special: list[str] = field(default_factory=list)
    magic_language: bool = False
    secret_language: bool = False
    evil_alignment: bool = False
    good_alignment: bool = False
    lawful_evil_alignment: bool = False


@dataclass
class Language:
    """Язык в D&D."""

    code: str
    type: str
    difficulty: str
    localization_keys: dict[str, str] = field(default_factory=dict)
    mechanics: LanguageMechanics = field(default_factory=LanguageMechanics)
    fallback_data: dict[str, str] = field(default_factory=dict)

    def is_available_for_race(self, race_code: str) -> bool:
        """Проверить доступность языка для расы.

        Args:
            race_code: Код расы для проверки.

        Returns:
            True если язык доступен для расы, иначе False.
        """
        return (
            self.mechanics.learnable_by_all
            or race_code in self.mechanics.learnable_by
            or race_code in self.mechanics.race_bonus
        )

    def is_available_for_class(self, class_code: str) -> bool:
        """Проверить доступность языка для класса.

        Args:
            class_code: Код класса для проверки.

        Returns:
            True если язык доступен для класса, иначе False.
        """
        return class_code in self.mechanics.learnable_by_special


class LanguageService(BaseYamlLoader):
    """Централизованный сервис для работы с языками.

    Реализует паттерн Service для унификации доступа к данным языков
    и их локализации.
    """

    def __init__(self, data_path: Path | None = None) -> None:
        """Инициализация сервиса.

        Args:
            data_path: Путь к файлу с данными языков.
        """
        if data_path is None:
            base_path = Path(__file__).parent.parent.parent
            data_path = base_path / "data" / "languages.yaml"
        super().__init__(data_path)
        self._languages: dict[str, Language] = {}
        self._metadata: dict[str, Any] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Загрузить данные из YAML файла."""
        try:
            data = self._load_yaml_data()
            self._metadata = data.get("language_metadata", {})
            self._languages = self._parse_languages(data.get("languages", {}))
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки данных языков: {e}") from e

    def _parse_languages(
        self, languages_data: dict[str, Any]
    ) -> dict[str, Language]:
        """Распарсить данные языков в объекты Language.

        Args:
            languages_data: Сырые данные языков из YAML

        Returns:
            Словарь объектов Language
        """
        result = {}
        for lang_code, lang_data in languages_data.items():
            result[lang_code] = self._create_language_object(
                lang_code, lang_data
            )
        return result

    def _create_language_object(
        self, lang_code: str, lang_data: dict[str, Any]
    ) -> Language:
        """Создать объект Language из данных.

        Args:
            lang_code: Код языка
            lang_data: Данные языка

        Returns:
            Объект Language
        """
        mechanics = LanguageMechanics(**lang_data.get("mechanics", {}))

        return Language(
            code=lang_data["code"],
            type=lang_data["type"],
            difficulty=lang_data["difficulty"],
            localization_keys=lang_data.get("localization_keys", {}),
            mechanics=mechanics,
            fallback_data=lang_data.get("fallback_data", {}),
        )

    def get_all_languages(self) -> dict[str, Language]:
        """Получить все языки.

        Returns:
            Словарь всех языков с их кодами.
        """
        return self._languages.copy()

    def get_language_by_code(self, code: str) -> Language | None:
        """Получить язык по коду.

        Args:
            code: Код языка.

        Returns:
            Объект языка или None если не найден.
        """
        return self._languages.get(code)

    def _filter_languages(
        self, predicate: Callable[[Language], bool]
    ) -> list[Language]:
        """Отфильтровать языки по предикату.

        Args:
            predicate: Функция-предикат для фильтрации

        Returns:
            Список отфильтрованных языков
        """
        return [lang for lang in self._languages.values() if predicate(lang)]

    def get_languages_by_type(self, language_type: str) -> list[Language]:
        """Получить языки по типу.

        Args:
            language_type: Тип языка для фильтрации.

        Returns:
            Список языков указанного типа.
        """
        return self._filter_languages(lambda lang: lang.type == language_type)

    def get_languages_by_difficulty(self, difficulty: str) -> list[Language]:
        """Получить языки по сложности.

        Args:
            difficulty: Сложность языка для фильтрации.

        Returns:
            Список языков указанной сложности.
        """
        return self._filter_languages(
            lambda lang: lang.difficulty == difficulty
        )

    def get_available_languages_for_race(
        self, race_code: str
    ) -> list[Language]:
        """Получить доступные языки для расы.

        Args:
            race_code: Код расы.

        Returns:
            Список доступных для расы языков.
        """
        return self._filter_languages(
            lambda lang: lang.is_available_for_race(race_code)
        )

    def get_default_language(self) -> Language | None:
        """Получить язык по умолчанию.

        Returns:
            Язык по умолчанию или None если не найден.
        """
        for lang in self._languages.values():
            if lang.mechanics.is_default:
                return lang
        return None

    def get_language_types(self) -> dict[str, str]:
        """Получить типы языков с локализованными названиями.

        Returns:
            Словарь типов языков с их локализованными названиями.
        """
        types: dict[str, str] = {}
        for type_code in self._metadata.get("types", {}):
            result = t(f"language.types.{type_code}")
            types[type_code] = (
                result if isinstance(result, str) else str(result)
            )
        return types

    def get_language_difficulties(self) -> dict[str, str]:
        """Получить сложности языков с локализованными названиями.

        Returns:
            Словарь сложностей языков с их локализованными названиями.
        """
        difficulties: dict[str, str] = {}
        for diff_code in self._metadata.get("difficulties", {}):
            result = t(f"language.difficulties.{diff_code}")
            difficulties[diff_code] = (
                result if isinstance(result, str) else str(result)
            )
        return difficulties

    def get_language_names_list(self) -> list[str]:
        """Получить список локализованных названий всех языков.

        Returns:
            Список локализованных названий языков.
        """
        return [lang.code for lang in self._languages.values()]

    def format_languages_list(self, languages: list[Language]) -> str:
        """Форматировать список языков для отображения.

        Args:
            languages: Список языков для форматирования.

        Returns:
            Отформатированная строка со списком языков.
        """
        if not languages:
            return "Нет доступных языков"

        formatted_languages = [
            f"{lang.code} ({lang.difficulty})" for lang in languages
        ]
        return ", ".join(formatted_languages)


# Глобальный экземпляр сервиса (простой Singleton)
_language_service: LanguageService | None = None


def get_language_service() -> LanguageService:
    """Получить глобальный экземпляр сервиса языков.

    Returns:
        Экземпляр LanguageService.
    """
    global _language_service
    if _language_service is None:
        _language_service = LanguageService()
    return _language_service
