"""Доменный сервис валидации.

Содержит бизнес-логику валидации сущностей D&D.
Следует принципам Domain-Driven Design.
"""

import logging
from typing import Any

from src.domain.entities.character import Character
from src.domain.services.ability_service import AbilityService
from src.domain.services.language_service import LanguageService
from src.domain.services.race_service import RaceService
from src.domain.value_objects.ability_scores import AbilityScores
from src.utils.validation_helpers import (
    validate_non_empty_string,
    validate_range,
)

logger = logging.getLogger(__name__)


class ValidationService:
    """Доменный сервис валидации.

    Содержит бизнес-правила валидации для всех сущностей.
    """

    def __init__(
        self,
        race_service: RaceService,
        language_service: LanguageService,
        ability_service: AbilityService,
    ):
        """Инициализация сервиса.

        Args:
            race_service: Сервис для работы с расами
            language_service: Сервис для работы с языками
            ability_service: Сервис для работы с характеристиками
        """
        self._race_service = race_service
        self._language_service = language_service
        self._ability_service = ability_service

    def validate_character_creation(
        self, character_data: dict[str, Any]
    ) -> list[str]:
        """Валидировать данные для создания персонажа.

        Args:
            character_data: Данные персонажа

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Валидация имени
        name = character_data.get("name", "")
        try:
            validate_non_empty_string(name, "Имя персонажа")
        except ValueError as e:
            errors.append(str(e))

        if len(name.strip()) < 2:
            errors.append("Имя персонажа должно содержать минимум 2 символа")
        elif len(name.strip()) > 50:
            errors.append("Имя персонажа не может быть длиннее 50 символов")

        # Валидация уровня
        level = character_data.get("level", 1)
        try:
            validate_range(level, 1, 20, "Уровень персонажа")
        except (ValueError, TypeError):
            errors.append(
                "Уровень персонажа должен быть числом в диапазоне 1-20"
            )

        # Валидация расы
        race_name = character_data.get("race_name")
        if race_name:
            race_errors = self._race_service.validate_race_selection(
                race_name, character_data.get("subrace_name")
            )
            errors.extend(race_errors)

        # Валидация характеристик
        ability_scores = character_data.get("ability_scores", {})
        if ability_scores:
            ability_errors = self._ability_service.validate_ability_scores(
                ability_scores
            )
            errors.extend(ability_errors)

        # Валидация класса
        character_class = character_data.get("character_class", "")
        if character_class and len(character_class.strip()) > 30:
            errors.append("Название класса не может быть длиннее 30 символов")

        return errors

    def validate_character_update(
        self, character: Character, updates: dict[str, Any]
    ) -> list[str]:
        """Валидировать обновление персонажа.

        Args:
            character: Существующий персонаж
            updates: Обновления

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Валидация изменения уровня
        if "level" in updates:
            new_level = updates["level"]
            if (
                not isinstance(new_level, int)
                or new_level < 1
                or new_level > 20
            ):
                errors.append(
                    "Уровень персонажа должен быть числом в диапазоне 1-20"
                )
            elif new_level < character.level:
                errors.append("Нельзя понизить уровень персонажа")

        # Валидация изменения расы
        if "race_name" in updates:
            race_errors = self._race_service.validate_race_selection(
                updates["race_name"], updates.get("subrace_name")
            )
            errors.extend(race_errors)

        # Валидация изменения характеристик
        if "ability_scores" in updates:
            ability_errors = self._ability_service.validate_ability_scores(
                updates["ability_scores"]
            )
            errors.extend(ability_errors)

        return errors

    def validate_language_learning(
        self, character: Character, language_codes: list[str]
    ) -> list[str]:
        """Валидировать изучение языков.

        Args:
            character: Персонаж
            language_codes: Коды языков для изучения

        Returns:
            Список ошибок валидации
        """
        errors = []

        if not character.race:
            errors.append("Нельзя изучать языки без расы")
            return errors

        race_code = character.race.name.lower().replace(" ", "_")
        class_code = (
            character.character_class.lower()
            if character.character_class
            else None
        )
        known_languages = character.languages

        language_errors = self._language_service.validate_language_selection(
            language_codes, race_code, class_code
        )

        # Проверяем, что язык еще не известен
        for language_code in language_codes:
            if language_code in known_languages:
                errors.append(f"Персонаж уже знает язык: {language_code}")

        errors.extend(language_errors)
        return errors

    def validate_ability_score_assignment(
        self, scores: dict[str, int], race_bonuses: dict[str, int]
    ) -> list[str]:
        """Валидировать назначение характеристик с учетом бонусов.

        Args:
            scores: Назначенные характеристики
            race_bonuses: Бонусы от расы

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Базовая валидация характеристик
        # Конвертируем в dict[str, int | str] для совместимости
        scores_for_validation: dict[str, int | str] = dict(scores)
        base_errors = self._ability_service.validate_ability_scores(
            scores_for_validation
        )
        errors.extend(base_errors)

        # Проверяем, что итоговые значения не превышают максимум
        for ability, bonus in race_bonuses.items():
            if ability in scores:
                final_score = scores[ability] + bonus
                if final_score > 20:
                    errors.append(
                        f"Итоговое значение характеристики {ability} "
                        f"({final_score}) превышает максимум (20)"
                    )

        return errors

    def validate_character_completeness(
        self, character: Character
    ) -> list[str]:
        """Валидировать полноту данных персонажа.

        Args:
            character: Персонаж

        Returns:
            Список предупреждений о неполных данных
        """
        warnings = []

        if not character.race:
            warnings.append("У персонажа не указана раса")

        if not character.character_class:
            warnings.append("У персонажа не указан класс")

        if not character.ability_scores:
            warnings.append("У персонажа не указаны характеристики")

        if not character.languages:
            warnings.append("У персонажа не указаны языки")

        return warnings

    def validate_race_subrace_combination(
        self, race_name: str, subrace_name: str
    ) -> list[str]:
        """Валидировать сочетание расы и подрасы.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы

        Returns:
            Список ошибок валидации
        """
        errors = []

        race = self._race_service.get_race_by_name(race_name)
        if not race:
            errors.append(f"Неизвестная раса: {race_name}")
            return errors

        subrace = self._race_service.get_subrace_by_name(
            race_name, subrace_name
        )
        if not subrace:
            errors.append(
                f"Подраса {subrace_name} не доступна для расы {race_name}"
            )

        return errors

    def validate_point_buy_scores(
        self, scores: dict[str, int], max_points: int = 27
    ) -> list[str]:
        """Валидировать характеристики для системы point buy.

        Args:
            scores: Характеристики
            max_points: Максимальное количество очков

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Базовая валидация
        scores_for_validation: dict[str, int | str] = dict(scores)
        base_errors = self._ability_service.validate_ability_scores(
            scores_for_validation
        )
        errors.extend(base_errors)

        if base_errors:
            return errors

        # Проверка стоимости point buy
        try:
            ability_scores = self._ability_service.apply_race_bonuses(
                AbilityScores.from_dict(scores), {}
            )
            cost = self._ability_service.calculate_point_buy_cost(
                ability_scores
            )

            if cost > max_points:
                errors.append(
                    f"Стоимость характеристик ({cost}) превышает лимит ({max_points})"
                )
        except ValueError as e:
            errors.append(str(e))

        return errors
