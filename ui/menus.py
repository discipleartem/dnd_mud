"""Отрисовка экранов меню (приветствие, главное меню, настройки, языки, сложность, flows)."""

import os
from datetime import datetime
from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from core.character import (
    load_characters,
    save_character,
    character_exists,
)
from core.adventure import load_adventures
from ui.input_handler import get_choice, get_int_input, get_str_input

SEPARATOR = f"{Fore.YELLOW}{'=' * 78}{Style.RESET_ALL}"


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


def select_difficulty(strings: dict[str, Any], settings: dict[str, Any]) -> str | None:
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

        choice = get_choice(
            options,
            get_string(strings, "difficulty.prompt", count=len(options)),
            default_index=current_idx - 1,
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
    choice = get_int_input(
        get_string(strings, "new_game.prompt", count=len(characters)),
        0,
        len(characters),
    )

    if choice == 0:
        return None

    return characters[choice - 1]


def _select_adventure(strings: dict[str, Any]) -> dict[str, Any] | None:
    """Экран выбора приключения.

    Returns:
        Выбранное приключение (dict) или None
    """
    adventures = load_adventures()

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
            name=adv.get("name", "?"),
            difficulty=adv.get("difficulty", "?"),
            desc=adv.get("description", ""),
        )
        print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {line}")

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

    character = _select_character(strings)
    if character is None:
        return

    adventure = _select_adventure(strings)
    if adventure is None:
        return

    print()
    print(
        f"{Fore.GREEN}"
        f"Запуск приключения '{adventure.get('name')}' "
        f"с персонажем '{character.get('name')}' "
        f"(сложность: {difficulty})"
        f"{Style.RESET_ALL}"
    )
    print()
    input(f"{Fore.CYAN}[Enter]{Style.RESET_ALL}")


def show_create_character_flow(
    strings: dict[str, Any], settings: dict[str, Any]
) -> dict[str, Any] | None:
    """Flow «Создать персонажа»: сложность → создание.

    Returns:
        Созданный персонаж (dict) или None
    """
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
    )

    if character_exists(name):
        msg = get_string(
            strings, "character.name_exists", name=name
        )
        print(f"{Fore.RED}{msg}{Style.RESET_ALL}")
        print()
        input(f"{Fore.CYAN}[Enter]{Style.RESET_ALL}")
        return None

    # Выбор расы
    from core.character import load_races

    races = load_races()
    for idx, race in enumerate(races, 1):
        print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {race.get('name', '?')}")
    print()
    race_idx = get_int_input(
        get_string(strings, "character.race_prompt", count=len(races)),
        1,
        len(races),
    )
    race = races[race_idx - 1]

    # Выбор класса
    from core.character import load_classes

    classes = load_classes()
    for idx, cls in enumerate(classes, 1):
        print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {cls.get('name', '?')}")
    print()
    class_idx = get_int_input(
        get_string(strings, "character.class_prompt", count=len(classes)),
        1,
        len(classes),
    )
    cls = classes[class_idx - 1]

    character = save_character(
        name=name,
        race=race.get("id", race.get("name")),
        class_name=cls.get("id", cls.get("name")),
        difficulty=difficulty,
    )

    msg = get_string(
        strings, "character.save_success", name=name
    )
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
        print(f"  {get_string(strings, 'languages.current')}: {lang_name}")
        print()

        options = [
            get_string(strings, "languages.lang_en"),
            get_string(strings, "languages.lang_ru"),
            get_string(strings, "languages.back"),
        ]

        choice = get_choice(
            options,
            get_string(strings, "languages.prompt", count=len(options) - 1),
        )

        if choice == 3:
            break

        new_lang = "en" if choice == 1 else "ru"
        settings["language"] = new_lang
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
        settings: Текущие настройки {"language": str, "hardcore": bool, "difficulty": str}

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
            get_string(strings, "settings.settings_option_back"),
        ]

        choice = get_choice(
            options,
            get_string(strings, "settings.prompt", count=len(options)),
        )

        if choice == 2:
            break

        if choice == 1:
            _clear_screen()
            print(SEPARATOR)
            print(
                f"{Fore.YELLOW}"
                f"{get_string(strings, 'settings.hardcore').center(78)}"
                f"{Style.RESET_ALL}"
            )
            print(SEPARATOR)
            print()

            hc_choice = get_choice(
                [
                    get_string(strings, "settings.hardcore_options.off"),
                    get_string(strings, "settings.hardcore_options.on"),
                ],
                get_string(strings, "settings.hardcore_prompt", count=2),
            )

            settings["hardcore"] = hc_choice == 2
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