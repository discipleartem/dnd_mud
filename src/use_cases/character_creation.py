"""Use Case для создания персонажа D&D.

Реализует бизнес-логику создания персонажа следуя
принципам Clean Architecture и Domain-Driven Design.
"""

from src.domain.factories.character_factory import CharacterFactory
from src.domain.value_objects.ability_scores import (
    AbilityScores as DomainAbilityScores,
)
from src.interfaces.repositories import ICharacterRepository, IRaceRepository
from src.ui.adapters.domain_adapters import CharacterAdapter
from src.ui.adapters.updated_adapters import Character as UpdatedCharacter
from src.ui.adapters.updated_adapters import Race as UpdatedRace
from src.ui.adapters.updated_adapters import SubRace as UpdatedSubRace
from src.ui.dto.character_dto import CharacterDTO, ValidationErrorDTO
from src.use_cases.ability_generation import AbilityGenerationUseCase
from src.use_cases.interfaces import BaseUseCase


class CreateCharacterUseCase(BaseUseCase):
    """Use Case для создания нового персонажа."""

    def __init__(
        self,
        character_repository: ICharacterRepository,
        race_repository: IRaceRepository,
    ):
        """Инициализировать Use Case.

        Args:
            character_repository: Репозиторий персонажей
            race_repository: Репозиторий рас
        """
        self.character_repository = character_repository
        self.race_repository = race_repository

    def execute(
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
        errors = []

        # Валидация имени
        if not name or not name.strip():
            errors.extend(
                self._create_error_response(
                    "name", "Имя персонажа не может быть пустым"
                )
            )

        # Валидация расы
        race = None
        subrace = None

        if race_name:
            try:
                race = self.race_repository.find_by_name(race_name)
                if not race:
                    errors.extend(
                        self._create_error_response(
                            "race", f"Раса '{race_name}' не найдена"
                        )
                    )
            except Exception as e:
                errors.extend(
                    self._create_error_response(
                        "race", f"Ошибка при поиске расы: {str(e)}"
                    )
                )

        # Валидация подрасы
        if subrace_name and race:
            try:
                subrace = self.race_repository.find_subrace_by_name(
                    race_name, subrace_name
                )
                if not subrace:
                    errors.extend(
                        self._create_error_response(
                            "subrace", f"Подраса '{subrace_name}' не найдена"
                        )
                    )
            except Exception as e:
                errors.extend(
                    self._create_error_response(
                        "subrace", f"Ошибка при поиске подрасы: {str(e)}"
                    )
                )

        # Создание характеристик
        domain_ability_scores = None
        if ability_scores:
            domain_ability_scores = self._create_ability_scores(ability_scores)

        # Создание персонажа
        if not errors:
            try:
                character = CharacterFactory.create_character(
                    name=name,
                    race=race,
                    subrace=subrace,
                    character_class=character_class,
                    ability_scores=domain_ability_scores,
                )

                # Сохранение в репозиторий
                saved_character = self.character_repository.save(character)

                # Преобразование в DTO
                character_dto = CharacterAdapter.to_dto(saved_character)

                return character_dto, errors

            except Exception as e:
                errors.extend(
                    self._create_error_response(
                        "general", f"Ошибка при создании персонажа: {str(e)}"
                    )
                )
                empty_character = CharacterDTO(name=name)
                return empty_character, errors

        # Возврат пустого персонажа с ошибками
        empty_character = CharacterDTO(name=name)
        return empty_character, errors

    def create_character_with_updated_adapters(
        self,
        name: str,
        race: UpdatedRace,
        subrace: UpdatedSubRace | None = None,
        character_class: str = "",
    ) -> tuple[UpdatedCharacter, list[str]]:
        """Создать персонажа с использованием обновленных адаптеров.

        Args:
            name: Имя персонажа
            race: Раса (обновленный адаптер)
            subrace: Подраса (обновленный адаптер)
            character_class: Класс персонажа

        Returns:
            Кортеж из (обновленный персонаж, список ошибок)
        """
        errors = []

        # Валидация имени
        if not name or not name.strip():
            errors.append("Имя персонажа не может быть пустым")

        if errors:
            # Возвращаем пустой персонажа с ошибками
            empty_character = UpdatedCharacter(
                CharacterDTO(name=name or "Безымянный")
            )
            return empty_character, errors

        try:
            # Создаем DTO персонажа
            character_dto = CharacterDTO(
                name=name.strip(),
                race_name=race.name,
                subrace_name=subrace.name if subrace else "",
                character_class=character_class,
                level=1,
                size_name="Средний",
                speed=race.speed,
                languages=race.languages.copy(),
            )

            # Генерируем характеристики
            ability_use_case = AbilityGenerationUseCase()
            ability_scores = ability_use_case.generate_with_race_bonuses(
                race, subrace, method="standard"
            )

            # Валидируем характеристики
            validation_errors = ability_use_case.validate_scores(
                ability_scores
            )
            if validation_errors:
                errors.extend(validation_errors)

            # Устанавливаем характеристики
            character_dto.ability_scores = ability_scores.to_dict()
            character_dto.ability_modifiers = (
                ability_scores.get_all_modifiers()
            )

            # Создаем обновленного персонажа
            character = UpdatedCharacter(character_dto)

            return character, errors

        except Exception as e:
            errors.append(f"Ошибка при создании персонажа: {str(e)}")
            fallback_character = UpdatedCharacter(
                CharacterDTO(name=name.strip())
            )
            return fallback_character, errors

    def _create_ability_scores(
        self, scores: dict[str, int]
    ) -> DomainAbilityScores:
        """Создать объект характеристик из словаря.

        Args:
            scores: Словарь характеристик

        Returns:
            Объект AbilityScores
        """
        defaults = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        }

        # Применяем значения по умолчанию
        for ability, default_value in defaults.items():
            if ability not in scores:
                scores[ability] = default_value

        return DomainAbilityScores(
            strength=scores["strength"],
            dexterity=scores["dexterity"],
            constitution=scores["constitution"],
            intelligence=scores["intelligence"],
            wisdom=scores["wisdom"],
            charisma=scores["charisma"],
        )

    def _validate_ability_scores(
        self, ability_scores: DomainAbilityScores
    ) -> list[ValidationErrorDTO]:
        """Валидировать характеристики.

        Args:
            ability_scores: Объект характеристик

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Проверка диапазонов
        abilities = {
            "strength": ability_scores.strength,
            "dexterity": ability_scores.dexterity,
            "constitution": ability_scores.constitution,
            "intelligence": ability_scores.intelligence,
            "wisdom": ability_scores.wisdom,
            "charisma": ability_scores.charisma,
        }

        for ability_name, value in abilities.items():
            if not (1 <= value <= 20):
                errors.extend(
                    self._create_error_response(
                        ability_name,
                        f"Характеристика должна быть в диапазоне 1-20, текущее значение: {value}",
                    )
                )

        # Проверка суммы баллов (для балансировки)
        total_points = sum(abilities.values())
        if (
            total_points < 60
        ):  # Минимальная сумма для сбалансированного персонажа
            errors.extend(
                self._create_error_response(
                    "ability_scores",
                    f"Слишком низкая сумма характеристик: {total_points} (минимум 60)",
                )
            )

        if total_points > 20 * 6:  # Максимум 20 для каждой из 6 характеристик
            errors.extend(
                self._create_error_response(
                    "ability_scores",
                    f"Слишком высокая сумма характеристик: {total_points}",
                )
            )

        return errors

    def _create_error_response(
        self, field: str, message: str, error_type: str = "error"
    ) -> list[ValidationErrorDTO]:
        """Создать DTO ошибки валидации.

        Args:
            field: Поле с ошибкой
            message: Сообщение об ошибке

        Returns:
            Список с одним элементом ValidationErrorDTO
        """
        return [ValidationErrorDTO(field=field, message=message)]


class ValidateCharacterUseCase(BaseUseCase):
    """Use Case для валидации персонажа."""

    def execute(self, character_dto: CharacterDTO) -> list[ValidationErrorDTO]:
        """Валидировать персонажа.

        Args:
            character_dto: DTO персонажа

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Валидация имени
        if not character_dto.name or not character_dto.name.strip():
            errors.extend(
                self._create_error_response(
                    "name", "Имя персонажа не может быть пустым"
                )
            )

        # Валидация уровня
        if character_dto.level < 1 or character_dto.level > 20:
            errors.extend(
                self._create_error_response(
                    "level", "Уровень персонажа должен быть в диапазоне 1-20"
                )
            )

        # Валидация характеристик
        if character_dto.ability_scores:
            for (
                ability_name,
                score_info,
            ) in character_dto.ability_scores.items():
                if isinstance(score_info, dict):
                    value = score_info.get("value", 10)
                else:
                    value = score_info

                if not isinstance(value, int) or value < 1 or value > 20:
                    errors.extend(
                        self._create_error_response(
                            ability_name,
                            f"Характеристика должна быть в диапазоне 1-20, текущее значение: {value}",
                        )
                    )

        return errors

    def _create_error_response(
        self, field: str, message: str, error_type: str = "error"
    ) -> list[ValidationErrorDTO]:
        """Создать DTO ошибки валидации.

        Args:
            field: Поле с ошибкой
            message: Сообщение об ошибке

        Returns:
            Список с одним элементом ValidationErrorDTO
        """
        return [ValidationErrorDTO(field=field, message=message)]
