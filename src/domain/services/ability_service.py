"""Доменный сервис для работы с характеристиками.

Содержит бизнес-логику связанную с характеристиками D&D.
Следует принципам Domain-Driven Design.
"""

import logging

from src.domain.value_objects.ability_scores import AbilityScores

logger = logging.getLogger(__name__)


class AbilityService:
    """Доменный сервис для работы с характеристиками.

    Содержит бизнес-логику для работы с характеристиками персонажей.
    """

    VALID_ABILITIES = {
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma",
    }

    MIN_SCORE = 1
    MAX_SCORE = 20

    def __init__(self) -> None:
        """Инициализировать сервис."""
        pass

    @staticmethod
    def modifier_formula(score: int) -> int:
        """Вычислить модификатор характеристики.

        Args:
            score: Значение характеристики

        Returns:
            Модификатор характеристики
        """
        return (score - 10) // 2

    @staticmethod
    def validate_ability_scores(scores: dict[str, int | str]) -> list[str]:
        """Валидировать характеристики.

        Args:
            scores: Словарь характеристик

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Проверяем обязательные характеристики
        required_abilities = AbilityService.VALID_ABILITIES
        missing_abilities = required_abilities - set(scores.keys())
        if missing_abilities:
            errors.append(
                f"Отсутствуют характеристики: {', '.join(missing_abilities)}"
            )

        # Проверяем значения характеристик
        for ability, value in scores.items():
            # Проверка названия характеристики
            if ability not in AbilityService.VALID_ABILITIES:
                errors.append(f"Неизвестная характеристика: {ability}")
                continue

            # Проверка типа значения
            if not isinstance(value, int):
                errors.append(f"Характеристика {ability} должна быть числом")
                continue

            # Проверка диапазона значения
            if (
                value < AbilityService.MIN_SCORE
                or value > AbilityService.MAX_SCORE
            ):
                errors.append(
                    f"Характеристика {ability} должна быть в диапазоне "
                    f"{AbilityService.MIN_SCORE}-{AbilityService.MAX_SCORE}, "
                    f"получено: {value}"
                )

        return errors

    @staticmethod
    def calculate_modifier(score: int) -> int:
        """Рассчитать модификатор характеристики.

        Args:
            score: Значение характеристики

        Returns:
            Модификатор характеристики
        """
        return AbilityService.modifier_formula(score)

    @staticmethod
    def calculate_all_modifiers(scores: AbilityScores) -> dict[str, int]:
        """Рассчитать все модификаторы характеристик.

        Args:
            scores: Характеристики персонажа

        Returns:
            Словарь модификаторов
        """
        return {
            "strength": AbilityService.calculate_modifier(scores.strength),
            "dexterity": AbilityService.calculate_modifier(scores.dexterity),
            "constitution": AbilityService.calculate_modifier(
                scores.constitution
            ),
            "intelligence": AbilityService.calculate_modifier(
                scores.intelligence
            ),
            "wisdom": AbilityService.calculate_modifier(scores.wisdom),
            "charisma": AbilityService.calculate_modifier(scores.charisma),
        }

    @staticmethod
    def apply_race_bonuses(
        scores: AbilityScores, bonuses: dict[str, int]
    ) -> AbilityScores:
        """Применить бонусы от расы к характеристикам.

        Args:
            scores: Исходные характеристики
            bonuses: Бонусы от расы

        Returns:
            Характеристики с примененными бонусами
        """
        current_scores = {
            "strength": scores.strength,
            "dexterity": scores.dexterity,
            "constitution": scores.constitution,
            "intelligence": scores.intelligence,
            "wisdom": scores.wisdom,
            "charisma": scores.charisma,
        }

        # Применяем бонусы
        for ability, bonus in bonuses.items():
            if ability in current_scores:
                current_scores[ability] += bonus

        return AbilityScores.from_dict(current_scores)

    @staticmethod
    def calculate_point_buy_cost(scores: AbilityScores) -> int:
        """Рассчитать стоимость характеристик в системе point buy.

        Args:
            scores: Характеристики

        Returns:
            Стоимость в очках
        """
        # Таблица стоимостей D&D 5e Point Buy
        cost_table = {
            8: 0,
            9: 1,
            10: 2,
            11: 3,
            12: 4,
            13: 5,
            14: 7,
            15: 9,
            16: 12,
            17: 15,
            18: 19,
            19: 24,
            20: 30,
        }

        total_cost = 0
        abilities = [
            scores.strength,
            scores.dexterity,
            scores.constitution,
            scores.intelligence,
            scores.wisdom,
            scores.charisma,
        ]

        for score in abilities:
            if score < 8:
                raise ValueError(
                    f"Характеристика {score} слишком низкая для point buy"
                )
            total_cost += cost_table.get(score, 0)

        return total_cost

    @staticmethod
    def get_standard_array() -> AbilityScores:
        """Получить стандартный массив характеристик.

        Returns:
            Стандартный массив D&D 5e
        """
        return AbilityScores(
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
        )

    @staticmethod
    def roll_ability_scores(method: str = "standard") -> AbilityScores:
        """Сгенерировать характеристики случайным образом.

        Args:
            method: Метод генерации (standard, heroic, etc.)

        Returns:
            Сгенерированные характеристики
        """
        import random

        if method == "standard":
            # 4d6, отбрасываем самый низкий
            scores = {}
            for ability in AbilityService.VALID_ABILITIES:
                rolls = [random.randint(1, 6) for _ in range(4)]
                rolls.sort()
                scores[ability] = sum(rolls[1:])  # Отбрасываем самый низкий
        elif method == "heroic":
            # 3d6 + 6
            scores = {}
            for ability in AbilityService.VALID_ABILITIES:
                rolls = [random.randint(1, 6) for _ in range(3)]
                scores[ability] = sum(rolls) + 6
        else:
            raise ValueError(f"Неизвестный метод генерации: {method}")

        return AbilityScores.from_dict(scores)

    @staticmethod
    def get_ability_score_summary(scores: AbilityScores) -> dict[str, str]:
        """Получить сводную информацию о характеристиках.

        Args:
            scores: Характеристики

        Returns:
            Словарь с информацией о характеристиках
        """
        modifiers = AbilityService.calculate_all_modifiers(scores)

        return {
            "strength": f"{scores.strength} ({modifiers['strength']:+d})",
            "dexterity": f"{scores.dexterity} ({modifiers['dexterity']:+d})",
            "constitution": "{} ({:+d})".format(
                scores.constitution, modifiers["constitution"]
            ),
            "intelligence": f"{scores.intelligence} ({modifiers['intelligence']:+d})",
            "wisdom": f"{scores.wisdom} ({modifiers['wisdom']:+d})",
            "charisma": f"{scores.charisma} ({modifiers['charisma']:+d})",
            "total": str(scores.get_total_score()),
            "point_buy_cost": str(
                AbilityService.calculate_point_buy_cost(scores)
            ),
        }

    @staticmethod
    def compare_ability_scores(
        scores1: AbilityScores, scores2: AbilityScores
    ) -> dict[str, str]:
        """Сравнить два набора характеристик.

        Args:
            scores1: Первый набор характеристик
            scores2: Второй набор характеристик

        Returns:
            Словарь с сравнением
        """
        comparison = {}

        for ability in AbilityService.VALID_ABILITIES:
            value1 = getattr(scores1, ability)
            value2 = getattr(scores2, ability)

            if value1 > value2:
                comparison[ability] = f"{value1} > {value2}"
            elif value1 < value2:
                comparison[ability] = f"{value1} < {value2}"
            else:
                comparison[ability] = f"{value1} = {value2}"

        return comparison
