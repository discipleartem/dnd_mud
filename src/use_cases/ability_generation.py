"""Use Case для генерации характеристик персонажа.

Следует принципам Clean Architecture - изолирует бизнес-логику
от инфраструктуры и UI.
"""

from src.ui.adapters.updated_adapters import Race as UpdatedRace
from src.ui.adapters.updated_adapters import SubRace as UpdatedSubRace
from src.ui.dto.character_dto import AbilityScoreDTO


class AbilityGenerationUseCase:
    """Use Case для генерации характеристик персонажа."""

    def __init__(self) -> None:
        """Инициализировать Use Case."""
        pass

    def generate_basic_scores(self) -> AbilityScoreDTO:
        """Сгенерировать базовые характеристики.

        Returns:
            DTO с базовыми характеристиками (10 во всем)
        """
        return AbilityScoreDTO(
            strength=10,
            dexterity=10,
            constitution=10,
            intelligence=10,
            wisdom=10,
            charisma=10,
        )

    def generate_standard_array(self) -> AbilityScoreDTO:
        """Сгенерировать характеристики по стандартному массиву.

        Returns:
            DTO с характеристиками из стандартного массива D&D 5e
        """
        # Стандартный массив: 15, 14, 13, 12, 10, 8
        standard_values = [15, 14, 13, 12, 10, 8]

        return AbilityScoreDTO(
            strength=standard_values[0],
            dexterity=standard_values[1],
            constitution=standard_values[2],
            intelligence=standard_values[3],
            wisdom=standard_values[4],
            charisma=standard_values[5],
        )

    def apply_racial_bonuses(
        self,
        base_scores: AbilityScoreDTO,
        race: UpdatedRace,
        subrace: UpdatedSubRace | None = None,
    ) -> AbilityScoreDTO:
        """Применить расовые бонусы к характеристикам.

        Args:
            base_scores: Базовые характеристики
            race: Раса персонажа
            subrace: Подраса (опционально)

        Returns:
            DTO с примененными бонусами
        """
        # Создаем копию базовых характеристик
        scores = AbilityScoreDTO(
            strength=base_scores.strength,
            dexterity=base_scores.dexterity,
            constitution=base_scores.constitution,
            intelligence=base_scores.intelligence,
            wisdom=base_scores.wisdom,
            charisma=base_scores.charisma,
        )

        # Применяем бонусы расы
        if race.ability_bonuses:
            for ability, bonus in race.ability_bonuses.items():
                if hasattr(scores, ability):
                    current_value = getattr(scores, ability)
                    setattr(scores, ability, current_value + bonus)

        # Применяем бонусы подрасы
        if subrace and subrace.ability_bonuses:
            for ability, bonus in subrace.ability_bonuses.items():
                if hasattr(scores, ability):
                    current_value = getattr(scores, ability)
                    setattr(scores, ability, current_value + bonus)

        return scores

    def generate_with_race_bonuses(
        self,
        race: UpdatedRace,
        subrace: UpdatedSubRace | None = None,
        method: str = "standard",
    ) -> AbilityScoreDTO:
        """Сгенерировать характеристики с учетом расовых бонусов.

        Args:
            race: Раса персонажа
            subrace: Подраса (опционально)
            method: Метод генерации ("basic", "standard", "random")

        Returns:
            DTO с готовыми характеристиками
        """
        # Генерируем базовые характеристики
        if method == "basic":
            base_scores = self.generate_basic_scores()
        elif method == "standard":
            base_scores = self.generate_standard_array()
        else:
            # Для случайной генерации пока используем стандартный массив
            base_scores = self.generate_standard_array()

        # Применяем расовые бонусы
        final_scores = self.apply_racial_bonuses(base_scores, race, subrace)

        return final_scores

    def validate_scores(self, scores: AbilityScoreDTO) -> list[str]:
        """Валидировать характеристики.

        Args:
            scores: Характеристики для валидации

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Проверяем диапазоны значений
        for ability in [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]:
            value = getattr(scores, ability)
            if not (1 <= value <= 20):
                errors.append(
                    f"{ability.capitalize()} должно быть в диапазоне 1-20, получено {value}"
                )

        # Проверяем сумму характеристик (для балансировки)
        total = sum(
            [
                scores.strength,
                scores.dexterity,
                scores.constitution,
                scores.intelligence,
                scores.wisdom,
                scores.charisma,
            ]
        )

        if total < 60:  # Минимальная сумма для сбалансированного персонажа
            errors.append(
                f"Сумма характеристик слишком низка: {total} (минимум 60)"
            )

        if total > 90:  # Максимальная сумма для балансировки
            errors.append(
                f"Сумма характеристик слишком высока: {total} (максимум 90)"
            )

        return errors
