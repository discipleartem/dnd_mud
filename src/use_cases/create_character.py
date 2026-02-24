"""Use Case для создания персонажа.

Реализует сценарий создания персонажа согласно Clean Architecture.
Координирует доменную логику и инфраструктурные сервисы.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from src.domain.entities.character import Character
from src.domain.services.character_creation_service import (
    CharacterCreationService,
)
from src.domain.value_objects.ability_scores import AbilityScores
from src.interfaces.repositories import (
    ICharacterRepository,
    ILanguageRepository,
    IRaceRepository,
)
from src.interfaces.services import IValidationService
from src.utils.logging_helpers import (
    log_debug,
    log_error,
    log_info,
)
from src.utils.validation_helpers import (
    validate_non_empty_string,
    validate_range,
)

# Настройка логирования
logger = logging.getLogger(__name__)


@dataclass
class CreateCharacterRequest:
    """DTO запроса на создание персонажа."""

    name: str
    ability_scores: dict[str, int]
    race_name: str | None = None
    subrace_name: str | None = None
    character_class: str = ""
    level: int = 1
    languages_to_learn: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        pass


@dataclass
class CreateCharacterResponse:
    """DTO ответа на создание персонажа."""

    character: Character
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Инициализация предупреждений."""
        pass


class CharacterCreationError(Exception):
    """Исключение при создании персонажа."""

    def __init__(self, message: str, errors: list[str] | None = None):
        """Инициализация исключения.

        Args:
            message: Сообщение об ошибке
            errors: Список конкретных ошибок
        """
        super().__init__(message)
        self.errors = errors or []


class CreateCharacterUseCase:
    """Use Case для создания персонажа.

    Реализует сценарий создания персонажа, координируя
    доменную логику и инфраструктурные сервисы.
    """

    def __init__(
        self,
        character_repository: ICharacterRepository,
        race_repository: IRaceRepository,
        language_repository: ILanguageRepository,
        validation_service: IValidationService,
        character_creation_service: CharacterCreationService,
    ):
        """Инициализация Use Case.

        Args:
            character_repository: Репозиторий персонажей
            race_repository: Репозиторий рас
            language_repository: Репозиторий языков
            validation_service: Сервис валидации
            character_creation_service: Доменный сервис создания персонажей
        """
        self._character_repo = character_repository
        self._race_repo = race_repository
        self._language_repo = language_repository
        self._validation_service = validation_service
        self._creation_service = character_creation_service

    def execute(
        self, request: CreateCharacterRequest
    ) -> CreateCharacterResponse:
        """Создать персонажа.

        Args:
            request: Данные для создания персонажа

        Returns:
            Ответ с созданным персонажем

        Raises:
            CharacterCreationError: При ошибках создания
        """
        log_info(f"Начало создания персонажа: {request.name}")
        warnings = []

        try:
            # 1. Валидация запроса
            log_debug("Валидация запроса на создание персонажа")
            validation_errors = self._validate_request(request)
            if validation_errors:
                log_error(f"Ошибки валидации запроса: {validation_errors}")
                raise CharacterCreationError(
                    "Ошибки валидации запроса", validation_errors
                )

            # 2. Подготовка данных
            log_debug("Подготовка данных для создания персонажа")
            character_data = self._prepare_character_data(request)

            # 3. Создание персонажа через доменный сервис
            log_debug("Создание персонажа через доменный сервис")
            character = self._creation_service.create_character(character_data)

            # 4. Дополнительная валидация созданного персонажа
            log_debug("Валидация созданного персонажа")
            character_errors = (
                self._validation_service.validate_character_creation(
                    character_data
                )
            )
            if character_errors:
                log_error(f"Ошибки валидации персонажа: {character_errors}")
                raise CharacterCreationError(
                    "Ошибки валидации персонажа", character_errors
                )

            # 5. Изучение дополнительных языков
            if request.languages_to_learn:
                log_debug(
                    "Изучение дополнительных языков: "
                    f"{request.languages_to_learn}"
                )
                language_warnings = self._learn_additional_languages(
                    character, request.languages_to_learn
                )
                warnings.extend(language_warnings)

            # 6. Сохранение персонажа
            log_debug("Сохранение персонажа в репозитории")
            saved_character = self._character_repo.save(character)

            log_info(f"Персонаж {request.name} успешно создан")
            return CreateCharacterResponse(
                character=saved_character, warnings=warnings
            )

        except CharacterCreationError as e:
            log_error(f"Ошибка создания персонажа {request.name}: {e}")
            raise
        except Exception as e:
            log_error(
                "Неожиданная ошибка при создании персонажа "
                f"{request.name}: {e}"
            )
            raise CharacterCreationError(
                f"Ошибка при создании персонажа: {e}"
            ) from None

    def _validate_request(self, request: CreateCharacterRequest) -> list[str]:
        """Валидировать запрос.

        Args:
            request: Запрос на создание

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Базовая валидация с использованием утилит
        try:
            validate_non_empty_string(request.name, "Имя персонажа")
        except ValueError as e:
            errors.append(str(e))

        try:
            validate_range(request.level, 1, 20, "Уровень персонажа")
        except ValueError as e:
            errors.append(str(e))

        # Валидация расы
        if request.race_name:
            race = self._race_repo.find_by_name(request.race_name)
            if not race:
                errors.append(f"Раса не найдена: {request.race_name}")
            else:
                # Валидация подрасы
                if request.subrace_name:
                    subrace = race.get_subrace_by_name(request.subrace_name)
                    if not subrace:
                        errors.append(
                            f"Подраса не найдена: {request.subrace_name}"
                        )

        # Валидация характеристик
        try:
            AbilityScores.from_dict(request.ability_scores)
        except ValueError as e:
            errors.append(f"Ошибка в характеристиках: {e}")

        return errors

    def _prepare_character_data(
        self, request: CreateCharacterRequest
    ) -> dict[str, Any]:
        """Подготовить данные для создания персонажа.

        Args:
            request: Запрос на создание

        Returns:
            Словарь данных для доменного сервиса
        """
        return {
            "name": request.name,
            "race": request.race_name,
            "subrace": request.subrace_name,
            "character_class": request.character_class,
            "level": request.level,
            "ability_scores": request.ability_scores,
        }

    def _learn_additional_languages(
        self, character: Character, language_codes: list[str]
    ) -> list[str]:
        """Изучить дополнительные языки.

        Args:
            character: Персонаж
            language_codes: Коды языков для изучения

        Returns:
            Список предупреждений
        """
        warnings = []

        for language_code in language_codes:
            language = self._language_repo.find_by_code(language_code)
            if not language:
                warnings.append(f"Язык не найден: {language_code}")
                continue

            if not character.can_learn_language(language):
                warnings.append(
                    f"Персонаж не может изучить язык: {language_code}"
                )
                continue

            try:
                character.learn_language(language_code)
            except ValueError as e:
                warnings.append(
                    f"Не удалось изучить язык {language_code}: {e}"
                )

        return warnings

    def get_available_races(self) -> list[str]:
        """Получить список доступных рас.

        Returns:
            Список названий рас
        """
        races = self._race_repo.find_all()
        return [race.name for race in races]

    def get_available_languages(self) -> list[str]:
        """Получить список доступных языков.

        Returns:
            Список кодов языков
        """
        languages = self._language_repo.find_all()
        return [lang.code for lang in languages]

    def validate_character_data(
        self, character_data: dict[str, Any]
    ) -> list[str]:
        """Валидировать данные персонажа.

        Args:
            character_data: Данные персонажа

        Returns:
            Список ошибок валидации
        """
        return self._validation_service.validate_character_creation(
            character_data
        )
