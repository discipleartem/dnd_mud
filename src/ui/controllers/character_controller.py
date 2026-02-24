"""Контроллеры UI слоя для работы с Use Cases.

Изолирует UI от бизнес-логики, используя Use Cases
следуя принципам Clean Architecture.
"""

from typing import Any

from src.interfaces.repositories import ICharacterRepository, IRaceRepository
from src.ui.adapters.domain_adapters import ValidationErrorAdapter
from src.ui.dto.character_dto import (
    CharacterDTO,
    RaceDTO,
    ValidationErrorDTO,
)
from src.use_cases.character_creation import (
    CreateCharacterUseCase,
    ValidateCharacterUseCase,
)


class CharacterController:
    """Контроллер для управления персонажами."""

    def __init__(
        self,
        character_repository: ICharacterRepository,
        race_repository: IRaceRepository,
    ):
        """Инициализировать контроллер.

        Args:
            character_repository: Репозиторий персонажей
            race_repository: Репозиторий рас
        """
        self.character_repository = character_repository
        self.race_repository = race_repository

        # Use Cases
        self.create_character_use_case = CreateCharacterUseCase(
            character_repository, race_repository
        )
        self.validate_character_use_case = ValidateCharacterUseCase()

    def create_character(
        self,
        name: str,
        race_name: str = "",
        subrace_name: str = "",
        character_class: str = "",
        ability_scores: dict[str, int] = None,
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
        return self.create_character_use_case.execute(
            name=name,
            race_name=race_name,
            subrace_name=subrace_name,
            character_class=character_class,
            ability_scores=ability_scores,
        )

    def validate_character(
        self, character_dto: CharacterDTO
    ) -> list[ValidationErrorDTO]:
        """Валидировать персонажа.

        Args:
            character_dto: DTO персонажа

        Returns:
            Список ошибок валидации
        """
        return self.validate_character_use_case.execute(character_dto)

    def save_character(
        self, character_dto: CharacterDTO
    ) -> tuple[CharacterDTO, list[ValidationErrorDTO]]:
        """Сохранить персонажа.

        Args:
            character_dto: DTO персонажа

        Returns:
            Кортеж из (сохраненный DTO, список ошибок)
        """
        try:
            # Валидация перед сохранением
            errors = self.validate_character(character_dto)
            if errors:
                return character_dto, errors

            # Здесь должна быть логика сохранения через Use Case
            # Пока возвращаем без изменений
            return character_dto, []

        except Exception as e:
            error = ValidationErrorAdapter.to_dto(
                "save", f"Ошибка сохранения: {str(e)}"
            )
            return character_dto, [error]


class RaceController:
    """Контроллер для управления расами."""

    def __init__(self, race_repository: IRaceRepository):
        """Инициализировать контроллер.

        Args:
            race_repository: Репозиторий рас
        """
        self.race_repository = race_repository

    def get_available_races(self) -> list[RaceDTO]:
        """Получить доступные расы.

        Returns:
            Список DTO рас
        """
        try:
            races = self.race_repository.find_all()
            from src.ui.adapters.domain_adapters import RaceAdapter

            return [RaceAdapter.to_dto(race) for race in races]
        except Exception as e:
            print(f"Ошибка при загрузке рас: {e}")
            return []

    def get_race_details(self, race_name: str) -> RaceDTO:
        """Получить детальную информацию о расе.

        Args:
            race_name: Название расы

        Returns:
            DTO расы с детальной информацией
        """
        try:
            race = self.race_repository.find_by_name(race_name)
            if not race:

                raise ValueError(f"Раса '{race_name}' не найдена")

            from src.ui.adapters.domain_adapters import RaceAdapter

            return RaceAdapter.to_dto(race)

        except Exception as e:
            # Возвращаем пустую DTO при ошибке
            return RaceDTO(name=f"Ошибка: {str(e)}")

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
        errors = []

        if not race_name or not race_name.strip():
            errors.append(
                ValidationErrorAdapter.to_dto(
                    "race", "Название расы не может быть пустым"
                )
            )
            return errors

        try:
            race = self.race_repository.find_by_name(race_name)
            if not race:
                errors.append(
                    ValidationErrorAdapter.to_dto(
                        "race", f"Раса '{race_name}' не найдена"
                    )
                )
                return errors

            # Проверка подрасы если указана
            if subrace_name and subrace_name.strip():
                subrace = self.race_repository.find_subrace_by_name(
                    race_name, subrace_name
                )
                if not subrace:
                    errors.append(
                        ValidationErrorAdapter.to_dto(
                            "subrace", f"Подраса '{subrace_name}' не найдена"
                        )
                    )

        except Exception as e:
            errors.append(
                ValidationErrorAdapter.to_dto(
                    "race", f"Ошибка при проверке расы: {str(e)}"
                )
            )

        return errors


class MenuController:
    """Контроллер для управления меню."""

    def __init__(
        self,
        character_controller: CharacterController,
        race_controller: RaceController,
    ):
        """Инициализировать контроллер.

        Args:
            character_controller: Контроллер персонажей
            race_controller: Контроллер рас
        """
        self.character_controller = character_controller
        self.race_controller = race_controller

    def handle_new_character_creation(self) -> dict[str, Any]:
        """Обработать создание нового персонажа.

        Returns:
            Словарь с результатом операции
        """
        result = {
            "success": False,
            "character": None,
            "errors": [],
            "message": "",
        }

        try:
            # Здесь будет логика взаимодействия с пользователем
            # через UI для получения данных персонажа

            # Временные данные для теста
            character_dto, errors = self.character_controller.create_character(
                name="Тестовый персонаж",
                race_name="Человек",
                character_class="Воин",
                ability_scores={
                    "strength": 16,
                    "dexterity": 14,
                    "constitution": 15,
                    "intelligence": 12,
                    "wisdom": 13,
                    "charisma": 10,
                },
            )

            if errors:
                result["errors"] = [
                    {"field": err.field, "message": err.message}
                    for err in errors
                ]
                result["message"] = "Ошибки валидации"
            else:
                result["success"] = True
                result["character"] = character_dto
                result["message"] = "Персонаж успешно создан"

        except Exception as e:
            result["message"] = f"Ошибка: {str(e)}"

        return result

    def get_menu_data(self) -> dict[str, Any]:
        """Получить данные для меню.

        Returns:
            Словарь с данными меню
        """
        return {
            "available_races": self.race_controller.get_available_races(),
            "total_characters": len(
                self.character_controller.character_repository.find_all()
            ),
        }
