"""Модуль создания новой игры.

Предоставляет функции для создания нового персонажа
и настройки начальных параметров игры.
"""

from i18n import t
from src.ui.adapters.updated_adapters import Character
from src.ui.adapters.updated_adapters import Race as UpdatedRace
from src.ui.adapters.updated_adapters import SubRace as UpdatedSubRace
from src.ui.dto.character_dto import CharacterDTO
from src.ui.factories.domain_factory import RaceFactory
from src.utils.ui_helpers import display_error, get_numeric_choice


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


def display_races(races: dict[str, UpdatedRace]) -> None:
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


def select_race(races: dict[str, UpdatedRace]) -> UpdatedRace:
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

            # Создаем фабрику и получаем расу
            factory = RaceFactory()
            selected_race = factory.get_race_by_name(choice)
            if selected_race:
                return selected_race
            print(t("new_game.race_selection.error_not_found"))

        except ValueError:
            print(t("new_game.race_selection.error_invalid"))


def display_race_details(race: UpdatedRace) -> None:
    """Отобразить подробную информацию о расе.

    Args:
        race: Раса для отображения.
    """
    title = t("new_game.race_details.title", race_name=race.name)
    print(f"\n{title}")
    print("=" * 50)
    print(
        "{}: {}".format(
            t("new_game.race_details.description_label"),
            getattr(race, "description", "Нет описания"),
        )
    )

    print(f"\n{t('new_game.race_details.abilities_label')}")
    if race.ability_bonuses_description:
        print(f"   {race.ability_bonuses_description}")
    else:
        print(f"   {t('new_game.race_details.no_bonuses')}")

    if race.features:
        print(f"\n{t('new_game.race_details.features_label')}")
        for feature in race.features:
            # feature - это словарь, а не объект
            feature_name = feature.get("name", "Без названия")
            feature_description = feature.get("description", "Нет описания")
            feature_emoji = _get_feature_emoji(feature_name)
            print(f"   • {feature_emoji} {feature_name}")
            print(f"     {feature_description}")

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


def _create_subrace_options(
    race: UpdatedRace,
) -> tuple[list[tuple[str, UpdatedRace | None, str]], int]:
    """Создать список опций выбора подрасы.

    Returns:
        (список опций, начальный номер)
    """
    options: list[tuple[str, UpdatedRace | None, str]] = []
    start_number = 1

    # Добавляем основную расу как вариант выбора
    if race.allow_base_race_choice:
        base_option = t(
            "new_game.subrace_selection.base_race_option", race_name=race.name
        )
        options.append((str(base_option), None, "👤"))
        start_number = 2

    # Добавляем доступные подрасы
    subrace_list = race.subraces
    for _i, subrace in enumerate(subrace_list, start_number):
        emoji = _get_subrace_emoji(subrace.name)
        options.append((str(subrace.name), subrace, emoji))

    return options, start_number


def _display_subrace_options(
    options: list[tuple[str, UpdatedSubRace | None, str]],
) -> None:
    """Отобразить опции выбора подрасы."""
    for i, (name, _, emoji) in enumerate(options, 1):
        print(f"{i}. {emoji} {name}")


def _display_base_race_details(race: UpdatedRace) -> None:
    """Отобразить детали базовой расы."""
    if not race.allow_base_race_choice:
        return

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
            # feature - это словарь, а не объект
            feature_name = feature.get("name", "Без названия")
            feature_description = feature.get("description", "Нет описания")
            feature_emoji = _get_feature_emoji(feature_name)
            print(f"      • {feature_emoji} {feature_name}")
            print(f"        {feature_description}")


def _display_subrace_details(
    subrace_list: list[UpdatedRace], start_number: int
) -> None:
    """Отобразить детали подрас."""
    for i, subrace in enumerate(subrace_list, start_number):
        emoji = _get_subrace_emoji(subrace.name)
        print(f"\n{i}. {emoji} {subrace.name}")
        print(f"   {subrace._dto.description}")

        if subrace.ability_bonuses_description:
            abilities_label = t("new_game.details_section.abilities_label")
            print(
                f"   {abilities_label} {subrace.ability_bonuses_description}"
            )

        if subrace.features:
            features_label = t("new_game.details_section.features_label")
            print(f"   {features_label}")
            for feature in subrace.features:
                # feature - это словарь, а не объект
                feature_name = feature.get("name", "Без названия")
                feature_description = feature.get(
                    "description", "Нет описания"
                )
                feature_emoji = _get_feature_emoji(feature_name)
                print(f"      • {feature_emoji} {feature_name}")
                print(f"        {feature_description}")


def _handle_subrace_choice(
    options: list[tuple[str, UpdatedRace | None, str]],
) -> UpdatedRace | None:
    """Обработать выбор подрасы.

    Returns:
        Выбранная подраса или None
    """
    try:
        prompt = str(t("new_game.subrace_selection.prompt"))
        choice_num = get_numeric_choice(len(options), prompt)

        selected_option = options[choice_num - 1]
        return selected_option[1]  # Возвращаем Race (SubRace как Race)
    except (ValueError, IndexError):
        error_msg = str(t("new_game.subrace_selection.error_invalid"))
        display_error(error_msg)
        return None


def select_subrace(race: UpdatedRace) -> UpdatedRace | None:
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

    # Создаем опции и отображаем их
    options, start_number = _create_subrace_options(race)
    _display_subrace_options(options)

    # Показываем детали
    details_title = t("new_game.details_section.title")
    print(f"\n{details_title}")
    print("-" * 40)

    subrace_list = race.subraces
    _display_base_race_details(race)
    _display_subrace_details(subrace_list, start_number)

    # Обрабатываем выбор
    return _handle_subrace_choice(options)


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
        Созданный персонаж
    """
    print(t("new_game.title"))
    print("=" * 50)

    # 1. Получить имя персонажа
    character_name = get_character_name()
    character = Character(character_dto=CharacterDTO(name=character_name))
    success_msg = t("new_game.character_name.success", name=character.name)
    print(success_msg)

    # 2. Получить список рас
    factory = RaceFactory()
    races = factory.get_all_races()

    # 3. Выбор из доступных рас
    display_races(races)
    selected_race = select_race(races)
    selected_race_dto = selected_race.get_dto()
    character.update_race(selected_race_dto, None)
    race_success = t(
        "new_game.race_selection.success", race=selected_race.name
    )
    print(race_success)

    # Показываем подробную информацию о расе
    display_race_details(selected_race)

    # 4. Выбор подрасы, если есть
    selected_subrace = select_subrace(selected_race)
    if selected_subrace:
        selected_subrace_dto = selected_subrace.get_dto()
        character.update_race(selected_race_dto, selected_subrace_dto)
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

    # Используем новый Use Case для генерации характеристик
    from src.use_cases.ability_generation import AbilityGenerationUseCase

    ability_use_case = AbilityGenerationUseCase()

    # Генерируем характеристики с учетом расовых бонусов
    final_scores = ability_use_case.generate_with_race_bonuses(
        selected_race, selected_subrace, method="standard"
    )

    # Валидируем характеристики
    validation_errors = ability_use_case.validate_scores(final_scores)
    if validation_errors:
        print("⚠️ Обнаружены ошибки в характеристиках:")
        for error in validation_errors:
            print(f"   • {error}")
        print("📊 Используем скорректированные характеристики")

    # Устанавливаем характеристики персонажу
    character.set_ability_scores(final_scores)

    # Показываем результат
    print(f"\n✅ {t('ability_generation.final.title')}")
    print(f"📊 {t('ability_generation.final.completed')}")

    # Отображаем итоговые характеристики
    print(f"\n{'='*30}")
    print("📋 Итоговые характеристики:")
    print(f"{'='*30}")
    print(
        f"💪 Сила: {final_scores.strength} ({final_scores.get_modifier('strength'):+d})"
    )
    print(
        f"🏃 Ловкость: {final_scores.dexterity} ({final_scores.get_modifier('dexterity'):+d})"
    )
    print(
        f"🛡️ Телосложение: {final_scores.constitution} ({final_scores.get_modifier('constitution'):+d})"
    )
    print(
        f"🧠 Интеллект: {final_scores.intelligence} ({final_scores.get_modifier('intelligence'):+d})"
    )
    print(
        f"�️ Мудрость: {final_scores.wisdom} ({final_scores.get_modifier('wisdom'):+d})"
    )
    print(
        f"🗣️ Харизма: {final_scores.charisma} ({final_scores.get_modifier('charisma'):+d})"
    )
    print(f"{'='*30}")

    return character
