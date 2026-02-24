"""YAML репозиторий языков согласно Clean Architecture.

Реализует Repository Pattern для работы с YAML файлами,
изолируя бизнес-логику от инфраструктуры.
"""

from pathlib import Path
from typing import Any

from src.core.yaml_utils import load_yaml_file
from src.domain.entities.language import Language
from src.interfaces.repositories import ILanguageRepository


class YamlLanguageRepository(ILanguageRepository):
    """YAML репозиторий языков.

    Infrastructure слой - реализует доступ к данным
    через YAML файлы следуя Clean Architecture.
    """

    def __init__(self, data_dir: str = "data") -> None:
        """Инициализировать репозиторий.

        Args:
            data_dir: Директория с YAML файлами
        """
        self._data_dir = Path(data_dir)
        self._languages: dict[str, Language] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Загрузить данные из YAML файлов."""
        try:
            languages_data = load_yaml_file(self._data_dir / "languages.yaml")
            for lang_id, lang_info in languages_data.items():
                language = self._create_language(lang_id, lang_info)
                self._languages[language.code] = language

        except FileNotFoundError as e:
            print(f"⚠️ Файл языков не найден: {e.filename}")

    def _create_language(
        self, lang_id: str, lang_info: dict[str, Any]
    ) -> Language:
        """Создать доменный язык из YAML данных.

        Args:
            lang_id: ID языка
            lang_info: Данные языка из YAML

        Returns:
            Доменная сущность Language
        """
        from src.domain.entities.language import LanguageMechanics

        mechanics = LanguageMechanics(
            script=lang_info.get("script", ""),
            is_default=lang_info.get("is_default", False),
            learnable_by_all=lang_info.get("learnable_by_all", False),
            learnable_by=lang_info.get("learnable_by", []),
            race_bonus=lang_info.get("race_bonus", []),
            learnable_by_special=lang_info.get("learnable_by_special", []),
            magic_language=lang_info.get("magic_language", False),
            secret_language=lang_info.get("secret_language", False),
            evil_alignment=lang_info.get("evil_alignment", False),
            good_alignment=lang_info.get("good_alignment", False),
            lawful_evil_alignment=lang_info.get(
                "lawful_evil_alignment", False
            ),
        )

        return Language(
            code=lang_info.get("code", lang_id),
            type=lang_info.get("type", "standard"),
            difficulty=lang_info.get("difficulty", "medium"),
            localization_keys=lang_info.get("localization_keys", {}),
            mechanics=mechanics,
            fallback_data=lang_info.get("fallback_data", {}),
        )

    def find_by_code(self, code: str) -> Language | None:
        """Найти язык по коду.

        Args:
            code: Код языка

        Returns:
            Язык или None если не найден
        """
        return self._languages.get(code)

    def get_languages_by_type(self, language_type: str) -> list[Language]:
        """Получить языки по типу.

        Args:
            language_type: Тип языка

        Returns:
            Список языков указанного типа
        """
        return [
            lang
            for lang in self._languages.values()
            if lang.type == language_type
        ]

    def get_available_for_race(self, race_code: str) -> list[Language]:
        """Получить языки доступные для расы.

        Args:
            race_code: Код расы

        Returns:
            Список доступных языков
        """
        available_languages = []
        for lang in self._languages.values():
            if lang.is_available_for_race(race_code):
                available_languages.append(lang)
        return available_languages

    def find_by_id(self, entity_id: str) -> Language | None:
        """Найти язык по ID.

        Args:
            entity_id: ID языка

        Returns:
            Язык или None если не найден
        """
        # В текущей реализации ID совпадает с кодом языка
        return self.find_by_code(entity_id)

    def find_all(self) -> list[Language]:
        """Получить все языки.

        Returns:
            Список всех языков
        """
        return list(self._languages.values())

    def save(self, entity: Language) -> Language:
        """Сохранить язык (заглушка).

        Args:
            entity: Язык для сохранения

        Returns:
            Сохраненный язык
        """
        print(f"💾 Сохранение языка {entity.code} (заглушка)")
        return entity

    def delete(self, entity_id: str) -> bool:
        """Удалить язык (заглушка).

        Args:
            entity_id: ID языка для удаления

        Returns:
            True если удален
        """
        print(f"🗑️ Удаление языка с ID {entity_id} (заглушка)")
        return True
