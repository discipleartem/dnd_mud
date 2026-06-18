"""Отрисовка экранов меню (приветствие, главное меню, настройки,
языки, сложность, flows)."""

import os
from typing import Any

from colorama import Fore, Style

from core.adventure import load_adventures
from core.character import (
    load_characters,
    save_character,
)
from core.localization import get_string, load_strings
from core.models import Adventure
from ui.input_handler import get_int_input, get_str_input

SEPARATOR = f"{Fore.YELLOW}{'=' * 78}{Style.RESET_ALL}"

ABILITY_NAMES_RU = {
    "strength": "Сила",
    "dexterity": "Ловкость",
    "constitution": "Выносливость",
    "intelligence": "Интеллект",
    "wisdom": "Мудрость",
    "charisma": "Харизма",
}


def show_welcome_screen(version: str, strings: dict[str, Any]) -> None:
    """Показать приветственный экран."""
    print()
    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'welcome.title').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()
    print(
        f"{Fore.GREEN}{get_string(strings, 'welcome.subtitle')}"
        f"{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}"
        f"{get_string(strings, 'welcome.version', version=version)}"
        f"{Style.RESET_ALL}"
    )
    print()


def _clear_screen() -> None:
    """Очистить экран терминала."""
    os.system("cls" if os.name == "nt" else "clear")


def show_main_menu(strings: dict[str, Any]) -> int:
    """Показать главное меню и получить выбор."""
    print(f"{Fore.YELLOW}{'-' * 78}{Style.RESET_ALL}")
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'menu.caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(f"{Fore.YELLOW}{'-' * 78}{Style.RESET_ALL}")
    print()

    menu_items = [
        ("1", get_string(strings, "menu.new_game")),
        ("2", get_string(strings, "menu.load_game")),
        ("3", get_string(strings, "menu.create_character")),
        ("4", get_string(strings, "menu.settings")),
        ("5", get_string(strings, "menu.languages")),
        ("0", get_string(strings, "menu.exit")),
    ]
    for num, label in menu_items:
        print(f"  {Fore.YELLOW}{num}{Style.RESET_ALL}. {label}")

    print()
    print(SEPARATOR)
    print()

    prompt = get_string(strings, "menu.prompt", max=5)
    return get_int_input(prompt, 0, 5)


def select_difficulty(
    strings: dict[str, Any], settings: dict[str, Any]
) -> str | None:
    """Экран выбора сложности.

    Args:
        strings: Словарь со строками интерфейса
        settings: Текущие настройки (используется difficulty по умолчанию)

    Returns:
        'normal' или 'hardcore', None если пользователь нажал Назад
    """
    _clear_screen()

    default = settings.get("difficulty", "normal")
    current_idx = 1 if default == "normal" else 2

    while True:
        print(SEPARATOR)
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'difficulty.caption').center(78)}"
            f"{Style.RESET_ALL}"
        )
        print(SEPARATOR)
        print()

        options = [
            get_string(strings, "difficulty.normal"),
            get_string(strings, "difficulty.hardcore"),
        ]
        for idx, opt in enumerate(options, 1):
            if current_idx == idx:
                marker = f"{Fore.GREEN}* {Style.RESET_ALL}"
            else:
                marker = "  "
            print(f"{marker}{Fore.YELLOW}{idx}{Style.RESET_ALL}. {opt}")
        print()
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'difficulty.back')}"
        )
        print()

        choice = get_int_input(
            get_string(strings, "difficulty.prompt", count=len(options)),
            0,
            len(options),
        )

        if choice == 0:
            return None

        return "normal" if choice == 1 else "hardcore"


def _select_character(strings: dict[str, Any]) -> dict[str, Any] | None:
    """Экран выбора персонажа из списка сохранённых.

    Returns:
        Выбранный персонаж (dict) или None, если список пуст/нажат Назад
    """
    characters = load_characters()

    if not characters:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'new_game.no_characters')}"
            f"{Style.RESET_ALL}"
        )
        print()
        input(f"{Fore.CYAN}[Enter]{Style.RESET_ALL}")
        return None

    _clear_screen()
    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'choose_character.caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()

    for idx, char in enumerate(characters, 1):
        race = char.get("race", "?")
        cls = char.get("class", "?")
        name = char.get("name", "?")
        level = char.get("level", 1)
        line = get_string(
            strings,
            "new_game.line",
            name=name,
            level=level,
            race=race,
            class_name=cls,
        )
        print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {line}")

    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'new_game.back')}"
    )
    print()
    choice = get_int_input(
        get_string(strings, "new_game.prompt", count=len(characters)),
        0,
        len(characters),
    )

    if choice == 0:
        return None

    return characters[choice - 1]


def _print_character_info(
    character: dict[str, Any], strings: dict[str, Any]
) -> None:
    name = character.get("name")
    level = character.get("level", 1)
    race = character.get("race")
    cls = character.get("class")
    print(f"  {name} — ур. {level} {race}/{cls}")


def _select_adventure(strings: dict[str, Any]) -> Adventure | None:
    """Экран выбора приключения.

    Returns:
        Выбранное приключение (Adventure) или None
    """
    adventures: list[Adventure] = load_adventures()

    if not adventures:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'adventures.no_adventures')}"
            f"{Style.RESET_ALL}"
        )
        print()
        input(f"{Fore.CYAN}[Enter]{Style.RESET_ALL}")
        return None

    _clear_screen()
    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'adventures.caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()

    for idx, adv in enumerate(adventures, 1):
        line = get_string(
            strings,
            "adventures.adventure_line",
            name=adv.name if isinstance(adv.name, str) else adv.get_name(),
            difficulty=adv.difficulty,
            desc=adv.description,
        )
        print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {line}")

    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'adventures.back')}"
    )
    print()
    choice = get_int_input(
        get_string(strings, "adventures.prompt", count=len(adventures)),
        0,
        len(adventures),
    )

    if choice == 0:
        return None

    return adventures[choice - 1]


def show_new_game_flow(
    strings: dict[str, Any], settings: dict[str, Any]
) -> None:
    """Flow «Новая игра»: сложность → персонаж → приключение."""
    difficulty = select_difficulty(strings, settings)
    if difficulty is None:
        return

    characters = load_characters()
    if characters:
        character = _select_character(strings)
        if character is None:
            return
    else:
        character = show_create_character_flow(
            strings, settings, difficulty=difficulty
        )
        if character is None:
            return

    adventure = _select_adventure(strings)
    if adventure is None:
        return

    print()
    print(
        f"{Fore.GREEN}"
        f"Запуск приключения '{adventure.get_name()}' "
        f"с персонажем '{character.get('name', '?')}' "
        f"(сложность: {difficulty})"
        f"{Style.RESET_ALL}"
    )
    print()
    input(f"{Fore.CYAN}[Enter]{Style.RESET_ALL}")


def _print_race_info(
    info: dict[str, Any], strings: dict[str, Any]
) -> None:
    """Print race or subrace details: description, bonuses, features."""
    desc = info.get("description", "")
    if desc:
        print(get_string(strings, "character.race_description", desc=desc))
    bonuses = info.get("ability_bonuses", {})
    if bonuses:
        bonus_parts = []
        for stat, val in bonuses.items():
            stat_ru = ABILITY_NAMES_RU.get(stat, stat.capitalize())
            bonus_parts.append(
                f"{Fore.CYAN}{stat_ru}{Style.RESET_ALL}"
                f"+{Fore.GREEN}{val}{Style.RESET_ALL}"
            )
        bonuses_str = ", ".join(bonus_parts)
        print(
            f"  {Fore.MAGENTA}Бонусы:{Style.RESET_ALL} {bonuses_str}"
        )
    features = info.get("features", [])
    if features:
        print(get_string(strings, "character.features_label"))
        for feat in features:
            print(
                get_string(
                    strings, "character.feature_line", name=feat.get("name", "")
                )
            )


def show_create_character_flow(
    strings: dict[str, Any],
    settings: dict[str, Any],
    difficulty: str | None = None,
) -> dict[str, Any] | None:
    """Flow «Создать персонажа»: сложность → создание.

    Args:
        strings: ...
        settings: ...
        difficulty: Если задана, используется без повторного запроса.
    Returns:
        Созданный персонаж (dict) или None
    """
    if difficulty is None:
        difficulty = select_difficulty(strings, settings)
        if difficulty is None:
            return None

    _clear_screen()
    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'character.creation_caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()

    name = get_str_input(
        get_string(strings, "character.name_prompt"),
        min_length=2,
        only_letters=True,
    )

    # Выбор расы/подрасы
    from core.character import load_races, load_race_full

    races = load_races()
    # Собираем плоский список вариантов: базовая раса + её подрасы
    race_options: list[dict[str, Any]] = []
    subrace_options_by_race: dict[str, list[dict[str, Any]]] = {}
    for race in races:
        race_id = race.get("id") or race.get("name")
        race_options.append(
            {
                "type": "race",
                "race_id": race_id,
                "subrace_id": None,
                "name": race.get("name", "?"),
            }
        )
        subraces_for_race: list[dict[str, Any]] = []
        race_full = load_race_full(race_id)
        subraces = race_full.get("subraces", {})
        if subraces:
            for subrace_id, subrace_info in subraces.items():
                subraces_for_race.append(
                    {
                        "type": "subrace",
                        "race_id": race_id,
                        "subrace_id": subrace_id,
                        "name": subrace_info.get("name", subrace_id),
                    }
                )
        subrace_options_by_race[race_id] = subraces_for_race

    _clear_screen()
    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'character.race_caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()

    base_num = 0
    for option in race_options:
        if option["type"] == "race":
            base_num += 1
            marker = f"  {Fore.YELLOW}{base_num}{Style.RESET_ALL}."
        else:
            continue
        print(f"{marker} {option['name']}")
        race_full = load_race_full(option["race_id"])
        _print_race_info(race_full or {}, strings)

        subraces_list = subrace_options_by_race.get(option["race_id"], [])
        if subraces_list:
            print(f"  {Fore.MAGENTA}Подрасы:{Style.RESET_ALL}")
            for sub in subraces_list:
                print(f"     {Fore.CYAN}{sub['name']}{Style.RESET_ALL}")
                race_full = load_race_full(sub["race_id"])
                subraces = race_full.get("subraces", {}) if race_full else {}
                subrace_info = subraces.get(sub["subrace_id"], {})
                _print_race_info(subrace_info, strings)
        print()

    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()
    choice = get_int_input(
        get_string(strings, "character.race_prompt", count=len(race_options)),
        0,
        len(race_options),
    )
    if choice == 0:
        return None
    selected = race_options[choice - 1]
    race_id = selected["race_id"]
    subrace_id = selected.get("subrace_id")

    # Выбор класса
    from core.character import load_classes

    classes = load_classes()
    for idx, cls in enumerate(classes, 1):
        print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {cls.get('name', '?')}")
    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()
    class_idx = get_int_input(
        get_string(strings, "character.class_prompt", count=len(classes)),
        0,
        len(classes),
    )
    if class_idx == 0:
        return None
    cls = classes[class_idx - 1]

    class_id = cls.get("id") or cls.get("name")
    character = save_character(
        name=name,
        race_id=str(race_id),
        class_id=str(class_id),
        difficulty=difficulty,
        subrace_id=str(subrace_id) if subrace_id else None,
    )

    msg = get_string(strings, "character.save_success", name=name)
    print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
    print()
    input(f"{Fore.CYAN}[Enter]{Style.RESET_ALL}")

    return character


def show_load_game_flow(strings: dict[str, Any]) -> None:
    """Flow «Загрузить игру»."""
    _clear_screen()
    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'load_game.caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'errors.load_not_implemented')}"
        f"{Style.RESET_ALL}"
    )
    print()
    input(f"{Fore.CYAN}[Enter]{Style.RESET_ALL}")


def show_languages_menu(
    strings: dict[str, Any], settings: dict[str, Any]
) -> dict[str, Any]:
    """Меню выбора языка.

    Returns:
        Обновлённый settings (возможно, изменён язык)
    """
    _clear_screen()

    while True:
        print(SEPARATOR)
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'languages.caption').center(78)}"
            f"{Style.RESET_ALL}"
        )
        print(SEPARATOR)
        print()

        current = settings.get("language", "ru")
        lang_name = get_string(
            strings, f"languages.lang_{current}", default=current
        )
        print(f"  {get_string(strings, 'languages.current')} {lang_name}")
        print()

        options = [
            get_string(strings, "languages.lang_en"),
            get_string(strings, "languages.lang_ru"),
        ]
        for idx, opt in enumerate(options, 1):
            marker = f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            print(f"{marker}{opt}")
        print()
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'languages.back')}"
        )
        print()

        choice = get_int_input(
            get_string(strings, "languages.prompt", count=len(options)),
            0,
            len(options),
        )

        if choice == 0:
            break

        new_lang = "en" if choice == 1 else "ru"
        settings["language"] = new_lang
        strings = load_strings(new_lang)
        msg = get_string(
            strings,
            "languages.changed",
            name=get_string(strings, f"languages.lang_{new_lang}"),
        )
        print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
        print()
        input(f"{Fore.CYAN}[Enter]{Style.RESET_ALL}")
        _clear_screen()

    return settings


def show_settings(
    strings: dict[str, Any], settings: dict[str, Any]
) -> dict[str, Any]:
    """Экран настроек.

    Позволяет переключить режим Hard Core и сложность.

    Args:
        strings: Словарь со строками интерфейса
        settings: Текущие настройки
        {"language": str, "hardcore": bool, "difficulty": str}

    Returns:
        Обновлённый словарь настроек
    """
    _clear_screen()

    while True:
        print(SEPARATOR)
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'settings.caption').center(78)}"
            f"{Style.RESET_ALL}"
        )
        print(SEPARATOR)
        print()

        hardcore = settings.get("hardcore", False)
        print(f'  {get_string(strings, "settings.hardcore")}: {hardcore}')
        print()

        options = [
            get_string(strings, "settings.settings_option_hardcore"),
        ]
        for idx, opt in enumerate(options, 1):
            marker = f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            print(f"{marker}{opt}")
        print()
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'settings.back')}"
        )
        print()

        choice = get_int_input(
            get_string(strings, "settings.prompt", count=len(options)),
            0,
            len(options),
        )

        if choice == 0:
            break

        if choice == 1:
            settings["hardcore"] = not settings.get("hardcore", False)
            msg = get_string(
                strings,
                "settings.hardcore_changed",
                value=str(settings["hardcore"]),
            )
            print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
            print()
            input(f"{Fore.CYAN}[Enter]{Style.RESET_ALL}")

        _clear_screen()

    return settings
