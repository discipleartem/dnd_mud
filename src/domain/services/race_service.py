"""Доменный сервис для работы с расами.

Содержит бизнес-логику связанную с расами D&D.
Следует принципам Domain-Driven Design.
"""

import logging

from src.domain.entities.race import Race, SubRace

logger = logging.getLogger(__name__)


class RaceService:
    """Доменный сервис для работы с расами.

    Содержит бизнес-логику для работы с расами и подрасами.
    """

    def __init__(self, available_races: list[Race]):
        """Инициализация сервиса.

        Args:
            available_races: Список доступных рас
        """
        self._races = {race.name.lower(): race for race in available_races}

    def get_race_by_name(self, name: str) -> Race | None:
        """Получить расу по названию.

        Args:
            name: Название расы

        Returns:
            Раса или None если не найдена
        """
        return self._races.get(name.lower())

    def get_subrace_by_name(
        self, race_name: str, subrace_name: str
    ) -> SubRace | None:
        """Получить подрасу по названию.

        Args:
            race_name: Название основной расы
            subrace_name: Название подрасы

        Returns:
            Подраса или None если не найдена
        """
        race = self.get_race_by_name(race_name)
        if not race:
            return None

        return race.subraces.get(subrace_name.lower())

    def get_all_race_names(self) -> list[str]:
        """Получить список всех названий рас.

        Returns:
            Список названий рас
        """
        return [race.name for race in self._races.values()]

    def get_subraces_for_race(self, race_name: str) -> list[str]:
        """Получить список подрас для расы.

        Args:
            race_name: Название расы

        Returns:
            Список названий подрас
        """
        race = self.get_race_by_name(race_name)
        if not race:
            return []

        return [subrace.name for subrace in race.subraces.values()]

    def get_race_languages(
        self, race_name: str, subrace_name: str | None = None
    ) -> list[str]:
        """Получить языки доступные для расы.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы (опционально)

        Returns:
            Список кодов языков
        """
        race = self.get_race_by_name(race_name)
        if not race:
            return []

        languages = set(race.languages)

        # Добавляем языки от подрасы
        if subrace_name:
            subrace = self.get_subrace_by_name(race_name, subrace_name)
            if subrace and hasattr(subrace, "languages"):
                languages.update(subrace.languages)

        return list(languages)

    def get_race_ability_bonuses(
        self, race_name: str, subrace_name: str | None = None
    ) -> dict[str, int]:
        """Получить бонусы к характеристикам от расы.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы (опционально)

        Returns:
            Словарь бонусов к характеристикам
        """
        race = self.get_race_by_name(race_name)
        if not race:
            return {}

        bonuses = race.ability_bonuses.copy()

        # Добавляем бонусы от подрасы
        if subrace_name:
            subrace = self.get_subrace_by_name(race_name, subrace_name)
            if subrace and hasattr(subrace, "ability_bonuses"):
                for ability, bonus in subrace.ability_bonuses.items():
                    bonuses[ability] = bonuses.get(ability, 0) + bonus

        return bonuses

    def validate_race_selection(
        self, race_name: str, subrace_name: str | None = None
    ) -> list[str]:
        """Валидировать выбор расы и подрасы.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы (опционально)

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Проверяем расу
        if not race_name.strip():
            errors.append("Название расы не может быть пустым")
        elif not self.get_race_by_name(race_name):
            errors.append(f"Неизвестная раса: {race_name}")

        # Проверяем подрасу
        if subrace_name:
            if not race_name.strip():
                errors.append("Нельзя выбрать подрасу без основной расы")
            else:
                subrace = self.get_subrace_by_name(race_name, subrace_name)
                if not subrace:
                    errors.append(
                        f"Неизвестная подраса: {subrace_name} для расы {race_name}"
                    )

        return errors

    def get_race_features(
        self, race_name: str, subrace_name: str | None = None
    ) -> list[str]:
        """Получить черты расы и подрасы.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы (опционально)

        Returns:
            Список описаний черт
        """
        race = self.get_race_by_name(race_name)
        if not race:
            return []

        features = []

        # Черты основной расы
        if hasattr(race, "features"):
            features.extend([feature.name for feature in race.features])

        # Черты подрасы
        if subrace_name:
            subrace = self.get_subrace_by_name(race_name, subrace_name)
            if subrace and hasattr(subrace, "features"):
                features.extend([feature.name for feature in subrace.features])

        return features
