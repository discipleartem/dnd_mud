"""Модуль генерации характеристик персонажа."""

from typing import Any

from i18n import t
from src.domain.entities.race import SubRace as DomainSubRace
from src.ui.adapters.ability_adapter import (
    Ability,
    AbilityEnum,
    AbilityScores,
    PointBuySystem,
)
from src.ui.adapters.character_adapter import Race, SubRace


def display_ability_generation_methods() -> None:
    """Отобразить методы генерации характеристик."""
    print(f"\n{t('ability_generation.title')}")
    print("=" * 50)
    print(f"1. 📊 {t('ability_generation.methods.standard')}")
    print(f"2. 💰 {t('ability_generation.methods.point_buy')}")
    print(f"3. 🎲 {t('ability_generation.methods.random')}")
    print()


def select_ability_generation_method() -> str:
    """Выбрать метод генерации характеристик."""
    while True:
        try:
            choice = input(t("ability_generation.prompt")).strip()
            if choice in ["1", "2", "3"]:
                methods = {"1": "standard", "2": "point_buy", "3": "random"}
                return methods[choice]
            else:
                print(t("ability_generation.error_invalid"))
        except ValueError:
            print(t("ability_generation.error_invalid"))


def display_racial_bonuses(race: Race, subrace: SubRace | None = None) -> None:
    """Отобразить бонусы к характеристикам от расы/подрасы."""
    print(f"\n{t('ability_generation.racial_bonuses.title')}")
    print("-" * 40)

    # Получаем доменные объекты из адаптеров
    domain_race = race._race if hasattr(race, "_race") else race
    domain_subrace = (
        subrace._subrace
        if subrace and hasattr(subrace, "_subrace")
        else subrace
    )

    # Проверяем типы и вызываем методы
    if hasattr(domain_race, "get_effective_ability_bonuses"):
        # Передаем только доменные объекты
        subrace_arg = (
            domain_subrace
            if isinstance(domain_subrace, DomainSubRace)
            else None
        )
        effective_bonuses = domain_race.get_effective_ability_bonuses(
            subrace_arg
        )
    else:
        effective_bonuses = {}

    # Показываем бонусы базовой расы (только если они применяются)
    if (
        domain_subrace
        and hasattr(domain_subrace, "inherit_base_abilities")
        and domain_subrace.inherit_base_abilities
        and hasattr(domain_race, "ability_bonuses")
    ):
        print(f"🏛️ {race.name}:")
        for ability_name, bonus in domain_race.ability_bonuses.items():
            try:
                ability = Ability(ability_name)
                print(f"   {ability.get_localized_name()}: +{bonus}")
            except ValueError:
                continue

    # Показываем бонусы подрасы
    if (
        domain_subrace
        and hasattr(domain_subrace, "ability_bonuses")
        and domain_subrace.ability_bonuses
    ):
        print(f"🌟 {subrace.name if subrace else 'Unknown'}:")
        for ability_name, bonus in domain_subrace.ability_bonuses.items():
            try:
                ability = Ability(ability_name)
                print(f"   {ability.get_localized_name()}: +{bonus}")
            except ValueError:
                continue
    elif (
        domain_subrace
        and hasattr(domain_subrace, "inherit_base_abilities")
        and not domain_subrace.inherit_base_abilities
    ):
        # Особый случай для подрас с переопределенными бонусами
        print(f"🌟 {subrace.name if subrace else 'Unknown'}:")
        print(
            "   {}".format(
                getattr(domain_subrace, "ability_bonuses_description", "")
            )
        )

    if not effective_bonuses:
        print(t("ability_generation.racial_bonuses.none"))

    print()


def display_abilities_with_bonuses(ability_scores: AbilityScores) -> None:
    """Отобразить характеристики с бонусами."""
    print(f"\n{t('ability_generation.current_scores.title')}")
    print("-" * 60)
    print(
        f"{'Характеристика':<15} {'Базовое':<10} {'Бонус':<10} "
        f"{'Итого':<10} {'Модификатор':<12}"
    )
    print("-" * 60)

    for ability in [
        Ability(AbilityEnum.STRENGTH),
        Ability(AbilityEnum.DEXTERITY),
        Ability(AbilityEnum.CONSTITUTION),
        Ability(AbilityEnum.INTELLIGENCE),
        Ability(AbilityEnum.WISDOM),
        Ability(AbilityEnum.CHARISMA),
    ]:
        base = ability_scores.base_scores.get(ability._ability, 10)
        bonus = ability_scores.racial_bonuses.get(ability._ability, 0)
        total = ability_scores.get_total_score(ability._ability)
        modifier = ability_scores.get_modifier(ability._ability)

        modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        bonus_str = f"+{bonus}" if bonus > 0 else "0"

        print(
            f"{ability.get_localized_name():<15} {base:<10} "
            f"{bonus_str:<10} {total:<10} {modifier_str:<12}"
        )

    print()


def generate_standard_array(ability_scores: AbilityScores) -> None:
    """Генерация характеристик стандартным массивом."""
    values = [15, 14, 13, 12, 10, 8]
    abilities = [
        AbilityEnum.STRENGTH,
        AbilityEnum.DEXTERITY,
        AbilityEnum.CONSTITUTION,
        AbilityEnum.INTELLIGENCE,
        AbilityEnum.WISDOM,
        AbilityEnum.CHARISMA,
    ]

    print(f"\n{t('ability_generation.standard.title')}")
    print("=" * 40)
    print(f"{t('ability_generation.standard.description')}")
    print(
        f"📊 {t('ability_generation.standard.values')}: "
        f"{', '.join(map(str, values))}"
    )
    print()

    # Отображаем доступные значения
    print(f"{t('ability_generation.standard.available_values')}:")
    for i, value in enumerate(values, 1):
        print(f"{i}. {value}")

    # Распределяем значения
    assigned_values: dict[Any, Any] = {}
    remaining_values = values.copy()

    for ability in abilities:
        ability_obj = Ability(ability)
        while True:
            print(
                "\n{}".format(
                    t(
                        "ability_generation.standard.assign_prompt",
                        ability=ability_obj.get_localized_name(),
                    )
                )
            )
            print(
                "{}: {}".format(
                    t("ability_generation.standard.remaining_values"),
                    ", ".join(map(str, remaining_values)),
                )
            )

            try:
                choice = input("Выберите значение: ").strip()

                # Только ввод значения
                try:
                    value = int(choice)
                    if value in remaining_values:
                        remaining_values.remove(value)
                        assigned_values[ability] = value
                        ability_scores.set_base_score(ability_obj, value)
                        print(
                            f"✅ {ability_obj.get_localized_name()}: {value}"
                        )
                        break
                    else:
                        print(
                            f"❌ Значение {value} отсутствует в "
                            f"списке доступных"
                        )
                except ValueError:
                    print(t("ability_generation.error_invalid"))
            except ValueError:
                print(t("ability_generation.error_invalid"))


def _display_point_buy_info(point_buy: PointBuySystem) -> dict[int, int]:
    """Отобразить информацию о системе покупки очков.

    Returns:
        Словарь стоимостей
    """
    valid_values = list(range(8, 16))  # 8-15 допустимые значения
    cost_table = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}

    print(f"\n{t('ability_generation.point_buy.title')}")
    print("=" * 40)
    print(f"{t('ability_generation.point_buy.description')}")
    print(
        "💰 {}: {}".format(
            t("ability_generation.point_buy.total_points"),
            point_buy.POINTS_TOTAL,
        )
    )
    print()

    # Отображаем таблицу стоимостей
    print(f"{t('ability_generation.point_buy.cost_table')}:")
    print(f"{'Значение':<10} {'Стоимость':<10}")
    print("-" * 20)
    for value in valid_values:
        cost = cost_table.get(value, 0)
        print(f"{value:<10} {cost:<10}")
    print()

    return cost_table


def _initialize_ability_scores(ability_scores: AbilityScores) -> None:
    """Инициализировать характеристики минимальными значениями."""
    abilities = [
        AbilityEnum.STRENGTH,
        AbilityEnum.DEXTERITY,
        AbilityEnum.CONSTITUTION,
        AbilityEnum.INTELLIGENCE,
        AbilityEnum.WISDOM,
        AbilityEnum.CHARISMA,
    ]

    for ability in abilities:
        ability_scores.set_base_score(Ability(ability), 1)


def _calculate_remaining_points(
    assigned_values: dict, cost_table: dict[int, int], abilities: list
) -> int:
    """Рассчитать оставшиеся очки."""
    total_points = 27
    spent_points = sum(
        cost_table.get(assigned_values[a], 0)
        for a in abilities
        if assigned_values.get(a, 1) != 1
    )
    return total_points - spent_points


def _set_minimum_values(
    ability_scores: AbilityScores, assigned_values: dict, abilities: list
) -> None:
    """Установить минимальные значения для нераспределенных характеристик."""
    for ability in abilities:
        if assigned_values.get(ability, 1) == 1:
            ability_scores.set_base_score(Ability(ability), 8)
            print(f"⚡ {Ability(ability).get_localized_name()}: 8 (минимум)")


def _check_can_confirm(
    assigned_values: dict, remaining_points: int, abilities: list
) -> tuple[bool, list]:
    """Проверить можно ли подтвердить выбор.

    Returns:
        (можно подтвердить, нераспределенные характеристики)
    """
    unassigned_abilities = [
        a for a in abilities if assigned_values.get(a, 1) == 1
    ]
    can_confirm = len(unassigned_abilities) == 0 and remaining_points == 0
    return can_confirm, unassigned_abilities


def _show_confirmation_errors(
    unassigned_abilities: list, remaining_points: int, abilities: list
) -> None:
    """Показать ошибки подтверждения."""
    if unassigned_abilities:
        print("\n❌ Сначала распределите все характеристики!")
        unassigned_names = [
            Ability(a).get_localized_name() for a in unassigned_abilities
        ]
        print("Не распределены: {}".format(", ".join(unassigned_names)))

    if remaining_points > 0:
        print(f"\n❌ Осталось нераспределенных очков: {remaining_points}")
        print("Распределите все очки перед подтверждением")


def _handle_user_confirmation(can_confirm: bool) -> str:
    """Обработать подтверждение пользователя."""
    if not can_confirm:
        choice = input(
            "\n1. ✅ Подтвердить выбор\n"
            "2. 🔄 Перераспределить очки\n"
            "Выберите действие: "
        ).strip()
    else:
        choice = input(
            "\n1. ✅ Подтвердить выбор\nВыберите действие: "
        ).strip()

    return choice


def _process_confirmation_choice(choice: str, can_confirm: bool) -> bool:
    """Обработать выбор подтверждения.

    Returns:
        True если нужно завершить, False если перераспределить
    """
    if choice == "1":
        if can_confirm:
            print("✅ Выбор подтвержден!")
            return True
        else:
            print(
                "❌ Невозможно подтвердить выбор! "
                "Сначала распределите все характеристики "
                "и потратьте все очки."
            )
    elif choice == "2":
        print("🔄 Возврат к распределению очков...")
        return False

    return False


def generate_point_buy(ability_scores: AbilityScores) -> None:
    """Генерация характеристик покупкой очков."""
    point_buy = PointBuySystem()

    # Отображаем информацию и получаем таблицу стоимостей
    cost_table = _display_point_buy_info(point_buy)

    # Инициализируем характеристики
    _initialize_ability_scores(ability_scores)

    # Распределяем характеристики
    abilities = [
        AbilityEnum.STRENGTH,
        AbilityEnum.DEXTERITY,
        AbilityEnum.CONSTITUTION,
        AbilityEnum.INTELLIGENCE,
        AbilityEnum.WISDOM,
        AbilityEnum.CHARISMA,
    ]

    assigned_values: dict[Any, Any] = {}
    valid_values = list(range(8, 16))

    for ability_enum in abilities:
        _distribute_single_ability(
            Ability(ability_enum),
            ability_scores,
            assigned_values,
            27,  # Будет обновлено ниже
            valid_values,
            cost_table,
        )
        # Обновляем оставшиеся очки
        remaining_points = _calculate_remaining_points(
            assigned_values, cost_table, abilities
        )

    # Устанавливаем минимальные значения
    _set_minimum_values(ability_scores, assigned_values, abilities)

    # Финальное подтверждение
    print(f"\n{t('ability_generation.final.confirmation')}")
    print("=" * 40)
    display_abilities_with_bonuses(ability_scores)

    remaining_points = _calculate_remaining_points(
        assigned_values, cost_table, abilities
    )
    print(
        "💰 {}: {}".format(
            t("ability_generation.point_buy.remaining_points"),
            remaining_points,
        )
    )

    # Проверяем можно ли подтвердить
    can_confirm, unassigned_abilities = _check_can_confirm(
        assigned_values, remaining_points, abilities
    )

    if not can_confirm:
        _show_confirmation_errors(
            unassigned_abilities, remaining_points, abilities
        )

    # Цикл подтверждения
    while True:
        choice = _handle_user_confirmation(can_confirm)

        if _process_confirmation_choice(choice, can_confirm):
            break


def _distribute_single_ability(
    ability: Ability,
    ability_scores: AbilityScores,
    assigned_values: dict,
    remaining_points: int,
    valid_values: list[int],
    cost_table: dict[int, int],
) -> None:
    """Распределить одну характеристику."""
    while True:
        # Определяем доступные значения на основе оставшихся очков
        available_values = []
        for value in valid_values:
            cost = cost_table.get(value, 0)
            if cost <= remaining_points:
                available_values.append(value)

        print(f"\nРаспределите значение для {ability.get_localized_name()}")
        print(
            "💰 {}: {}".format(
                t("ability_generation.point_buy.remaining_points"),
                remaining_points,
            )
        )
        print(
            "📊 {}: {}".format(
                t("ability_generation.point_buy.available_values"),
                ", ".join(map(str, available_values)),
            )
        )

        try:
            choice = input("Выберите значение (0 для пропуска): ").strip()

            if choice == "0":
                # Пропускаем характеристику - оставляем значение 1
                assigned_values[ability] = 1
                break

            try:
                value = int(choice)
                if value in available_values:
                    cost = cost_table.get(value, 0)
                    assigned_values[ability] = value
                    ability_scores.set_base_score(ability, value)
                    print(
                        f"✅ {ability.get_localized_name()}: {value} (стоимость: {cost} очков)"
                    )
                    break
                else:
                    cost = (
                        cost_table.get(value, 0)
                        if value in valid_values
                        else 0
                    )
                    if cost > remaining_points:
                        print(
                            f"❌ Значение {value} стоит {cost} очков, у вас осталось только {remaining_points}"
                        )
                    else:
                        print(
                            "❌ Значение {} недоступно. Доступные значения: {}".format(
                                value, ", ".join(map(str, available_values))
                            )
                        )
            except ValueError:
                print(t("ability_generation.error_invalid"))
        except ValueError:
            print(t("ability_generation.error_invalid"))


def generate_random_scores(
    ability_scores: AbilityScores, hardcore_mode: bool = False
) -> None:
    """Генерация характеристик случайным образом."""
    print(f"\n{t('ability_generation.random.title')}")
    print("=" * 40)
    print(f"{t('ability_generation.random.description')}")
    print()

    # Генерируем значения
    import random

    # 4d6 drop lowest для каждой характеристики
    scores = []
    for _ in range(6):
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls.sort(reverse=True)
        scores.append(sum(rolls[:3]))
    print(
        f"🎲 {t('ability_generation.random.rolled_values')}: {', '.join(map(str, scores))}"
    )
    print()

    if hardcore_mode:
        # Hardcore режим - случайное распределение
        abilities = [
            AbilityEnum.STRENGTH,
            AbilityEnum.DEXTERITY,
            AbilityEnum.CONSTITUTION,
            AbilityEnum.INTELLIGENCE,
            AbilityEnum.WISDOM,
            AbilityEnum.CHARISMA,
        ]
        random.shuffle(scores)
        for ability, value in zip(abilities, scores, strict=True):
            ability_scores.set_base_score(Ability(ability), value)

        print(f"⚡ {t('ability_generation.random.hardcore_mode')}")
        display_abilities_with_bonuses(ability_scores)
    else:
        # Обычный режим - выбор распределения
        abilities = [
            AbilityEnum.STRENGTH,
            AbilityEnum.DEXTERITY,
            AbilityEnum.CONSTITUTION,
            AbilityEnum.INTELLIGENCE,
            AbilityEnum.WISDOM,
            AbilityEnum.CHARISMA,
        ]
        remaining_scores = scores.copy()

        for ability in abilities:
            ability_obj = Ability(ability)
            while True:
                print(
                    f"\n{t('ability_generation.random.assign_prompt', ability=ability_obj.get_localized_name())}"
                )
                print(
                    f"{t('ability_generation.random.remaining_values')}: {', '.join(map(str, remaining_scores))}"
                )

                try:
                    choice = input("Выберите значение: ").strip()

                    # Только ввод значения
                    try:
                        value = int(choice)
                        if value in remaining_scores:
                            remaining_scores.remove(value)
                            ability_scores.set_base_score(ability_obj, value)
                            print(
                                f"✅ {ability_obj.get_localized_name()}: {value}"
                            )
                            break
                        else:
                            print(
                                f"❌ Значение {value} отсутствует в списке доступных"
                            )
                    except ValueError:
                        print(t("ability_generation.error_invalid"))
                except ValueError:
                    print(t("ability_generation.error_invalid"))


def handle_variant_human_ability_choice(ability_scores: AbilityScores) -> None:
    """Обработать выбор характеристик для Человека (варианта)."""
    print("\n⚡ ВЫБОР ХАРАКТЕРИСТИК ДЛЯ ЧЕЛОВЕКА (ВАРИАНТА)")
    print("=" * 50)
    print("Выберите 2 характеристики для увеличения на +1")
    print()

    # Получаем список всех характеристик
    abilities = [
        AbilityEnum.STRENGTH,
        AbilityEnum.DEXTERITY,
        AbilityEnum.CONSTITUTION,
        AbilityEnum.INTELLIGENCE,
        AbilityEnum.WISDOM,
        AbilityEnum.CHARISMA,
    ]
    choices_made = 0
    max_choices = 2

    while choices_made < max_choices:
        print(
            f"\n📊 Осталось выбрать: {max_choices - choices_made} характеристик"
        )
        print("Доступные характеристики:")

        for i, ability in enumerate(abilities, 1):
            ability_obj = Ability(ability)
            current_total = ability_scores.get_total_score(
                ability_obj._ability
            )
            modifier = ability_scores.get_modifier(ability_obj._ability)
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            print(
                f"{i}. {ability_obj.get_localized_name()}: {current_total} (мод. {modifier_str})"
            )

        try:
            choice = input(
                f"\nВыберите характеристику ({choices_made + 1}/{max_choices}): "
            ).strip()

            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(abilities):
                    selected_ability = abilities[index]
                    selected_ability_obj = Ability(selected_ability)

                    # Применяем бонус
                    current_bonus = ability_scores.racial_bonuses.get(
                        selected_ability_obj._ability, 0
                    )
                    ability_scores.racial_bonuses[
                        selected_ability_obj._ability
                    ] = (current_bonus + 1)

                    print(
                        f"✅ {selected_ability_obj.get_localized_name()} увеличена на +1"
                    )
                    choices_made += 1

                    # Показываем текущее состояние
                    print("\n📊 Текущие бонусы:")
                    for ability in abilities:
                        ability_obj = Ability(ability)
                        bonus = ability_scores.racial_bonuses.get(
                            ability_obj._ability, 0
                        )
                        if bonus > 0:
                            print(
                                f"   {ability_obj.get_localized_name()}: +{bonus}"
                            )
                else:
                    print("❌ Неверный номер характеристики")
            else:
                print("❌ Введите номер характеристики")
        except ValueError:
            print("❌ Неверный ввод")

    print("\n✅ Выбор характеристик завершен!")


def generate_ability_scores(
    race: Race, subrace: SubRace | None = None, hardcore_mode: bool = False
) -> AbilityScores:
    """Основная функция генерации характеристик."""
    from src.domain.value_objects.ability_scores import (
        AbilityScores as DomainAbilityScores,
    )

    # Создаем объект характеристик
    ability_scores = AbilityScores(DomainAbilityScores())

    # Применяем расовые бонусы через универсальный метод
    # Получаем доменные объекты
    domain_race = race._race if hasattr(race, "_race") else race
    domain_subrace = (
        subrace._subrace
        if subrace and hasattr(subrace, "_subrace")
        else subrace
    )

    if hasattr(domain_race, "get_effective_ability_bonuses"):
        subrace_arg = (
            domain_subrace
            if isinstance(domain_subrace, DomainSubRace)
            else None
        )
        effective_bonuses = domain_race.get_effective_ability_bonuses(
            subrace_arg
        )
    else:
        effective_bonuses = {}
    ability_scores.apply_racial_bonuses(effective_bonuses)

    # Отображаем бонусы от расы
    display_racial_bonuses(race, subrace)

    # Выбираем метод генерации
    display_ability_generation_methods()
    method = select_ability_generation_method()

    # Генерируем характеристики выбранным методом
    if method == "standard":
        generate_standard_array(ability_scores)
    elif method == "point_buy":
        generate_point_buy(ability_scores)
    elif method == "random":
        generate_random_scores(ability_scores, hardcore_mode)

    # Обрабатываем выбор характеристик для подрас с выбором
    if subrace and _has_ability_choice_feature(subrace):
        handle_variant_human_ability_choice(ability_scores)

    # Финальное отображение
    print(f"\n{t('ability_generation.final.title')}")
    print("=" * 40)
    display_abilities_with_bonuses(ability_scores)

    return ability_scores


def _has_ability_choice_feature(subrace: SubRace) -> bool:
    """Проверить, есть ли у подрасы черта с выбором характеристик."""
    for feature in subrace.features:
        mechanics = feature.mechanics
        if (
            mechanics.get("type") == "ability_bonus"
            and mechanics.get("target") == "choice"
            and mechanics.get("choice") is True
        ):
            return True
    return False
