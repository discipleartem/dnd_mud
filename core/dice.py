"""Броски кубиков для D&D 5e.

Функции для броска разных кубиков (к4, к6, к8, к10, к12, к20, к100)
с модификаторами, преимуществом/помехой и расчётом модификаторов характеристик.
"""

import random


def roll(count: int = 1, sides: int = 20, modifier: int = 0) -> int:
    """Бросить несколько кубиков и сложить результат с модификатором.

    Пример:
        roll(2, 6, 3)  # 2к6+3 -> (4 + 5) + 3 = 12

    Args:
        count: Сколько кубиков бросить
        sides: Сколько граней у кубика (4, 6, 8, 10, 12, 20, 100)
        modifier: Число, которое прибавляется к сумме

    Returns:
        Итоговая сумма
    """
    total = 0
    for _ in range(count):
        total += random.randint(1, sides)
    return total + modifier


def roll_d20(advantage: bool = False, disadvantage: bool = False) -> int:
    """Бросок к20 с преимуществом или помехой.

    С преимуществом — бросаем дважды, берём лучший.
    С помехой — бросаем дважды, берём худший.

    Args:
        advantage: Бросать с преимуществом
        disadvantage: Бросать с помехой

    Returns:
        Результат от 1 до 20

    Raises:
        ValueError: Если указаны и advantage, и disadvantage одновременно
    """
    if advantage and disadvantage:
        raise ValueError(
            "Нельзя бросать с преимуществом и помехой одновременно"
        )

    if not advantage and not disadvantage:
        return random.randint(1, 20)

    roll1 = random.randint(1, 20)
    roll2 = random.randint(1, 20)

    if advantage:
        return max(roll1, roll2)
    else:
        return min(roll1, roll2)


def roll_with_mods(
    count: int = 1,
    sides: int = 20,
    modifier: int = 0,
    advantage: bool = False,
    disadvantage: bool = False,
) -> tuple[int, list[int]]:
    """Бросок кубиков с подробным результатом.

    Возвращает не только сумму, но и список выпавших значений.
    Это нужно, чтобы показать игроку, что выпало на каждом кубике.

    Args:
        count: Сколько кубиков бросить
        sides: Сколько граней
        modifier: Модификатор
        advantage: Преимущество (дополнительный кубик, берём лучший)
        disadvantage: Помеха (дополнительный кубик, берём худший)

    Returns:
        Кортеж (сумма, список_значений_кубиков)
    """
    # Бросаем основные кубики
    rolls = []
    for _ in range(count):
        rolls.append(random.randint(1, sides))

    # Если преимущество или помеха — бросаем ещё один кубик
    if advantage or disadvantage:
        extra = random.randint(1, sides)
        rolls.append(extra)

        # Сортируем: при преимуществе — по убыванию (лучшие первые),
        # при помехе — по возрастанию (худшие первые)
        rolls.sort(reverse=advantage)

        # Берём только нужное количество (отбрасываем лишний)
        rolls = rolls[:count]

    total = sum(rolls) + modifier
    return total, rolls


def ability_modifier(score: int) -> int:
    """Рассчитать модификатор характеристики.

    Формула: (значение - 10) // 2
    Например: 18 -> +4, 10 -> 0, 6 -> -2

    Args:
        score: Значение характеристики (обычно от 3 до 30)

    Returns:
        Модификатор (от -4 до +10)
    """
    return (score - 10) // 2


def critical_hit(extra_dice: int = 0) -> tuple[int, list[int]]:
    """Симулировать критическое попадание.

    При критическом попадании все кубики урона удваиваются.

    Args:
        extra_dice: Дополнительные кубики урона (например, от класса)

    Returns:
        Кортеж (итоговый_урон, список_значений_кубиков)
    """
    base = random.randint(1, 8)  # Базовый кубик оружия (к8)

    extra = []
    for _ in range(extra_dice):
        extra.append(random.randint(1, 8))

    # Удваиваем: базовый + ещё один за крит, и каждый дополнительный
    all_rolls = [base, base] + extra + extra
    total = sum(all_rolls)
    return total, all_rolls
