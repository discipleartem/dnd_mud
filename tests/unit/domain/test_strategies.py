"""Тесты для стратегий доменной логики."""

import pytest

from src.domain.strategies.ability_strategy import (
    AbilityCalculator,
    ScaledAbilityModifierStrategy,
    StandardAbilityModifierStrategy,
    VariantAbilityModifierStrategy,
)


class TestStandardAbilityModifierStrategy:
    """Тесты стандартной стратегии модификаторов."""

    def test_calculate_modifier_normal_range(self) -> None:
        """Тест вычисления модификаторов в нормальном диапазоне."""
        strategy = StandardAbilityModifierStrategy()

        assert strategy.calculate_modifier(10) == 0
        assert strategy.calculate_modifier(11) == 0
        assert strategy.calculate_modifier(12) == 1
        assert strategy.calculate_modifier(8) == -1
        assert strategy.calculate_modifier(20) == 5
        assert strategy.calculate_modifier(1) == -5

    def test_calculate_modifier_invalid_range(self) -> None:
        """Тест вычисления модификаторов за пределами диапазона."""
        strategy = StandardAbilityModifierStrategy()

        with pytest.raises(ValueError, match="Значение характеристики должно быть от 1 до 20"):
            strategy.calculate_modifier(0)

        with pytest.raises(ValueError, match="Значение характеристики должно быть от 1 до 20"):
            strategy.calculate_modifier(21)


class TestVariantAbilityModifierStrategy:
    """Тесты вариантной стратегии модификаторов."""

    def test_calculate_modifier_variant(self) -> None:
        """Тест вычисления модификаторов по вариантной формуле."""
        strategy = VariantAbilityModifierStrategy()

        # Проверяем, что работает так же как стандартная для целых чисел
        assert strategy.calculate_modifier(10) == 0
        assert strategy.calculate_modifier(12) == 1
        assert strategy.calculate_modifier(8) == -1


class TestScaledAbilityModifierStrategy:
    """Тесты масштабируемой стратегии модификаторов."""

    def test_calculate_modifier_standard_range(self) -> None:
        """Тест вычисления модификаторов в стандартном диапазоне."""
        strategy = ScaledAbilityModifierStrategy()

        # До 20 работает как стандартная
        assert strategy.calculate_modifier(10) == 0
        assert strategy.calculate_modifier(20) == 5

    def test_calculate_modifier_scaled_range(self) -> None:
        """Тест вычисления модификаторов в масштабируемом диапазоне."""
        strategy = ScaledAbilityModifierStrategy(max_score=30, scaling_factor=1.5)

        # Выше 20 применяется масштабирование
        assert strategy.calculate_modifier(22) == 8  # 5 + 1.5*2 -> 8
        assert strategy.calculate_modifier(24) == 11  # 5 + 1.5*4 -> 11

    def test_calculate_modifier_invalid_range(self) -> None:
        """Тест вычисления модификаторов за пределами диапазона."""
        strategy = ScaledAbilityModifierStrategy(max_score=30)

        with pytest.raises(ValueError, match="Значение характеристики должно быть от 1 до 30"):
            strategy.calculate_modifier(31)


class TestAbilityCalculator:
    """Тесты калькулятора характеристик."""

    def test_calculator_with_standard_strategy(self) -> None:
        """Тест калькулятора со стандартной стратегией."""
        strategy = StandardAbilityModifierStrategy()
        calculator = AbilityCalculator(strategy)

        assert calculator.calculate_modifier(14) == 2
        assert calculator.calculate_modifier(7) == -2

    def test_calculator_change_strategy(self) -> None:
        """Тест изменения стратегии калькулятора."""
        standard = StandardAbilityModifierStrategy()
        variant = VariantAbilityModifierStrategy()
        calculator = AbilityCalculator(standard)

        assert calculator.calculate_modifier(14) == 2

        calculator.set_strategy(variant)
        assert calculator.calculate_modifier(14) == 2  # Результат тот же

    def test_calculate_all_modifiers(self) -> None:
        """Тест вычисления всех модификаторов."""
        strategy = StandardAbilityModifierStrategy()
        calculator = AbilityCalculator(strategy)

        scores = {
            "strength": 16,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 10,
            "wisdom": 8,
            "charisma": 6,
        }

        modifiers = calculator.calculate_all_modifiers(scores)

        expected = {
            "strength": 3,
            "dexterity": 2,
            "constitution": 1,
            "intelligence": 0,
            "wisdom": -1,
            "charisma": -2,
        }

        assert modifiers == expected
