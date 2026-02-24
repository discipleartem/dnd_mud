"""Модуль создания новой игры.

Предоставляет функции для создания нового персонажа
и настройки начальных параметров игры.
"""

from i18n import t
from src.ui.entities.character import Character
from src.ui.entities.race import Race, SubRace
from src.ui.main_menu.ability_generation import generate_ability_scores


def get_character_name() -> str:
    """Получить и валидировать имя персонажа.

    Returns:
        Валидированное имя персонажа.
    """
    while True:
        name = input(t("new_game.character_name.prompt")).strip()
        if not name:
            print(t("new_game.character_name.error_empty"))
            continue
        if len(name) < 2:
            print(t("new_game.character_name.error_too_short"))
            continue
        if len(name) > 15:
            print(t("new_game.character_name.error_too_long"))
            continue
        return name


def display_races(races: dict[str, Race]) -> None:
    """Отобразить список доступных рас.

    Args:
        races: Словарь рас для отображения.
    """
    print(f"\n{t('new_game.race_selection.title')}")
    print("=" * 40)
    for i, (_race_id, race) in enumerate(races.items(), 1):
        print(f"{i}. {race.name}")
        if race.ability_bonuses_description:
            print(f"   🎯 {race.ability_bonuses_description}")
        print()


def select_race(races: dict[str, Race]) -> Race:
    """Выбрать расу из списка.

    Args:
        races: Словарь доступных рас.

    Returns:
        Выбранная раса.
    """
    while True:
        try:
            choice = input(t("new_game.race_selection.prompt")).strip()

            if choice.isdigit():
                race_index = int(choice) - 1
                race_list = list(races.values())
                if 0 <= race_index < len(race_list):
                    return race_list[race_index]
                print(t("new_game.race_selection.error_number"))
                continue

            selected_race = Race.get_race_by_name(choice)
            if selected_race:
                return selected_race
            print(t("new_game.race_selection.error_not_found"))

        except ValueError:
            print(t("new_game.race_selection.error_invalid"))


def display_race_details(race: Race) -> None:
    """Отобразить подробную информацию о расе.

    Args:
        race: Раса для отображения.
    """
    title = t("new_game.race_details.title", race_name=race.name)
    print(f"\n{title}")
    print("=" * 50)
    print(f"{t('new_game.race_details.description_label')} {race.description}")

    print(f"\n{t('new_game.race_details.abilities_label')}")
    if race.ability_bonuses_description:
        print(f"   {race.ability_bonuses_description}")
    else:
        print(f"   {t('new_game.race_details.no_bonuses')}")

    if race.features:
        print(f"\n{t('new_game.race_details.features_label')}")
        for feature in race.features:
            feature_emoji = _get_feature_emoji(feature.name)
            print(f"   • {feature_emoji} {feature.name}")
            print(f"     {feature.description}")

    print(f"\n{t('new_game.race_details.other_stats_label')}")
    size_name = race.size.get_localized_name()
    print(f"   {t('new_game.race_details.size_label')} {size_name}")
    print(
        f"   {t('new_game.race_details.speed_label')} {race.speed} "
        f"{t('new_game.race_details.speed_unit')}"
    )
    languages_display = race.get_languages_display()
    print(
        f"   {t('new_game.race_details.languages_label')} "
        f"{languages_display}"
    )


def select_subrace(race: Race) -> SubRace | None:
    """Универсально выбрать подрасу для любой расы.

    Args:
        race: Базовая раса для выбора подрасы.

    Returns:
        Выбранная подраса или None.
    """
    if not race.subraces:
        return None

    title = t("new_game.subrace_selection.title", race_name=race.name)
    print(f"\n{title}")
    print("=" * 40)

    # Создаём список опций выбора
    options: list[tuple[str, SubRace | None, str]] = []

    # Добавляем основную расу как вариант выбора только если разрешено
    if race.allow_base_race_choice:
        base_option = t(
            "new_game.subrace_selection.base_race_option", race_name=race.name
        )
        options.append((str(base_option), None, "👤"))
        print(f"1. 👤 {base_option}")
        start_number = 2
    else:
        start_number = 1

    # Добавляем доступные подрасы
    subrace_list = list(race.subraces.values())
    for i, subrace in enumerate(subrace_list, start_number):
        emoji = _get_subrace_emoji(subrace.name)
        options.append((str(subrace.name), subrace, emoji))
        print(f"{i}. {emoji} {subrace.name}")

    # Показываем подробности о всех опциях
    details_title = t("new_game.details_section.title")
    print(f"\n{details_title}")
    print("-" * 40)

    # Детали базовой расы (только если разрешено выбирать)
    if race.allow_base_race_choice:
        base_option = t(
            "new_game.subrace_selection.base_race_option", race_name=race.name
        )
        base_desc = t(
            "new_game.subrace_selection.base_race_description",
            race_name=race.name,
        )
        print(f"\n1. 👤 {base_option}")
        print(f"   {base_desc}")
        if race.ability_bonuses_description:
            abilities_label = t("new_game.details_section.abilities_label")
            print(f"   {abilities_label} {race.ability_bonuses_description}")
        if race.features:
            features_label = t("new_game.details_section.features_label")
            print(f"   {features_label}")
            for feature in race.features:
                feature_emoji = _get_feature_emoji(feature.name)
                print(f"      • {feature_emoji} {feature.name}")
                print(f"        {feature.description}")

    # Детали подрас
    for i, subrace in enumerate(subrace_list, start_number):
        emoji = _get_subrace_emoji(subrace.name)
        print(f"\n{i}. {emoji} {subrace.name}")
        print(f"   {subrace.description}")

        if subrace.ability_bonuses_description:
            abilities_label = t("new_game.details_section.abilities_label")
            print(
                f"   {abilities_label} "
                f"{subrace.ability_bonuses_description}"
            )

        if subrace.features:
            features_label = t("new_game.details_section.features_label")
            print(f"   {features_label}")
            for feature in subrace.features:
                feature_emoji = _get_feature_emoji(feature.name)
                print(f"      • {feature_emoji} {feature.name}")
                print(f"        {feature.description}")

    # Цикл выбора
    while True:
        try:
            prompt = t(
                "new_game.subrace_selection.prompt", race_name=race.name
            )
            choice = input(f"\n{prompt}").strip()

            if choice.isdigit():
                choice_num = int(choice)

                if 1 <= choice_num <= len(options):
                    selected_option = options[choice_num - 1]
                    return selected_option[1]  # Возвращаем SubRace или None
                else:
                    print(t("new_game.subrace_selection.error_number"))
            else:
                print(t("new_game.subrace_selection.error_invalid"))

        except ValueError:
            print(t("new_game.subrace_selection.error_invalid"))


def _get_subrace_emoji(subrace_name: str) -> str:
    """Получить эмодзи для подрасы на основе названия.

    Args:
        subrace_name: Название подрасы.

    Returns:
        Эмодзи для подрасы.
    """
    return "⚡"


def _get_feature_emoji(feature_name: str) -> str:
    """Получить эмодзи для особенности на основе названия.

    Args:
        feature_name: Название особенности.

    Returns:
        Эмодзи для особенности.
    """
    feature_emoji_map = {
        "темное зрение": "🌙",
        "светочувствительность": "☀️",
        "устойчивость к магии": "🛡️",
        "мастерство": "⚔️",
        "ловкость": "🏃",
        "маскировка": "🥷",
    }

    feature_name_lower = feature_name.lower()
    return feature_emoji_map.get(feature_name_lower, "⚡")


def new_game() -> Character:
    """Новая игра.

    Returns:
        Созданный персонаж.
    """
    print(t("new_game.title"))
    print(t("new_game.subtitle"))

    # 1. Присвоить имя персонажа
    character = Character()
    character.name = get_character_name()
    success_msg = t("new_game.character_name.success", name=character.name)
    print(success_msg)

    # 2. Получить список рас
    races = Race.get_all_races()

    # 3. Выбор из доступных рас
    display_races(races)
    selected_race = select_race(races)
    character.race = selected_race
    race_success = t(
        "new_game.race_selection.success", race=selected_race.name
    )
    print(race_success)

    # Показываем подробную информацию о расе
    display_race_details(selected_race)

    # 4. Выбор подрасы, если есть
    selected_subrace = select_subrace(selected_race)
    if selected_subrace:
        character.subrace = selected_subrace
        subrace_success = t(
            "new_game.subrace_selection.success", subrace=selected_subrace.name
        )
        print(subrace_success)
    else:
        print(t("new_game.subrace_selection.not_selected"))

    # 5. Генерация характеристик
    print(f"\n{'='*50}")
    print(f"🎲 {t('ability_generation.title')} 🎲")
    print(f"{'='*50}")

    # TODO: Добавить проверку на hardcore режим из настроек
    hardcore_mode = False  # Временно выключен

    character.ability_scores = generate_ability_scores(
        selected_race, selected_subrace, hardcore_mode
    )

    print(f"\n✅ {t('ability_generation.final.title')}")
    print(f"📊 {t('ability_generation.final.completed')}")

    return character
