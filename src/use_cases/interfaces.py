"""Интерфейсы Use Cases для D&D MUD.

Определяет контракты для сценариев использования системы,
следуя принципам Clean Architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol

from src.ui.dto.character_dto import (
    CharacterDTO,
    LanguageDTO,
    RaceDTO,
    ValidationErrorDTO,
)


class CharacterCreationUseCase(Protocol):
    """Use Case для создания персонажа."""

    def create_character(
        self,
        name: str,
        race_name: str,
        subrace_name: str = "",
        character_class: str = "",
        ability_scores: dict[str, int] | None = None,
    ) -> tuple[CharacterDTO, list[ValidationErrorDTO]]:
        """Создать нового персонажа.

        Args:
            name: Имя персонажа
            race_name: Название расы
            subrace_name: Название подрасы
            character_class: Класс персонажа
            ability_scores: Характеристики

        Returns:
            Кортеж из (DTO персонажа, список ошибок)
        """
        ...


class LanguageManagementUseCase(Protocol):
    """Use Case для управления языками персонажа."""

    def get_available_languages(self) -> list[LanguageDTO]:
        """Получить доступные языки.

        Returns:
            Список доступных языков
        """
        ...

    def learn_language(
        self, character_dto: CharacterDTO, language_code: str
    ) -> tuple[CharacterDTO, list[ValidationErrorDTO]]:
        """Изучить новый язык.

        Args:
            character_dto: DTO персонажа
            language_code: Код языка

        Returns:
            Кортеж из (обновленный DTO, список ошибок)
        """
        ...

    def forget_language(
        self, character_dto: CharacterDTO, language_code: str
    ) -> tuple[CharacterDTO, list[ValidationErrorDTO]]:
        """Забыть язык.

        Args:
            character_dto: DTO персонажа
            language_code: Код языка

        Returns:
            Кортеж из (обновленный DTO, список ошибок)
        """
        ...


class RaceSelectionUseCase(Protocol):
    """Use Case для выбора расы персонажа."""

    def get_available_races(self) -> list[RaceDTO]:
        """Получить доступные расы.

        Returns:
            Список доступных рас
        """
        ...

    def get_race_details(self, race_name: str) -> RaceDTO:
        """Получить детальную информацию о расе.

        Args:
            race_name: Название расы

        Returns:
            DTO расы с детальной информацией
        """
        ...

    def validate_race_selection(
        self, race_name: str, subrace_name: str = ""
    ) -> list[ValidationErrorDTO]:
        """Валидировать выбор расы.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы

        Returns:
            Список ошибок валидации
        """
        ...


class CharacterValidationUseCase(Protocol):
    """Use Case для валидации персонажа."""

    def validate_character(
        self, character_dto: CharacterDTO
    ) -> list[ValidationErrorDTO]:
        """Валидировать персонажа.

        Args:
            character_dto: DTO персонажа

        Returns:
            Список ошибок валидации
        """
        ...

    def validate_ability_scores(
        self, ability_scores: dict[str, int]
    ) -> list[ValidationErrorDTO]:
        """Валидировать характеристики.

        Args:
            ability_scores: Словарь характеристик

        Returns:
            Список ошибок валидации
        """
        ...


class CharacterLoadUseCase(Protocol):
    """Use Case для загрузки персонажей."""

    def load_character(self, character_id: str) -> CharacterDTO:
        """Загрузить персонажа по ID.

        Args:
            character_id: ID персонажа

        Returns:
            DTO персонажа
        """
        ...

    def load_all_characters(self) -> list[CharacterDTO]:
        """Загрузить всех персонажей.

        Returns:
            Список DTO персонажей
        """
        ...

    def save_character(self, character_dto: CharacterDTO) -> CharacterDTO:
        """Сохранить персонажа.

        Args:
            character_dto: DTO персонажа

        Returns:
            Сохраненный DTO персонажа
        """
        ...


class BaseUseCase(ABC):
    """Базовый класс для Use Cases."""

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Выполнить Use Case."""
        pass

    def _create_error_response(
        self, field: str, message: str, error_type: str = "error"
    ) -> list[ValidationErrorDTO]:
        """Создать ответ с ошибкой.

        Args:
            field: Имя поля
            message: Сообщение об ошибке
            error_type: Тип ошибки

        Returns:
            Список с одной ошибкой
        """
        from src.ui.adapters.domain_adapters import ValidationErrorAdapter

        return [ValidationErrorAdapter.to_dto(field, message, error_type)]

    def _create_success_response(
        self, data: Any
    ) -> tuple[Any, list[ValidationErrorDTO]]:
        """Создать успешный ответ.

        Args:
            data: Данные для возврата

        Returns:
            Кортеж из (данные, пустой список ошибок)
        """
        return data, []
