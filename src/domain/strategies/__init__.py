"""Стратегии доменной логики.

Содержит реализации паттерна Strategy для различных алгоритмов.
"""

from .ability_strategy import (
    AbilityCalculator,
    ScaledAbilityModifierStrategy,
    StandardAbilityModifierStrategy,
    VariantAbilityModifierStrategy,
)

__all__ = [
    "AbilityCalculator",
    "StandardAbilityModifierStrategy",
    "VariantAbilityModifierStrategy",
    "ScaledAbilityModifierStrategy",
]
