"""Доменный сервис для работы с языками.

Содержит бизнес-логику связанную с языками D&D.
Следует принципам Domain-Driven Design.
"""

import logging

from src.domain.entities.language import Language

logger = logging.getLogger(__name__)


class LanguageService:
    """Доменный сервис для работы с языками.

    Содержит бизнес-логику для работы с языками персонажей.
    """

    def __init__(self, available_languages: list[Language]):
        """Инициализация сервиса.

        Args:
            available_languages: Список доступных языков
        """
        self._languages = {lang.code: lang for lang in available_languages}

    def get_language_by_code(self, code: str) -> Language | None:
        """Получить язык по коду.

        Args:
            code: Код языка

        Returns:
            Язык или None если не найден
        """
        return self._languages.get(code)

    def get_languages_by_type(self, language_type: str) -> list[Language]:
        """Получить языки по типу.

        Args:
            language_type: Тип языка (standard, exotic, etc.)

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

    def get_available_for_class(self, class_code: str) -> list[Language]:
        """Получить языки доступные для класса.

        Args:
            class_code: Код класса

        Returns:
            Список доступных языков
        """
        available_languages = []
        for lang in self._languages.values():
            if lang.is_available_for_class(class_code):
                available_languages.append(lang)
        return available_languages

    def can_character_learn_language(
        self, language_code: str, race_code: str, class_code: str | None = None
    ) -> bool:
        """Проверить, может ли персонаж изучить язык.

        Args:
            language_code: Код языка
            race_code: Код расы персонажа
            class_code: Код класса персонажа (опционально)

        Returns:
            True если язык доступен для изучения
        """
        language = self.get_language_by_code(language_code)
        if not language:
            return False

        return language.can_be_learned_by_character(race_code, class_code)

    def get_learnable_languages(
        self,
        race_code: str,
        class_code: str | None = None,
        known_languages: list[str] | None = None,
    ) -> list[Language]:
        """Получить языки, которые может изучить персонаж.

        Args:
            race_code: Код расы персонажа
            class_code: Код класса персонажа (опционально)
            known_languages: Список уже известных языков (опционально)

        Returns:
            Список доступных для изучения языков
        """
        known_languages = known_languages or []
        learnable = []

        for lang in self._languages.values():
            # Пропускаем уже известные языки
            if lang.code in known_languages:
                continue

            # Проверяем доступность для изучения
            if self.can_character_learn_language(
                lang.code, race_code, class_code
            ):
                learnable.append(lang)

        return learnable

    def get_language_difficulty_score(self, language_code: str) -> int:
        """Получить оценку сложности изучения языка.

        Args:
            language_code: Код языка

        Returns:
            Оценка сложности (1-5, где 1 - легко, 5 - очень сложно)
        """
        language = self.get_language_by_code(language_code)
        if not language:
            return 3  # Средняя сложность по умолчанию

        return language.get_learning_difficulty_score()

    def get_exotic_languages(self) -> list[Language]:
        """Получить все экзотические языки.

        Returns:
            Список экзотических языков
        """
        return self.get_languages_by_type("exotic")

    def get_standard_languages(self) -> list[Language]:
        """Получить все стандартные языки.

        Returns:
            Список стандартных языков
        """
        return self.get_languages_by_type("standard")

    def get_magic_languages(self) -> list[Language]:
        """Получить все магические языки.

        Returns:
            Список магических языков
        """
        return [
            lang
            for lang in self._languages.values()
            if lang.is_magic_language()
        ]

    def get_secret_languages(self) -> list[Language]:
        """Получить все секретные языки.

        Returns:
            Список секретных языков
        """
        return [
            lang
            for lang in self._languages.values()
            if lang.is_secret_language()
        ]

    def validate_language_selection(
        self,
        language_codes: list[str],
        race_code: str,
        class_code: str | None = None,
    ) -> list[str]:
        """Валидировать выбор языков.

        Args:
            language_codes: Список кодов языков
            race_code: Код расы персонажа
            class_code: Код класса персонажа (опционально)

        Returns:
            Список ошибок валидации
        """
        errors = []

        for language_code in language_codes:
            if not language_code.strip():
                errors.append("Код языка не может быть пустым")
                continue

            language = self.get_language_by_code(language_code)
            if not language:
                errors.append(f"Неизвестный язык: {language_code}")
                continue

            if not self.can_character_learn_language(
                language_code, race_code, class_code
            ):
                errors.append(f"Язык {language_code} недоступен для изучения")

        return errors

    def get_language_summary(self, language_code: str) -> dict[str, str]:
        """Получить сводную информацию о языке.

        Args:
            language_code: Код языка

        Returns:
            Словарь с информацией о языке
        """
        language = self.get_language_by_code(language_code)
        if not language:
            return {}

        return {
            "code": language.code,
            "type": language.type,
            "difficulty": language.difficulty,
            "is_magic": str(language.is_magic_language()),
            "is_secret": str(language.is_secret_language()),
            "is_exotic": str(language.is_exotic_language()),
            "difficulty_score": str(language.get_learning_difficulty_score()),
        }
