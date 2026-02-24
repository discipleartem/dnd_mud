"""Value Object для характеристик персонажа D&D.

Представляет шесть основных характеристик с валидацией и операциями.
Следует принципу неизменяемости Value Objects.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AbilityScores:
    """Характеристики персонажа D&D.

    Value Object - неизменяемый набор шести характеристик.
    """

    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    def __post_init__(self) -> None:
        """Валидация значений характеристик."""
        abilities = {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
        }

        for name, value in abilities.items():
            if not 1 <= value <= 20:
                raise ValueError(
                    f"Характеристика {name} должна быть в диапазоне 1-20, получено: {value}"
                )

    @classmethod
    def from_dict(cls, scores: dict[str, int]) -> "AbilityScores":
        """Создать характеристики из словаря.

        Args:
            scores: Словарь с характеристиками

        Returns:
            Объект AbilityScores

        Raises:
            ValueError: Если в словаре неизвестные характеристики
        """
        valid_abilities = {
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        }

        unknown = set(scores.keys()) - valid_abilities
        if unknown:
            raise ValueError(f"Неизвестные характеристики: {unknown}")

        # Устанавливаем значения по умолчанию для отсутствующих характеристик
        defaults = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        }

        final_scores = defaults.copy()
        final_scores.update(scores)

        return cls(**final_scores)

    def get_modifier(self, ability: str) -> int:
        """Получить модификатор характеристики.

        Args:
            ability: Название характеристики

        Returns:
            Модификатор характеристики

        Raises:
            ValueError: Если неизвестная характеристика
        """
        if not hasattr(self, ability):
            raise ValueError(f"Неизвестная характеристика: {ability}")

        value = getattr(self, ability)
        if not isinstance(value, int):
            raise ValueError(
                f"Значение характеристики должно быть целым числом: {ability}"
            )
        return (value - 10) // 2

    def get_all_modifiers(self) -> dict[str, int]:
        """Получить все модификаторы характеристик.

        Returns:
            Словарь модификаторов
        """
        return {
            "strength": self.get_modifier("strength"),
            "dexterity": self.get_modifier("dexterity"),
            "constitution": self.get_modifier("constitution"),
            "intelligence": self.get_modifier("intelligence"),
            "wisdom": self.get_modifier("wisdom"),
            "charisma": self.get_modifier("charisma"),
        }

    def apply_bonuses(self, bonuses: dict[str, int]) -> "AbilityScores":
        """Применить бонусы к характеристикам.

        Args:
            bonuses: Словарь бонусов к характеристикам

        Returns:
            Новые характеристики с применёнными бонусами
        """
        current_scores = {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
        }

        # Применяем бонусы
        for ability, bonus in bonuses.items():
            if ability in current_scores:
                current_scores[ability] += bonus

        return self.from_dict(current_scores)

    def get_total_score(self) -> int:
        """Получить сумму всех характеристик.

        Returns:
            Сумма всех характеристик
        """
        return (
            self.strength
            + self.dexterity
            + self.constitution
            + self.intelligence
            + self.wisdom
            + self.charisma
        )

    def get_point_buy_cost(self) -> int:
        """Получить стоимость характеристик в системе point buy.

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
            self.strength,
            self.dexterity,
            self.constitution,
            self.intelligence,
            self.wisdom,
            self.charisma,
        ]

        for score in abilities:
            if score < 8:
                raise ValueError(
                    f"Характеристика {score} слишком низкая для point buy"
                )
            total_cost += cost_table.get(score, 0)

        return total_cost

    def to_dict(self) -> dict[str, int]:
        """Преобразовать в словарь.

        Returns:
            Словарь характеристик
        """
        return {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
        }

    def __str__(self) -> str:
        """Строковое представление."""
        modifiers = self.get_all_modifiers()
        parts = []

        for ability in [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]:
            value = getattr(self, ability)
            mod = modifiers[ability]
            mod_str = f"+{mod}" if mod >= 0 else str(mod)
            parts.append(f"{ability[:3].upper()}: {value} ({mod_str})")

        return ", ".join(parts)

    def __repr__(self) -> str:
        """Детальное строковое представление."""
        return (
            f"AbilityScores(strength={self.strength}, dexterity={self.dexterity}, "
            f"constitution={self.constitution}, intelligence={self.intelligence}, "
            f"wisdom={self.wisdom}, charisma={self.charisma})"
        )
