"""Стратегии для работы с характеристиками.

Реализует паттерн Strategy для различных правил вычисления модификаторов.
Следует принципам Domain-Driven Design и Clean Architecture.
"""

from typing import Protocol


class AbilityModifierStrategy(Protocol):
    """Протокол стратегии вычисления модификаторов характеристик."""

    def calculate_modifier(self, score: int) -> int:
        """Вычислить модификатор характеристики.

        Args:
            score: Значение характеристики

        Returns:
            Модификатор характеристики
        """
        ...


class StandardAbilityModifierStrategy:
    """Стандартная стратегия вычисления модификаторов D&D 5e.

    Использует формулу: (score - 10) // 2
    """

    def calculate_modifier(self, score: int) -> int:
        """Вычислить модификатор по стандартной формуле.

        Args:
            score: Значение характеристики (1-20)

        Returns:
            Модификатор характеристики (-5 до +5)
        """
        if score < 1 or score > 20:
            raise ValueError(
                f"Значение характеристики должно быть от 1 до 20: {score}"
            )

        return (score - 10) // 2


class VariantAbilityModifierStrategy:
    """Вариантная стратегия с измененными правилами.

    Использует формулу: floor((score - 10) / 2)
    """

    def calculate_modifier(self, score: int) -> int:
        """Вычислить модификатор по вариантной формуле.

        Args:
            score: Значение характеристики

        Returns:
            Модификатор характеристики
        """
        if score < 1 or score > 20:
            raise ValueError(
                f"Значение характеристики должно быть от 1 до 20: {score}"
            )

        # Используем floor для более консервативных модификаторов
        import math

        return math.floor((score - 10) / 2)


class ScaledAbilityModifierStrategy:
    """Масштабируемая стратегия для высоких уровней.

    Применяет масштабирование для значений выше 20.
    """

    def __init__(self, max_score: int = 30, scaling_factor: float = 1.5):
        """Инициализировать стратегию масштабирования.

        Args:
            max_score: Максимальное значение характеристики
            scaling_factor: Коэффициент масштабирования
        """
        self.max_score = max_score
        self.scaling_factor = scaling_factor
        self._standard = StandardAbilityModifierStrategy()

    def calculate_modifier(self, score: int) -> int:
        """Вычислить модификатор с масштабированием.

        Args:
            score: Значение характеристики

        Returns:
            Модификатор характеристики
        """
        if score < 1 or score > self.max_score:
            raise ValueError(
                f"Значение характеристики должно быть от 1 до {self.max_score}: {score}"
            )

        if score <= 20:
            return self._standard.calculate_modifier(score)

        # Масштабирование для высоких значений
        base_modifier = self._standard.calculate_modifier(20)
        additional_points = score - 20
        scaled_bonus = int(additional_points * self.scaling_factor)

        return base_modifier + scaled_bonus


class AbilityCalculator:
    """Калькулятор характеристик с использованием стратегий.

    Контекст в паттерне Strategy, который использует различные стратегии
    для вычисления модификаторов.
    """

    def __init__(self, strategy: AbilityModifierStrategy):
        """Инициализировать калькулятор со стратегией.

        Args:
            strategy: Стратегия вычисления модификаторов
        """
        self._strategy = strategy

    def set_strategy(self, strategy: AbilityModifierStrategy) -> None:
        """Установить новую стратегию.

        Args:
            strategy: Новая стратегия вычисления
        """
        self._strategy = strategy

    def calculate_modifier(self, score: int) -> int:
        """Вычислить модификатор используя текущую стратегию.

        Args:
            score: Значение характеристики

        Returns:
            Модификатор характеристики
        """
        return self._strategy.calculate_modifier(score)

    def calculate_all_modifiers(
        self, scores: dict[str, int]
    ) -> dict[str, int]:
        """Вычислить модификаторы для всех характеристик.

        Args:
            scores: Словарь значений характеристик

        Returns:
            Словарь модификаторов характеристик
        """
        modifiers = {}
        for ability, score in scores.items():
            modifiers[ability] = self.calculate_modifier(score)

        return modifiers
