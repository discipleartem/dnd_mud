"""Модуль генерации характеристик персонажа."""

from typing import Any

from i18n import t
from src.ui.entities.abilities import (
    Ability,
    AbilityScores,
    PointBuyCosts,
    PointBuySystem,
    RandomGeneration,
    StandardArray,
)
from src.ui.entities.race import Race, SubRace


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

    # Получаем итоговые бонусы через универсальный метод
    effective_bonuses = race.get_effective_ability_bonuses(subrace)

    # Показываем бонусы базовой расы (только если они применяются)
    if subrace and subrace.inherit_base_abilities and race.ability_bonuses:
        print(f"🏛️ {race.name}:")
        for ability_name, bonus in race.ability_bonuses.items():
            try:
                ability = Ability(ability_name)
                print(f"   {ability.get_localized_name()}: +{bonus}")
            except ValueError:
                continue

    # Показываем бонусы подрасы
    if subrace and subrace.ability_bonuses:
        print(f"🌟 {subrace.name}:")
        for ability_name, bonus in subrace.ability_bonuses.items():
            try:
                ability = Ability(ability_name)
                print(f"   {ability.get_localized_name()}: +{bonus}")
            except ValueError:
                continue
    elif subrace and not subrace.inherit_base_abilities:
        # Особый случай для подрас с переопределенными бонусами
        print(f"🌟 {subrace.name}:")
        print(f"   {subrace.ability_bonuses_description}")

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

    for ability in Ability:
        base = ability_scores.base_scores.get(ability, 10)
        bonus = ability_scores.racial_bonuses.get(ability, 0)
        total = ability_scores.get_total_score(ability)
        modifier = ability_scores.get_modifier(ability)

        modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        bonus_str = f"+{bonus}" if bonus > 0 else "0"

        print(
            f"{ability.get_localized_name():<15} {base:<10} "
            f"{bonus_str:<10} {total:<10} {modifier_str:<12}"
        )

    print()


def generate_standard_array(ability_scores: AbilityScores) -> None:
    """Генерация характеристик стандартным массивом."""
    values = StandardArray.get_values()
    abilities = list(Ability)

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
        while True:
            print(
                f"\n{t('ability_generation.standard.assign_prompt', ability=ability.get_localized_name())}"
            )
            print(
                f"{t('ability_generation.standard.remaining_values')}: "
                f"{', '.join(map(str, remaining_values))}"
            )

            try:
                choice = input("Выберите значение: ").strip()

                # Только ввод значения
                try:
                    value = int(choice)
                    if value in remaining_values:
                        remaining_values.remove(value)
                        assigned_values[ability] = value
                        ability_scores.set_base_score(ability, value)
                        print(f"✅ {ability.get_localized_name()}: {value}")
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


def generate_point_buy(ability_scores: AbilityScores) -> None:
    """Генерация характеристик покупкой очков."""
    point_buy = PointBuySystem()
    valid_values = PointBuyCosts.get_valid_values()

    print(f"\n{t('ability_generation.point_buy.title')}")
    print("=" * 40)
    print(f"{t('ability_generation.point_buy.description')}")
    print(
        f"💰 {t('ability_generation.point_buy.total_points')}: "
        f"{point_buy.POINTS_TOTAL}"
    )
    print()

    # Отображаем таблицу стоимостей
    print(f"{t('ability_generation.point_buy.cost_table')}:")
    print(f"{'Значение':<10} {'Стоимость':<10}")
    print("-" * 20)
    for value in valid_values:
        cost = PointBuyCosts.get_cost(value)
        print(f"{value:<10} {cost:<10}")
    print()

    # Устанавливаем начальные значения
    # (1 для всех характеристик - минимально допустимое)
    for ability in Ability:
        ability_scores.set_base_score(ability, 1)

    # Словарь для отслеживания распределенных характеристик
    assigned_values: dict[Any, Any] = {}
    remaining_points = point_buy.POINTS_TOTAL

    # Главный цикл распределения значений
    abilities = list(Ability)

    for ability in abilities:
        _distribute_single_ability(
            ability,
            ability_scores,
            assigned_values,
            remaining_points,
            valid_values,
        )
        # Обновляем remaining_points после каждого распределения
        remaining_points = 27 - sum(
            PointBuyCosts.get_cost(assigned_values[a])
            for a in abilities
            if assigned_values.get(a, 1) != 1
        )

    # Устанавливаем 8 для нераспределенных характеристик
    # (тех что остались со значением 1)
    for ability in abilities:
        if assigned_values.get(ability, 1) == 1:
            ability_scores.set_base_score(ability, 8)
            print(
                f"⚪ {ability.get_localized_name()}: установлено значение 8 (по умолчанию)"
            )

    # Финальное подтверждение
    print(f"\n{t('ability_generation.final.confirmation')}")
    print("=" * 40)
    display_abilities_with_bonuses(ability_scores)
    print(
        f"💰 {t('ability_generation.point_buy.remaining_points')}: "
        f"{remaining_points}"
    )

    # Проверяем, можно ли подтверждать выбор
    unassigned_abilities = [
        a for a in abilities if assigned_values.get(a, 1) == 1
    ]
    can_confirm = len(unassigned_abilities) == 0 and remaining_points == 0

    if not can_confirm:
        if unassigned_abilities:
            print("\n❌ Сначала распределите все характеристики!")
            unassigned_names = [
                a.get_localized_name() for a in unassigned_abilities
            ]
            print(f"Не распределены: {', '.join(unassigned_names)}")

        if remaining_points > 0:
            print(f"\n❌ Осталось нераспределенных очков: {remaining_points}")
            print("Распределите все очки перед подтверждением")

    while True:
        if not can_confirm:
            choice = input(
                "\n1. ✅ Подтвердить выбор\n2. 🔄 Перераспределить очки\nВыберите действие: "
            ).strip()
        else:
            choice = input(
                "\n1. ✅ Подтвердить выбор\nВыберите действие: "
            ).strip()

        if choice == "1":
            if can_confirm:
                print("✅ Выбор подтвержден!")
                break
            else:
                print(
                    "❌ Невозможно подтвердить выбор! "
                    "Сначала распределите все характеристики "
                    "и потратьте все очки."
                )
        elif choice == "2":
            print("🔄 Возврат к распределению очков...")
            # Возвращаем очки за все характеристики кроме тех что были изменены вручную
            total_refund = 0
            for ability in abilities:
                current_value = assigned_values.get(ability, 1)
                if current_value != 1:  # Только для измененных характеристик
                    # Возвращаем очки за эту характеристику
                    cost = PointBuyCosts.get_cost(current_value)
                    total_refund += cost
                    # Сбрасываем значение в 1
                    ability_scores.set_base_score(ability, 1)
                    assigned_values[ability] = 1

            remaining_points += total_refund
            print(f"💰 Возвращено очков: {total_refund}")
            print(f"💰 Всего доступно очков: {remaining_points}")

            # Начинаем заново цикл распределения для всех характеристик
            for ability in abilities:
                if assigned_values.get(ability, 1) == 1:
                    _distribute_single_ability(
                        ability,
                        ability_scores,
                        assigned_values,
                        remaining_points,
                        valid_values,
                    )
                    # Обновляем remaining_points после каждого распределения
                    remaining_points = 27 - sum(
                        PointBuyCosts.get_cost(assigned_values[a])
                        for a in abilities
                        if assigned_values.get(a, 1) != 1
                    )
            break
        else:
            print("❌ Неверный выбор")


def _distribute_single_ability(
    ability: Ability,
    ability_scores: AbilityScores,
    assigned_values: dict,
    remaining_points: int,
    valid_values: list[int],
) -> None:
    """Распределить одну характеристику."""
    while True:
        # Определяем доступные значения на основе оставшихся очков
        available_values = []
        for value in valid_values:
            cost = PointBuyCosts.get_cost(value)
            if cost <= remaining_points:
                available_values.append(value)

        print(f"\nРаспределите значение для {ability.get_localized_name()}")
        print(
            f"💰 {t('ability_generation.point_buy.remaining_points')}: {remaining_points}"
        )
        print(
            f"📊 {t('ability_generation.point_buy.available_values')}: {', '.join(map(str, available_values))}"
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
                    cost = PointBuyCosts.get_cost(value)
                    assigned_values[ability] = value
                    ability_scores.set_base_score(ability, value)
                    print(
                        f"✅ {ability.get_localized_name()}: {value} (стоимость: {cost} очков)"
                    )
                    break
                else:
                    cost = (
                        PointBuyCosts.get_cost(value)
                        if value in valid_values
                        else 0
                    )
                    if cost > remaining_points:
                        print(
                            f"❌ Значение {value} стоит {cost} очков, у вас осталось только {remaining_points}"
                        )
                    else:
                        print(
                            f"❌ Значение {value} недоступно. Доступные значения: {', '.join(map(str, available_values))}"
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
    scores = RandomGeneration.generate_scores()
    print(
        f"🎲 {t('ability_generation.random.rolled_values')}: {', '.join(map(str, scores))}"
    )
    print()

    if hardcore_mode:
        # Hardcore режим - случайное распределение
        assigned = RandomGeneration.assign_randomly(scores)
        for ability, value in assigned.items():
            ability_scores.set_base_score(ability, value)

        print(f"⚡ {t('ability_generation.random.hardcore_mode')}")
        display_abilities_with_bonuses(ability_scores)
    else:
        # Обычный режим - выбор распределения
        abilities = list(Ability)
        remaining_scores = scores.copy()

        for ability in abilities:
            while True:
                print(
                    f"\n{t('ability_generation.random.assign_prompt', ability=ability.get_localized_name())}"
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
                            ability_scores.set_base_score(ability, value)
                            print(
                                f"✅ {ability.get_localized_name()}: {value}"
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
    abilities = list(Ability)
    choices_made = 0
    max_choices = 2

    while choices_made < max_choices:
        print(
            f"\n📊 Осталось выбрать: {max_choices - choices_made} характеристик"
        )
        print("Доступные характеристики:")

        for i, ability in enumerate(abilities, 1):
            current_total = ability_scores.get_total_score(ability)
            modifier = ability_scores.get_modifier(ability)
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            print(
                f"{i}. {ability.get_localized_name()}: {current_total} (мод. {modifier_str})"
            )

        try:
            choice = input(
                f"\nВыберите характеристику ({choices_made + 1}/{max_choices}): "
            ).strip()

            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(abilities):
                    selected_ability = abilities[index]

                    # Применяем бонус
                    current_bonus = ability_scores.racial_bonuses.get(
                        selected_ability, 0
                    )
                    ability_scores.racial_bonuses[selected_ability] = (
                        current_bonus + 1
                    )

                    print(
                        f"✅ {selected_ability.get_localized_name()} увеличена на +1"
                    )
                    choices_made += 1

                    # Показываем текущее состояние
                    print("\n📊 Текущие бонусы:")
                    for ability in abilities:
                        bonus = ability_scores.racial_bonuses.get(ability, 0)
                        if bonus > 0:
                            print(
                                f"   {ability.get_localized_name()}: +{bonus}"
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
    # Создаем объект характеристик
    ability_scores = AbilityScores()

    # Применяем расовые бонусы через универсальный метод
    effective_bonuses = race.get_effective_ability_bonuses(subrace)
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
