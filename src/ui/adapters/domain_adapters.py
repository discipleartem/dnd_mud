"""Адаптеры для преобразования доменных сущностей в DTO.

Изолирует UI слой от прямых зависимостей доменной логики,
следуя принципам Clean Architecture и паттерну Adapter.
"""

from typing import Any

from src.domain.entities.character import Character as DomainCharacter
from src.domain.entities.language import Language as DomainLanguage
from src.domain.entities.race import (
    Race as DomainRace,
)
from src.domain.entities.race import (
    SubRace as DomainSubRace,
)
from src.domain.value_objects.ability_scores import (
    AbilityScores as DomainAbilityScores,
)
from src.ui.dto.character_dto import (
    AbilityScoreDTO,
    CharacterDTO,
    LanguageDTO,
    RaceDTO,
    ValidationErrorDTO,
)


class CharacterAdapter:
    """Адаптер для преобразования Character сущностей."""

    @staticmethod
    def to_dto(character: DomainCharacter) -> CharacterDTO:
        """Преобразовать доменную сущность в DTO.

        Args:
            character: Доменная сущность персонажа

        Returns:
            DTO для UI слоя
        """
        return CharacterDTO.from_domain(character)

    @staticmethod
    def from_dto(dto: CharacterDTO) -> DomainCharacter:
        """Преобразовать DTO в доменную сущность.

        Args:
            dto: DTO из UI слоя

        Returns:
            Доменная сущность персонажа
        """
        # Для создания доменной сущности нужны раса и характеристики
        # Это будет реализовано в Use Cases
        raise NotImplementedError(
            "Создание доменных сущностей из DTO должно "
            "проходить через Use Cases"
        )


class RaceAdapter:
    """Адаптер для преобразования Race сущностей."""

    @staticmethod
    def to_dto(race: DomainRace) -> RaceDTO:
        """Преобразовать доменную сущность в DTO.

        Args:
            race: Доменная сущность расы

        Returns:
            DTO для UI слоя
        """
        return RaceDTO.from_domain(race)

    @staticmethod
    def to_subrace_dto(subrace: DomainSubRace) -> RaceDTO:
        """Преобразовать доменную подрасу в DTO.

        Args:
            subrace: Доменная сущность подрасы

        Returns:
            DTO для UI слоя
        """
        return RaceDTO(
            name=subrace.name,
            description=getattr(subrace, "description", ""),
            ability_bonuses=getattr(subrace, "ability_bonuses", {}),
            languages=getattr(subrace, "languages", []),
            features=[],
        )


class LanguageAdapter:
    """Адаптер для преобразования Language сущностей."""

    @staticmethod
    def to_dto(language: DomainLanguage) -> LanguageDTO:
        """Преобразовать доменную сущность в DTO.

        Args:
            language: Доменная сущность языка

        Returns:
            DTO для UI слоя
        """
        return LanguageDTO.from_domain(language)


class AbilityScoresAdapter:
    """Адаптер для преобразования характеристик."""

    @staticmethod
    def to_dto(ability_scores: DomainAbilityScores) -> AbilityScoreDTO:
        """Преобразовать доменные характеристики в DTO.

        Args:
            ability_scores: Доменные характеристики

        Returns:
            DTO для UI слоя
        """
        return AbilityScoreDTO(
            strength=ability_scores.strength,
            dexterity=ability_scores.dexterity,
            constitution=ability_scores.constitution,
            intelligence=ability_scores.intelligence,
            wisdom=ability_scores.wisdom,
            charisma=ability_scores.charisma,
        )

    @staticmethod
    def from_dto(dto: AbilityScoreDTO) -> DomainAbilityScores:
        """Преобразовать DTO в доменные характеристики.

        Args:
            dto: DTO из UI слоя

        Returns:
            Доменные характеристики
        """
        return DomainAbilityScores(
            strength=dto.strength,
            dexterity=dto.dexterity,
            constitution=dto.constitution,
            intelligence=dto.intelligence,
            wisdom=dto.wisdom,
            charisma=dto.charisma,
        )


class ValidationErrorAdapter:
    """Адаптер для преобразования ошибок валидации."""

    @staticmethod
    def to_dto(
        field: str, message: str, error_type: str = "error"
    ) -> ValidationErrorDTO:
        """Преобразовать ошибку в DTO.

        Args:
            field: Имя поля с ошибкой
            message: Сообщение об ошибке
            error_type: Тип ошибки

        Returns:
            DTO для UI слоя
        """
        return ValidationErrorDTO(
            field=field,
            message=message,
            error_type=error_type,
        )

    @staticmethod
    def from_validation_errors(errors: list[str]) -> list[ValidationErrorDTO]:
        """Преобразовать список ошибок в DTO.

        Args:
            errors: Список ошибок валидации

        Returns:
            Список DTO для UI слоя
        """
        dtos = []
        for error in errors:
            # Простая парсилка ошибок вида "Поле: сообщение"
            if ":" in error:
                field, message = error.split(":", 1)
                dtos.append(
                    ValidationErrorAdapter.to_dto(
                        field.strip(), message.strip()
                    )
                )
            else:
                dtos.append(ValidationErrorAdapter.to_dto("general", error))
        return dtos


class DomainEntityAdapter:
    """Общий адаптер для работы с доменными сущностями."""

    @staticmethod
    def get_character_summary(character: DomainCharacter) -> dict[str, Any]:
        """Получить сводную информацию о персонаже.

        Args:
            character: Доменная сущность персонажа

        Returns:
            Словарь с информацией для UI
        """
        return character.get_summary()

    @staticmethod
    def get_race_information(race: DomainRace) -> dict[str, Any]:
        """Получить информацию о расе.

        Args:
            race: Доменная сущность расы

        Returns:
            Словарь с информацией для UI
        """
        return {
            "name": race.name,
            "description": getattr(race, "description", ""),
            "size": race.size.category.value,
            "speed": race.speed,
            "ability_bonuses": getattr(race, "ability_bonuses", {}),
            "languages": getattr(race, "languages", []),
            "features_count": len(getattr(race, "features", [])),
        }

    @staticmethod
    def get_language_information(language: DomainLanguage) -> dict[str, Any]:
        """Получить информацию о языке.

        Args:
            language: Доменная сущность языка

        Returns:
            Словарь с информацией для UI
        """
        return {
            "code": language.code,
            "name": language.name,
            "description": getattr(language, "description", ""),
            "type": getattr(language, "type", "standard"),
            "is_learnable": getattr(language, "is_learnable", True),
        }
