"""Фабрика для создания персонажей.

Реализует паттерн Factory для инкапсуляции логики создания персонажей.
Следует принципам Domain-Driven Design и Clean Architecture.
"""

from typing import Any

from src.domain.entities.character import Character
from src.domain.entities.race import Race, SubRace
from src.domain.value_objects.ability_scores import AbilityScores


class CharacterFactory:
    """Фабрика для создания персонажей D&D.

    Инкапсулирует сложную логику создания персонажей с правильными
    значениями по умолчанию и валидацией.
    """

    @staticmethod
    def create_character(
        name: str,
        race: Race | None = None,
        character_class: str | None = None,
        level: int = 1,
        ability_scores: AbilityScores | None = None,
        languages: list | None = None,
    ) -> Character:
        """Создать персонажа с параметрами по умолчанию.

        Args:
            name: Имя персонажа
            race: Раса персонажа
            character_class: Класс персонажа
            level: Уровень персонажа
            ability_scores: Характеристики персонажа
            languages: Список известных языков

        Returns:
            Созданный персонаж
        """
        # Значения по умолчанию
        if ability_scores is None:
            ability_scores = AbilityScores()

        if character_class is None:
            character_class = ""

        # Создание персонажа
        character = Character(
            name=name,
            race=race,
            character_class=character_class,
            level=level,
            ability_scores=ability_scores,
        )

        # Добавляем языки если указаны
        if languages:
            for language in languages:
                if language not in character._known_languages:
                    character.learn_language(language)

        return character

    @staticmethod
    def create_with_race(
        name: str,
        race: Race,
        subrace: SubRace | None = None,
        character_class: str | None = None,
        level: int = 1,
    ) -> Character:
        """Создать персонажа с расой и подрасой.

        Args:
            name: Имя персонажа
            race: Раса персонажа
            subrace: Подраса персонажа
            character_class: Класс персонажа
            level: Уровень персонажа

        Returns:
            Созданный персонаж с учетом бонусов расы
        """
        if character_class is None:
            character_class = ""

        # Получаем эффективные бонусы к характеристикам
        ability_bonuses = race.get_effective_ability_bonuses(subrace)

        # Создаем характеристики с бонусами
        base_scores = AbilityScores()
        final_scores = base_scores.apply_bonuses(ability_bonuses)

        # Создание персонажа
        character = Character(
            name=name,
            race=race,
            subrace=subrace,
            character_class=character_class,
            level=level,
            ability_scores=final_scores,
        )

        # Добавляем языки от расы
        if hasattr(race, "languages"):
            for language in race.languages:
                if language not in character._known_languages:
                    character.learn_language(language)
        if subrace and hasattr(subrace, "languages"):
            for language in subrace.languages:
                if language not in character._known_languages:
                    character.learn_language(language)

        return character

    @staticmethod
    def create_hero(
        name: str, race_name: str, character_class: str, **kwargs: Any
    ) -> Character:
        """Создать персонажа-героя с оптимизированными характеристиками.

        Args:
            name: Имя персонажа
            race_name: Название расы
            character_class: Класс персонажа
            **kwargs: Дополнительные параметры

        Returns:
            Созданный персонаж-герой
        """
        # TODO: Реализовать логику создания героя с оптимизацией
        # под класс и расу
        return CharacterFactory.create_character(
            name=name, character_class=character_class, **kwargs
        )
