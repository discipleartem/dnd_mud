"""Адаптер для способностей и характеристик.

Преобразует доменные сущности способностей в формат подходящий для UI.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.domain.value_objects.ability_scores import (
        AbilityScores as DomainAbilityScores,
    )
else:
    from src.domain.value_objects.ability_scores import (
        AbilityScores as DomainAbilityScores,
    )


class Ability:
    """UI адаптер для способности."""

    def __init__(self, domain_ability: Any):
        """Инициализировать адаптер способности.

        Args:
            domain_ability: Доменная способность или заглушка
        """
        self._ability = domain_ability

    def __getattr__(self, name: str) -> Any:
        """Проксировать вызовы к доменной способности."""
        return getattr(self._ability, name)

    def __str__(self) -> str:
        """Строковое представление."""
        return str(self._ability)


class AbilityEnum:
    """UI адаптер для перечисления способностей."""

    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


class AbilityScores:
    """UI адаптер для характеристик персонажа."""

    def __init__(self, domain_ability_scores: DomainAbilityScores):
        """Инициализировать адаптер характеристик.

        Args:
            domain_ability_scores: Доменные характеристики
        """
        self._ability_scores = domain_ability_scores

    def __getattr__(self, name: str) -> Any:
        """Проксировать вызовы к доменным характеристикам."""
        return getattr(self._ability_scores, name)

    def to_dict(self) -> dict:
        """Преобразовать в словарь."""
        if hasattr(self._ability_scores, "to_dict"):
            return self._ability_scores.to_dict()
        return {}

    def get_modifier(self, ability: str) -> int:
        """Получить модификатор характеристики."""
        if hasattr(self._ability_scores, "get_modifier"):
            return self._ability_scores.get_modifier(ability)
        return 0

    def get_all_modifiers(self) -> dict[str, int]:
        """Получить все модификаторы."""
        if hasattr(self._ability_scores, "get_all_modifiers"):
            return self._ability_scores.get_all_modifiers()
        return {}


class PointBuyCosts:
    """UI адаптер для стоимости покупки очков."""

    def __init__(self, domain_costs: Any = None):
        """Инициализировать адаптер стоимости."""
        self._costs = domain_costs or {}

    def __getattr__(self, name: str) -> Any:
        """Проксировать вызовы."""
        return getattr(self._costs, name, None)


class PointBuySystem:
    """UI адаптер для системы покупки очков."""

    def __init__(self, domain_system: Any = None):
        """Инициализировать адаптер системы."""
        self._system = domain_system or {}

    def __getattr__(self, name: str) -> Any:
        """Проксировать вызовы."""
        return getattr(self._system, name, None)


class RandomGeneration:
    """UI адаптер для случайной генерации."""

    def __init__(self, domain_random: Any = None):
        """Инициализировать адаптер случайной генерации."""
        self._random = domain_random or {}

    def __getattr__(self, name: str) -> Any:
        """Проксировать вызовы."""
        return getattr(self._random, name, None)


class StandardArray:
    """UI адаптер для стандартного массива."""

    def __init__(self, domain_array: Any = None):
        """Инициализировать адаптер стандартного массива."""
        self._array = domain_array or {}

    def __getattr__(self, name: str) -> Any:
        """Проксировать вызовы."""
        return getattr(self._array, name, None)


# Псевдонимы для обратной совместимости
AbilityAdapter = Ability
AbilityEnumAdapter = AbilityEnum
AbilityScoresAdapter = AbilityScores
PointBuyCostsAdapter = PointBuyCosts
PointBuySystemAdapter = PointBuySystem
RandomGenerationAdapter = RandomGeneration
StandardArrayAdapter = StandardArray
