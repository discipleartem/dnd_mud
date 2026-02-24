"""Доменный сервис создания персонажа.

Содержит бизнес-логику для создания и валидации персонажей.
Следует принципам Domain-Driven Design.
"""

import logging
from typing import Any

from src.domain.entities.character import Character
from src.domain.entities.language import Language
from src.domain.entities.race import Race
from src.domain.services.ability_service import AbilityService
from src.domain.services.language_service import LanguageService
from src.domain.services.race_service import RaceService
from src.domain.value_objects.ability_scores import AbilityScores

logger = logging.getLogger(__name__)


class CharacterCreationService:
    """Доменный сервис создания персонажей.

    Координирует сложную бизнес-логику создания персонажей,
    включая валидацию и применение правил.
    """

    def __init__(
        self, available_races: list[Race], available_languages: list[Language]
    ):
        """Инициализация сервиса.

        Args:
            available_races: Список доступных рас
            available_languages: Список доступных языков
        """
        self._race_service = RaceService(available_races)
        self._language_service = LanguageService(available_languages)
        self._ability_service = AbilityService()
        self._races = {race.name: race for race in available_races}

        logger.info(
            f"CharacterCreationService инициализирован с {len(available_races)} расами и {len(available_languages)} языками"
        )

    def create_character(self, character_data: dict[str, Any]) -> Character:
        """Создать персонажа с валидацией.

        Args:
            character_data: Данные для создания персонажа

        Returns:
            Созданный персонаж

        Raises:
            ValueError: Если данные невалидны
        """
        # Валидация
        errors = self.validate_character_data(character_data)
        if errors:
            raise ValueError(f"Ошибки валидации: {'; '.join(errors)}")

        # Создание персонажа
        name = character_data["name"]
        race_name = character_data.get("race", "").lower()
        subrace_name = character_data.get("subrace", "").lower()
        character_class = character_data.get("character_class", "")
        level = character_data.get("level", 1)
        ability_scores_data = character_data.get("ability_scores", {})

        # Поиск расы
        race = None
        subrace = None

        if race_name:
            race = self._find_race_by_name(race_name)
            if not race:
                raise ValueError(f"Раса не найдена: {race_name}")

            # Поиск подрасы
            if subrace_name:
                subrace = race.get_subrace_by_name(subrace_name)
                if not subrace:
                    raise ValueError(
                        f"Подраса не найдена: {subrace_name} для расы {race_name}"
                    )

        # Создание характеристик
        ability_scores = AbilityScores.from_dict(ability_scores_data)

        # Создание персонажа
        character = Character(
            name=name,
            race=race,
            character_class=character_class,
            level=level,
            subrace=subrace,
            ability_scores=ability_scores,
        )

        return character

    def validate_character_data(
        self, character_data: dict[str, Any]
    ) -> list[str]:
        """Валидировать данные персонажа.

        Args:
            character_data: Данные для валидации

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Проверка обязательных полей
        if not character_data.get("name", "").strip():
            errors.append("Имя персонажа обязательно")

        # Валидация уровня
        level = character_data.get("level", 1)
        if not isinstance(level, int) or level < 1 or level > 20:
            errors.append("Уровень должен быть числом от 1 до 20")

        # Валидация расы
        race_name = character_data.get("race", "")
        if race_name:
            race = self._find_race_by_name(race_name.lower())
            if not race:
                errors.append(f"Неизвестная раса: {race_name}")
            else:
                # Валидация подрасы
                subrace_name = character_data.get("subrace", "")
                if subrace_name:
                    subrace = race.get_subrace_by_name(subrace_name.lower())
                    if not subrace:
                        errors.append(
                            f"Подраса {subrace_name} не найдена для расы {race_name}"
                        )

        # Валидация характеристик
        ability_scores = character_data.get("ability_scores", {})
        if ability_scores:
            try:
                AbilityScores.from_dict(ability_scores)
            except ValueError as e:
                errors.append(f"Ошибка в характеристиках: {e}")

        # Валидация совместимости расы и класса
        if race_name and character_data.get("character_class"):
            race = self._find_race_by_name(race_name.lower())
            if race:
                race_errors = race.validate_character_compatibility(
                    character_data
                )
                errors.extend(race_errors)

        return errors

    def _find_race_by_name(self, race_name: str) -> Race | None:
        """Найти расу по названию.

        Args:
            race_name: Название расы

        Returns:
            Раса или None если не найдена
        """
        return self._race_service.get_race_by_name(race_name)

    def get_available_races(self) -> list[Race]:
        """Получить список доступных рас.

        Returns:
            Список доступных рас
        """
        return list(self._race_service._races.values())

    def get_race_by_name(self, race_name: str) -> Race | None:
        """Получить расу по названию.

        Args:
            race_name: Название расы

        Returns:
            Раса или None если не найдена
        """
        return self._race_service.get_race_by_name(race_name)

    def get_subraces_for_race(self, race_name: str) -> list[str]:
        """Получить подрасы для указанной расы.

        Args:
            race_name: Название расы

        Returns:
            Список названий подрас
        """
        return self._race_service.get_subraces_for_race(race_name)

    def calculate_point_buy_cost(self, ability_scores: dict[str, int]) -> int:
        """Рассчитать стоимость характеристик в системе point buy.

        Args:
            ability_scores: Характеристики

        Returns:
            Стоимость в очках

        Raises:
            ValueError: Если характеристики невалидны
        """
        scores = AbilityScores.from_dict(ability_scores)
        return scores.get_point_buy_cost()

    def suggest_races_for_class(self, character_class: str) -> list[Race]:
        """Предложить расы для указанного класса.

        Args:
            character_class: Класс персонажа

        Returns:
            Список подходящих рас
        """
        # Простая эвристика - можно усложнить по мере необходимости
        class_bonuses = {
            "fighter": ["strength", "constitution"],
            "wizard": ["intelligence"],
            "cleric": ["wisdom", "charisma"],
            "rogue": ["dexterity", "intelligence"],
            "barbarian": ["strength", "constitution"],
            "bard": ["charisma", "dexterity"],
            "druid": ["wisdom", "constitution"],
            "monk": ["dexterity", "wisdom"],
            "paladin": ["strength", "charisma"],
            "ranger": ["dexterity", "wisdom"],
            "sorcerer": ["charisma"],
            "warlock": ["charisma"],
        }

        preferred_bonuses = class_bonuses.get(character_class.lower(), [])
        if not preferred_bonuses:
            return list(self._races.values())

        # Ищем расы с подходящими бонусами
        suitable_races = []
        for race in self._races.values():
            race_bonuses = set(race.ability_bonuses.keys())
            if any(bonus in race_bonuses for bonus in preferred_bonuses):
                suitable_races.append(race)

        return suitable_races if suitable_races else list(self._races.values())

    def get_max_languages_for_character(self, character: Character) -> int:
        """Получить максимальное количество языков для персонажа.

        Args:
            character: Персонаж

        Returns:
            Максимальное количество языков
        """
        # Базовое количество языков от расы
        base_languages = len(character.race.languages) if character.race else 1

        # Бонус от интеллекта
        int_mod = character.get_ability_modifier("intelligence")

        # Общее количество: базовые + бонус от интеллекта
        return max(base_languages, base_languages + int_mod)

    def can_learn_more_languages(self, character: Character) -> bool:
        """Проверить, может ли персонаж выучить ещё языки.

        Args:
            character: Персонаж

        Returns:
            True если может выучить ещё языки
        """
        current_languages = len(character.languages)
        max_languages = self.get_max_languages_for_character(character)

        return current_languages < max_languages
