# src/domain/value_objects/dice.py
"""Кубики D&D."""

import random
from typing import List


class Dice:
    """Класс для работы с кубиками D&D."""

    @staticmethod
    def roll(sides: int) -> int:
        """Бросает кубик с указанным количеством граней."""
        return random.randint(1, sides)

    @staticmethod
    def roll_multiple(sides: int, count: int) -> List[int]:
        """Бросает несколько кубиков."""
        return [Dice.roll(sides) for _ in range(count)]

    @staticmethod
    def roll_d20() -> int:
        """Бросает d20."""
        return Dice.roll(20)

    @staticmethod
    def roll_d6() -> int:
        """Бросает d6."""
        return Dice.roll(6)

    @staticmethod
    def roll_d4() -> int:
        """Бросает d4."""
        return Dice.roll(4)

    @staticmethod
    def roll_d8() -> int:
        """Бросает d8."""
        return Dice.roll(8)

    @staticmethod
    def roll_d10() -> int:
        """Бросает d10."""
        return Dice.roll(10)

    @staticmethod
    def roll_d12() -> int:
        """Бросает d12."""
        return Dice.roll(12)

    @staticmethod
    def roll_with_advantage(sides: int = 20) -> tuple[int, bool]:
        """Бросает кубик с преимуществом.

        Returns:
            (результат, было_ли_преимущество)
        """
        roll1 = Dice.roll(sides)
        roll2 = Dice.roll(sides)
        result = max(roll1, roll2)
        return result, roll1 != roll2

    @staticmethod
    def roll_with_disadvantage(sides: int = 20) -> tuple[int, bool]:
        """Бросает кубик с помехой.

        Returns:
            (результат, была_ли_помеха)
        """
        roll1 = Dice.roll(sides)
        roll2 = Dice.roll(sides)
        result = min(roll1, roll2)
        return result, roll1 != roll2

    @staticmethod
    def parse_dice_string(dice_str: str) -> tuple[int, int]:
        """Парсит строку типа '2d6' в (количество, грани).

        Args:
            dice_str: Строка в формате 'XdY'

        Returns:
            Кортеж (количество_кубиков, количество_граней)
        """
        if "d" not in dice_str.lower():
            raise ValueError(f"Неверный формат кубика: {dice_str}")

        parts = dice_str.lower().split("d")
        if len(parts) != 2:
            raise ValueError(f"Неверный формат кубика: {dice_str}")

        try:
            count = int(parts[0]) if parts[0] else 1
            sides = int(parts[1])
            return count, sides
        except ValueError:
            raise ValueError(f"Неверный формат кубика: {dice_str}")

    @staticmethod
    def roll_d20_with_advantage(advantage: str = "none") -> tuple[int, bool, bool]:
        """Бросает d20 с преимуществом/помехой.

        Args:
            advantage: Тип преимущества ("none", "advantage", "disadvantage")

        Returns:
            Кортеж (значение, крит_успех, крит_провал)
        """
        if advantage == "advantage":
            value, _ = Dice.roll_with_advantage(20)
        elif advantage == "disadvantage":
            value, _ = Dice.roll_with_disadvantage(20)
        else:
            value = Dice.roll_d20()

        crit_success = value == 20
        crit_fail = value == 1
        return value, crit_success, crit_fail

    @staticmethod
    def roll_dice_string(dice_str: str) -> int:
        """Бросает кубики по строке типа '2d6+3'.

        Args:
            dice_str: Строка в формате 'XdY[+Z]'

        Returns:
            Сумма бросков с модификатором
        """
        # Парсим модификатор
        modifier = 0
        if "+" in dice_str:
            dice_part, mod_part = dice_str.split("+")
            modifier = int(mod_part.strip())
            dice_str = dice_part.strip()
        elif "-" in dice_str:
            dice_part, mod_part = dice_str.split("-")
            modifier = -int(mod_part.strip())
            dice_str = dice_part.strip()

        # Бросаем кубики
        count, sides = Dice.parse_dice_string(dice_str)
        rolls = Dice.roll_multiple(sides, count)

        return sum(rolls) + modifier
