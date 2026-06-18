"""Игровой движок — основной игровой цикл.

Принимает команды от игрока, обрабатывает их (проверки, бой и т.д.),
возвращает текстовые ответы для отображения.
"""

from core.dice import ability_modifier, roll_d20
from core.models import Adventure, Character


def run_game_loop(character: Character, adventure: Adventure) -> None:
    """Запустить основной игровой цикл.

    Пока что это заглушка — просто показывает, что игра началась,
    и ждёт команды "exit" для выхода.

    Args:
        character: Словарь с данными персонажа
        adventure: Словарь с данными приключения
    """
    running = True
    print("Игра запущена! Введите 'help' для списка команд.\n")

    while running:
        command = input("> ").strip().lower()

        if command in ("exit", "quit", "выход"):
            print("Выход из игры...")
            running = False

        elif command in ("help", "помощь"):
            print(_get_help_text())

        elif command in ("stats", "характеристики", "char"):
            print(_get_stats_text(character))

        else:
            print('Команда не распознана. Наберите "help" для списка команд.')


def ability_check(
    character: Character,
    ability: str,
    dc: int = 10,
    advantage: bool = False,
    disadvantage: bool = False,
) -> tuple[bool, int, str]:
    """Проверка характеристики (ability check).

    Бросает к20, добавляет модификатор характеристики,
    сравнивает со сложностью (DC).

    Args:
        character: Словарь с данными персонажа
        ability: Ключ характеристики ('strength', 'dexterity' и т.д.)
        dc: Сложность (DC, по умолчанию 10)
        advantage: Бросать с преимуществом
        disadvantage: Бросать с помехой

    Returns:
        Кортеж (успех, итоговый_результат, описание_броска)
    """
    score = character.stats.get(ability, 10)
    mod = ability_modifier(score)
    roll = roll_d20(advantage=advantage, disadvantage=disadvantage)
    total = roll + mod

    success = total >= dc
    status = "успех" if success else "провал"
    description = (
        f"Бросок {ability}: d20={roll} + {mod} = {total} "
        f"(DC {dc}) — {status}"
    )

    return success, total, description


def _get_help_text() -> str:
    """Собрать текст справки.

    Returns:
        Список доступных команд
    """
    return (
        "Доступные команды:\n"
        "  stats — показать характеристики персонажа\n"
        "  help  — показать эту справку\n"
        "  exit  — выйти из игры"
    )


def _get_stats_text(character: Character) -> str:
    """Собрать текст с характеристиками персонажа.

    Args:
        character: Объект персонажа

    Returns:
        Отформатированные характеристики
    """
    lines = [
        f"Персонаж: {character.name}",
        f"Уровень: {character.level}",
        f"Раса: {character.race}",
        f"Класс: {character.class_name}",
        f"HP: {character.current_hp}",
        "",
        "Характеристики:",
    ]
    for stat_key, value in character.stats.items():
        lines.append(f"  {stat_key}: {value}")
    return "\n".join(lines)
