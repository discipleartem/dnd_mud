"""Отрисовка экранов меню (приветствие, главное меню, настройки,
языки, сложность, flows)."""

from typing import Any, Literal

from colorama import Fore, Style

from core.adventure import load_adventures
from core.character import (
    POINT_BUY_BUDGET,
    POINT_BUY_COSTS,
    STANDARD_ARRAY,
    STAT_NAMES,
    can_assign_point_buy_value,
    generate_stats_point_buy,
    generate_stats_random,
    generate_stats_standard_array,
    get_race_bonuses,
    load_characters,
    load_classes,
    load_race_full,
    load_races,
    point_buy_total_cost,
    save_character,
)
from core.dice import roll_ability_score
from core.difficulty import adventure_allows_difficulty
from core.localization import get_string, load_strings
from core.models import Adventure, Character
from ui.input_handler import get_int_input, get_str_input

ConfirmStatsResult = Literal["accept", "reroll", "back"]
PoolEntryMode = Literal["list", "manual"]
SelectCharacterResult = Character | Literal["create"] | None

SEPARATOR = f"{Fore.YELLOW}{'=' * 78}{Style.RESET_ALL}"


def _ability_name(strings: dict[str, Any], stat_key: str) -> str:
    """Локализованное имя характеристики."""
    return get_string(strings, f"stats.{stat_key}")


def _press_enter(strings: dict[str, Any]) -> None:
    """Ожидание нажатия Enter."""
    prompt = get_string(strings, "common.press_enter")
    input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")


def _choice_prompt(strings: dict[str, Any]) -> str:
    """Подсказка для числового выбора."""
    return get_string(strings, "common.choice_prompt")


def _stats_caption_line(strings: dict[str, Any]) -> str:
    """Заголовок экрана генерации характеристик."""
    caption = get_string(strings, "character.stats_generation_caption")
    return f"{Fore.YELLOW}{caption.center(78)}{Style.RESET_ALL}"


def _stats_total_line(strings: dict[str, Any]) -> str:
    """Заголовок итоговых характеристик."""
    total = get_string(strings, "character.stats_total")
    return f"{Fore.YELLOW}{total.center(78)}{Style.RESET_ALL}"


def _prompt_pool_value_manual(
    strings: dict[str, Any],
    stat_name: str,
    pool: list[int],
) -> int | None:
    """Запросить значение из пула вручную; 0 — назад."""
    display_pool = sorted(pool, reverse=True)
    enter_msg = get_string(
        strings, "character.stats_enter_value_for", stat=stat_name
    )
    back_hint = get_string(strings, "character.stats_enter_value_back_hint")

    while True:
        print(f"{Fore.YELLOW}{enter_msg} {back_hint}{Style.RESET_ALL}")
        print()
        value = get_int_input(_choice_prompt(strings), 0, 15, strings)
        if value == 0:
            return None
        if value in pool:
            return value
        err = get_string(
            strings,
            "character.stats_value_not_in_pool",
            value=value,
            values=display_pool,
        )
        print(f"{Fore.RED}{err}{Style.RESET_ALL}")


def _prompt_point_buy_stat_value(
    strings: dict[str, Any],
    stat_name: str,
    stats: dict[str, int],
    stat: str,
) -> None:
    """Запросить новое значение point-buy для характеристики."""
    enter_msg = get_string(
        strings, "character.stats_enter_point_buy_value", stat=stat_name
    )

    while True:
        print(f"{Fore.YELLOW}{enter_msg}{Style.RESET_ALL}")
        print()
        value = get_int_input(_choice_prompt(strings), 8, 15, strings)
        if can_assign_point_buy_value(stats, stat, value):
            stats[stat] = value
            return
        if value not in POINT_BUY_COSTS:
            print(
                f"{Fore.RED}"
                f"{get_string(strings, 'character.stats_max_value_15')}"
                f"{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.RED}"
                f"{get_string(strings, 'character.stats_not_enough_points')}"
                f"{Style.RESET_ALL}"
            )


def _assign_stats_from_pool(
    strings: dict[str, Any],
    available: list[int],
    *,
    show_counts: bool = False,
    entry_mode: PoolEntryMode = "list",
    race_id: str | None = None,
    subrace_id: str | None = None,
    show_race_bonuses: bool = False,
) -> dict[str, int] | None:
    """Распределить значения из пула по характеристикам."""
    selected: dict[str, int] = {}
    pool = list(available)
    print_bonuses = show_race_bonuses and race_id is not None

    for stat in STAT_NAMES:
        stat_name = _ability_name(strings, stat)
        print(SEPARATOR)
        print(_stats_caption_line(strings))
        print(SEPARATOR)
        print()

        if print_bonuses:
            assert race_id is not None
            _print_race_bonuses(strings, race_id, subrace_id)
            print()
            print_bonuses = False

        if selected:
            print(
                f"{Fore.GREEN}"
                f"{get_string(strings, 'character.stats_selected_label')}"
                f"{Style.RESET_ALL}"
            )
            for s, v in selected.items():
                s_name = _ability_name(strings, s)
                print(f"  {s_name}: {v}")
            print()

        display_values = pool if show_counts else sorted(pool, reverse=True)
        avail_msg = get_string(
            strings,
            "character.stats_available",
            values=display_values,
        )
        print(f"{Fore.CYAN}{avail_msg}{Style.RESET_ALL}")
        print()

        if entry_mode == "manual":
            selected_value = _prompt_pool_value_manual(
                strings, stat_name, pool
            )
            if selected_value is None:
                return None
        else:
            choose_msg = get_string(
                strings, "character.stats_choose_value_for", stat=stat_name
            )
            print(f"{Fore.YELLOW}{choose_msg}{Style.RESET_ALL}")
            print()

            if show_counts:
                unique_rolls = sorted(set(pool), reverse=True)
                for idx, value in enumerate(unique_rolls, 1):
                    count = pool.count(value)
                    remain_msg = get_string(
                        strings,
                        "character.stats_value_remaining",
                        value=value,
                        count=count,
                    )
                    print(
                        f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {remain_msg}"
                    )
                max_choice = len(unique_rolls)
            else:
                sorted_avail = sorted(pool, reverse=True)
                for idx, value in enumerate(sorted_avail, 1):
                    print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {value}")
                max_choice = len(pool)

            print(
                f"  {Fore.YELLOW}0{Style.RESET_ALL}."
                f" {get_string(strings, 'character.back')}"
            )
            print()

            choice = get_int_input(
                _choice_prompt(strings), 0, max_choice, strings
            )
            if choice == 0:
                return None

            if show_counts:
                sorted_unique = sorted(set(pool), reverse=True)
                selected_value = sorted_unique[choice - 1]
            else:
                sorted_avail = sorted(pool, reverse=True)
                selected_value = sorted_avail[choice - 1]

        selected[stat] = selected_value
        pool.remove(selected_value)

    return selected


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
    return get_int_input(prompt, 0, 5, strings)


def select_difficulty(strings: dict[str, Any]) -> str | None:
    """Экран выбора сложности при создании персонажа."""

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
        marker = f"{Fore.GREEN}* {Style.RESET_ALL}" if idx == 1 else "  "
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
        strings,
    )

    if choice == 0:
        return None

    return "normal" if choice == 1 else "hardcore"


def _difficulty_label(strings: dict[str, Any], difficulty: str) -> str:
    """Локализованное название режима сложности."""
    mode_key = f"difficulty.{difficulty}"
    mode = get_string(strings, mode_key)
    if mode == mode_key:
        return difficulty
    return mode


def _difficulty_color(difficulty: str) -> str:
    """Цвет для отображения режима сложности."""
    if difficulty == "hardcore":
        return Fore.RED
    if difficulty == "normal":
        return Fore.GREEN
    return Fore.CYAN


def _character_race_label(char: Character) -> str:
    """Читаемое название расы или подрасы персонажа."""
    race_full = load_race_full(char.race)
    if char.subrace:
        subraces = race_full.get("subraces", {})
        if isinstance(subraces, dict):
            subrace_info = subraces.get(char.subrace, {})
            if isinstance(subrace_info, dict):
                name = subrace_info.get("name")
                if name:
                    return str(name)
        return char.subrace
    name = race_full.get("name")
    if name:
        return str(name)
    return char.race


def _character_class_label(char: Character) -> str:
    """Читаемое название класса персонажа."""
    for cls in load_classes():
        if cls.get("id") == char.class_name:
            return str(cls.get("name", char.class_name))
    return char.class_name


def _format_character_stats_compact(
    char: Character, strings: dict[str, Any]
) -> str:
    """Компактная строка характеристик: аббревиатура + значение."""
    if not char.stats:
        return ""

    parts = []
    for stat in STAT_NAMES:
        value = char.stats.get(stat)
        if value is None:
            continue
        abbr = _ability_name(strings, stat)[:3]
        parts.append(
            f"{Fore.CYAN}{abbr}{Style.RESET_ALL} "
            f"{Fore.YELLOW}{value:>2}{Style.RESET_ALL}"
        )
    return "  ".join(parts)


def _print_character_card(
    idx: int, char: Character, strings: dict[str, Any]
) -> None:
    """Вывести карточку персонажа в списке выбора."""
    mode = _difficulty_label(strings, char.difficulty)
    mode_color = _difficulty_color(char.difficulty)
    race_label = _character_race_label(char)
    class_label = _character_class_label(char)

    print(
        f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
        f"{Fore.CYAN}{Style.BRIGHT}{char.name}{Style.RESET_ALL}"
    )
    info_line = get_string(
        strings,
        "choose_character.info_line",
        race=f"{Fore.CYAN}{race_label}{Style.RESET_ALL}",
        class_name=f"{Fore.CYAN}{class_label}{Style.RESET_ALL}",
        level=f"{Fore.YELLOW}{char.level}{Style.RESET_ALL}",
        mode=f"{mode_color}{mode}{Style.RESET_ALL}",
    )
    print(f"       {info_line}")

    vitals_line = get_string(
        strings,
        "choose_character.vitals_line",
        hp=f"{Fore.GREEN}{char.current_hp}{Style.RESET_ALL}",
        xp=f"{Fore.MAGENTA}{char.experience}{Style.RESET_ALL}",
    )
    print(f"       {vitals_line}")

    stats_compact = _format_character_stats_compact(char, strings)
    if stats_compact:
        stats_line = get_string(
            strings, "choose_character.stats_line", stats=stats_compact
        )
        print(f"       {stats_line}")

    print()


def _select_character(strings: dict[str, Any]) -> SelectCharacterResult:
    """Экран выбора персонажа из списка сохранённых."""
    characters = load_characters()

    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'choose_character.caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()
    print(
        f"  {Fore.YELLOW}{Style.BRIGHT}"
        f"{get_string(strings, 'choose_character.list_header')}"
        f"{Style.RESET_ALL}"
    )
    print()

    for idx, char in enumerate(characters, 1):
        _print_character_card(idx, char, strings)

    create_idx = len(characters) + 1
    print()
    print(
        f"  {Fore.YELLOW}{create_idx}{Style.RESET_ALL}."
        f" {Fore.GREEN}{get_string(strings, 'choose_character.create_new')}"
        f"{Style.RESET_ALL}"
    )
    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {Fore.LIGHTBLACK_EX}{get_string(strings, 'choose_character.back')}"
        f"{Style.RESET_ALL}"
    )
    print()
    choice = get_int_input(
        get_string(strings, "choose_character.prompt", count=create_idx),
        0,
        create_idx,
        strings,
    )

    if choice == 0:
        return None
    if choice == create_idx:
        return "create"

    return characters[choice - 1]


def _select_adventure(
    strings: dict[str, Any],
    language: str,
    character: Character,
) -> Adventure | None:
    """Экран выбора приключения с учётом сложности персонажа."""
    adventures: list[Adventure] = load_adventures()

    if not adventures:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'adventures.no_adventures')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return None

    matching = [
        adv
        for adv in adventures
        if adventure_allows_difficulty(adv, character.difficulty)
    ]
    other = [
        adv
        for adv in adventures
        if not adventure_allows_difficulty(adv, character.difficulty)
    ]

    if not matching:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'adventures.none_for_difficulty')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return None

    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'adventures.caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()

    for idx, adv in enumerate(matching, 1):
        line = get_string(
            strings,
            "adventures.adventure_line",
            name=adv.get_name(language),
            difficulty=adv.difficulty,
            desc=adv.description,
        )
        print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {line}")

    if other:
        print()
        print(
            f"{Fore.LIGHTBLACK_EX}"
            f"{get_string(strings, 'adventures.unavailable_header')}"
            f"{Style.RESET_ALL}"
        )
        for adv in other:
            line = get_string(
                strings,
                "adventures.unavailable_line",
                name=adv.get_name(language),
                difficulty=adv.difficulty,
                desc=adv.description,
            )
            print(f"  {Fore.LIGHTBLACK_EX}— {line}{Style.RESET_ALL}")

    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'adventures.back')}"
    )
    print()
    choice = get_int_input(
        get_string(strings, "adventures.prompt", count=len(matching)),
        0,
        len(matching),
        strings,
    )

    if choice == 0:
        return None

    return matching[choice - 1]


def show_new_game_flow(
    strings: dict[str, Any], settings: dict[str, Any]
) -> None:
    """Flow «Новая игра»: персонаж → приключение."""
    language = settings.get("language", "ru")

    while True:
        characters = load_characters()
        if not characters:
            character = show_create_character_flow(strings, settings)
        else:
            result = _select_character(strings)
            if result is None:
                return
            if result == "create":
                character = show_create_character_flow(strings, settings)
            else:
                character = result

        if character is None:
            return

        while True:
            adventure = _select_adventure(strings, language, character)
            if adventure is None:
                break

            print()
            launch_msg = get_string(
                strings,
                "new_game.launch",
                adventure=adventure.get_name(language),
                name=character.name,
                difficulty=character.difficulty,
            )
            print(f"{Fore.GREEN}{launch_msg}{Style.RESET_ALL}")
            print()
            _press_enter(strings)
            return


def _print_race_info(info: dict[str, Any], strings: dict[str, Any]) -> None:
    """Вывести подробности расы или подрасы."""
    desc = info.get("description", "")
    if desc:
        print(get_string(strings, "character.race_description", desc=desc))

    speed = info.get("speed")
    if speed:
        print(get_string(strings, "character.speed_label", speed=speed))

    languages = info.get("languages", [])
    if languages:
        language_line = ", ".join(str(lang) for lang in languages)
        print(
            get_string(
                strings, "character.languages_label", langs=language_line
            )
        )

    bonuses = info.get("ability_bonuses", {})
    if bonuses:
        bonus_parts = []
        for stat, val in bonuses.items():
            stat_ru = _ability_name(strings, stat)
            bonus_parts.append(
                f"{Fore.CYAN}{stat_ru}{Style.RESET_ALL}"
                f"+{Fore.GREEN}{val}{Style.RESET_ALL}"
            )
        bonuses_str = ", ".join(bonus_parts)
        print(
            get_string(
                strings, "character.ability_bonuses_label", bonuses=bonuses_str
            )
        )

    features = info.get("features", [])
    if features:
        print(get_string(strings, "character.features_label"))
        for feat in features:
            description = feat.get("description", "")
            print(
                get_string(
                    strings,
                    "character.feature_line",
                    name=feat.get("name", ""),
                    desc=description,
                )
            )


def _select_subrace(
    strings: dict[str, Any], race_id: str
) -> tuple[bool, str | None]:
    """Показать описание расы и выбрать подрасу."""
    race_full = load_race_full(race_id)
    subraces = race_full.get("subraces", {})
    allow_base = bool(race_full.get("allow_base_race_choice", False))

    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'character.subrace_caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()

    race_name = race_full.get("name", race_id)
    print(f"{Fore.CYAN}{race_name}{Style.RESET_ALL}")
    _print_race_info(race_full, strings)
    print()

    if not subraces:
        if allow_base:
            print(get_string(strings, "character.no_subraces"))
            print()
            print(
                f"  {Fore.YELLOW}1{Style.RESET_ALL}. "
                f"{Fore.CYAN}{race_name}{Style.RESET_ALL}"
            )
            print(
                f"  {Fore.YELLOW}0{Style.RESET_ALL}."
                f" {get_string(strings, 'character.back')}"
            )
            print()
            choice = get_int_input(
                get_string(strings, "character.subrace_prompt"),
                0,
                1,
                strings,
            )
            if choice == 0:
                return False, None
            return True, None
        return False, None

    print(get_string(strings, "character.subraces_label"))
    choices: list[tuple[str | None, dict[str, Any]]] = []
    if allow_base:
        base_info = dict(race_full)
        base_info["name"] = race_full.get("base_choice_name", race_name)
        choices.append((None, base_info))

    for subrace_id, subrace_info in subraces.items():
        choices.append((str(subrace_id), subrace_info))

    for idx, (subrace_id, subrace_info) in enumerate(choices, 1):
        print()
        print(
            f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            f"{Fore.CYAN}{subrace_info.get('name', '?')}"
            f"{Style.RESET_ALL}"
        )
        if not (subrace_id is None and idx == 1):
            _print_race_info(subrace_info, strings)

    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()
    choice = get_int_input(
        get_string(strings, "character.subrace_prompt"),
        0,
        len(choices),
        strings,
    )
    if choice == 0:
        return False, None

    subrace_id, _ = choices[choice - 1]
    return True, subrace_id


def _select_class(strings: dict[str, Any]) -> dict[str, Any] | None:
    """Выбрать класс персонажа или вернуться назад."""
    classes = load_classes()
    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'character.class_prompt').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()
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
        strings,
    )
    if class_idx == 0:
        return None
    return classes[class_idx - 1]


def show_create_character_flow(
    strings: dict[str, Any],
    settings: dict[str, Any],
) -> Character | None:
    """Flow «Создать персонажа»: сложность → создание."""
    difficulty = select_difficulty(strings)
    if difficulty is None:
        return None

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
        strings=strings,
    )

    while True:
        races = load_races()
        print(SEPARATOR)
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'character.race_caption').center(78)}"
            f"{Style.RESET_ALL}"
        )
        print(SEPARATOR)
        print()

        for idx, race in enumerate(races, 1):
            print(
                f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
                f"{race.get('name', '?')}"
            )

        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'character.back')}"
        )
        print()
        choice = get_int_input(
            get_string(strings, "character.race_prompt", count=len(races)),
            0,
            len(races),
            strings,
        )
        if choice == 0:
            return None

        selected = races[choice - 1]
        race_id = str(selected.get("id") or selected.get("name"))

        while True:
            subrace_selected, subrace_id = _select_subrace(strings, race_id)
            if not subrace_selected:
                break

            while True:
                stats = show_stats_generation_flow(
                    strings, race_id, subrace_id, difficulty
                )
                if stats is None:
                    break

                cls = _select_class(strings)
                if cls is None:
                    continue

                class_id = cls.get("id") or cls.get("name")

                character = save_character(
                    name=name,
                    race_id=str(race_id),
                    class_id=str(class_id),
                    difficulty=difficulty,
                    subrace_id=str(subrace_id) if subrace_id else None,
                    stats=stats,
                )

                msg = get_string(strings, "character.save_success", name=name)
                print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
                print()
                _press_enter(strings)

                return character


def show_stats_generation_flow(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
    difficulty: str,
) -> dict[str, int] | None:
    """Flow генерации характеристик с выбором метода."""
    if difficulty == "hardcore":
        return _select_stats_random_hardcore(strings, race_id, subrace_id)

    while True:
        print(SEPARATOR)
        print(_stats_caption_line(strings))
        print(SEPARATOR)
        print()

        methods = [
            get_string(strings, "character.stats_standard_array"),
            get_string(strings, "character.stats_point_buy"),
            get_string(strings, "character.stats_random"),
        ]

        for idx, method in enumerate(methods, 1):
            print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {method}")
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'character.back')}"
        )
        print()

        choice = get_int_input(
            get_string(strings, "character.stats_generation_method_prompt"),
            0,
            3,
            strings,
        )

        if choice == 0:
            return None

        stats: dict[str, int] | None = None
        if choice == 1:
            stats = _select_stats_standard_array(strings, race_id, subrace_id)
        elif choice == 2:
            stats = _select_stats_point_buy(strings, race_id, subrace_id)
        elif choice == 3:
            stats = _select_stats_random_normal(strings, race_id, subrace_id)

        if stats is not None:
            return stats


def _select_stats_standard_array(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
) -> dict[str, int] | None:
    """Выбор характеристик из стандартного массива."""
    show_bonuses = True

    while True:
        selected = _assign_stats_from_pool(
            strings,
            list(STANDARD_ARRAY),
            entry_mode="manual",
            race_id=race_id,
            subrace_id=subrace_id,
            show_race_bonuses=show_bonuses,
        )
        show_bonuses = False
        if selected is None:
            return None

        selected_values = [selected[stat] for stat in STAT_NAMES]
        stats = generate_stats_standard_array(
            selected_values, race_id, subrace_id
        )
        result = _confirm_stats(
            strings,
            stats,
            race_id,
            subrace_id,
            reroll_label_key="character.stats_reroll_redistribute",
        )
        if result == "accept":
            return stats
        if result == "back":
            return None


def _select_stats_point_buy(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
) -> dict[str, int] | None:
    """Система покупки очков (Point-buy)."""
    show_bonuses = True

    while True:
        print_race_bonuses = show_bonuses
        show_bonuses = False

        stats = {stat: 8 for stat in STAT_NAMES}

        while True:
            print(SEPARATOR)
            print(_stats_caption_line(strings))
            print(SEPARATOR)
            print()

            if print_race_bonuses:
                _print_race_bonuses(strings, race_id, subrace_id)
                print()
                print_race_bonuses = False

            total_cost = point_buy_total_cost(
                [stats[stat] for stat in STAT_NAMES]
            )
            points_available = POINT_BUY_BUDGET - total_cost

            points_msg = get_string(
                strings,
                "character.stats_points_available",
                available=points_available,
                total=POINT_BUY_BUDGET,
            )
            print(f"{Fore.CYAN}{points_msg}{Style.RESET_ALL}")
            print()
            print(
                f"{Fore.YELLOW}"
                f"{get_string(strings, 'character.stats_current')}"
                f"{Style.RESET_ALL}"
            )

            for idx, stat in enumerate(STAT_NAMES, 1):
                stat_name = _ability_name(strings, stat)
                cost = POINT_BUY_COSTS[stats[stat]]
                cost_msg = get_string(
                    strings, "character.stats_cost_points", cost=cost
                )
                print(
                    f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {stat_name}: "
                    f"{Fore.CYAN}{stats[stat]}{Style.RESET_ALL} {cost_msg}"
                )

            print()
            print(
                f"{Fore.GREEN}"
                f"{get_string(strings, 'character.stats_commands')}"
                f"{Style.RESET_ALL}"
            )
            choose_increase = get_string(
                strings, "character.stats_choose_stat_increase"
            )
            print(
                f"  {Fore.YELLOW}1-6{Style.RESET_ALL}. " f"{choose_increase}"
            )
            print(
                f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
                f"{get_string(strings, 'character.stats_finish_distribution')}"
            )
            print()

            choice = get_int_input(_choice_prompt(strings), 0, 6, strings)

            if choice == 0:
                if points_available >= 0:
                    stats_result = generate_stats_point_buy(
                        [stats[stat] for stat in STAT_NAMES],
                        race_id,
                        subrace_id,
                    )
                    result = _confirm_stats(
                        strings,
                        stats_result,
                        race_id,
                        subrace_id,
                        reroll_label_key="character.stats_reroll_redistribute",
                    )
                    if result == "accept":
                        return stats_result
                    if result == "back":
                        return None
                    break
                overspent = get_string(
                    strings, "character.stats_points_overspent"
                )
                print(f"{Fore.RED}{overspent}{Style.RESET_ALL}")
                _press_enter(strings)
                continue

            stat_to_modify = STAT_NAMES[choice - 1]
            stat_name = _ability_name(strings, stat_to_modify)
            _prompt_point_buy_stat_value(
                strings, stat_name, stats, stat_to_modify
            )


def _select_stats_random_normal(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
) -> dict[str, int] | None:
    """Случайный метод для Normal режима с распределением значений."""
    show_bonuses = True

    while True:
        print(SEPARATOR)
        print(_stats_caption_line(strings))
        print(SEPARATOR)
        print()

        if show_bonuses:
            _print_race_bonuses(strings, race_id, subrace_id)
            print()
            show_bonuses = False

        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'character.stats_generating_random')}"
            f"{Style.RESET_ALL}"
        )
        print()

        rolls = [roll_ability_score() for _ in range(6)]
        rolls.sort(reverse=True)

        print(
            f"{Fore.CYAN}"
            f"{get_string(strings, 'character.stats_random_rolls')}"
            f"{Style.RESET_ALL}"
        )
        rolls_display = get_string(
            strings,
            "character.stats_available",
            values=rolls,
        )
        print(f"  {rolls_display}")
        print()
        print(
            f"  {Fore.YELLOW}1{Style.RESET_ALL}. "
            f"{get_string(strings, 'character.stats_random_accept')}"
        )
        print(
            f"  {Fore.YELLOW}2{Style.RESET_ALL}. "
            f"{get_string(strings, 'character.stats_random_regenerate')}"
        )
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
            f"{get_string(strings, 'character.back')}"
        )
        print()

        roll_choice = get_int_input(_choice_prompt(strings), 0, 2, strings)
        if roll_choice == 0:
            return None
        if roll_choice == 2:
            continue

        selected = _assign_stats_from_pool(strings, rolls, show_counts=True)
        if selected is None:
            continue

        selected_values = [selected[stat] for stat in STAT_NAMES]
        stats = generate_stats_random(selected_values, race_id, subrace_id)
        result = _confirm_stats(
            strings,
            stats,
            race_id,
            subrace_id,
            reroll_label_key="character.stats_reroll_regenerate",
        )
        if result == "accept":
            return stats
        if result == "back":
            return None


def _select_stats_random_hardcore(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
) -> dict[str, int]:
    """Случайный метод для HardCore режима."""
    race_bonuses = get_race_bonuses(race_id, subrace_id)

    print(SEPARATOR)
    print(_stats_caption_line(strings))
    print(SEPARATOR)
    print()
    _print_race_bonuses(strings, race_id, subrace_id)
    print()
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'character.stats_hardcore_auto')}"
        f"{Style.RESET_ALL}"
    )
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'character.stats_hardcore_method')}"
        f"{Style.RESET_ALL}"
    )
    print()

    base_values: list[int] = []
    for stat in STAT_NAMES:
        roll = roll_ability_score()
        base_values.append(roll)
        stat_name = _ability_name(strings, stat)
        print(f"  {stat_name}: {Fore.YELLOW}{roll}{Style.RESET_ALL}")

    print()
    _press_enter(strings)

    stats = generate_stats_random(base_values, race_id, subrace_id)

    print(SEPARATOR)
    print(_stats_total_line(strings))
    print(SEPARATOR)
    print()

    for stat in STAT_NAMES:
        _print_final_stat_line(strings, stat, stats[stat], race_bonuses)

    print()
    _press_enter(strings)

    return stats


def _confirm_stats(
    strings: dict[str, Any],
    stats: dict[str, int],
    race_id: str,
    subrace_id: str | None,
    *,
    reroll_label_key: str,
) -> ConfirmStatsResult:
    """Подтверждение выбранных характеристик."""
    race_bonuses = get_race_bonuses(race_id, subrace_id)

    print(SEPARATOR)
    print(_stats_total_line(strings))
    print(SEPARATOR)
    print()

    for stat in STAT_NAMES:
        _print_final_stat_line(
            strings, stat, stats.get(stat, 10), race_bonuses
        )

    print()
    print(
        f"  {Fore.YELLOW}1{Style.RESET_ALL}. "
        f"{get_string(strings, 'character.stats_confirm')}"
    )
    print(
        f"  {Fore.YELLOW}2{Style.RESET_ALL}. "
        f"{get_string(strings, reroll_label_key)}"
    )
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()

    choice = get_int_input(_choice_prompt(strings), 0, 2, strings)

    if choice == 0:
        return "back"
    if choice == 2:
        return "reroll"
    return "accept"


def _print_race_bonuses(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
) -> None:
    """Вывести блок расовых бонусов."""
    bonuses = get_race_bonuses(race_id, subrace_id)
    print(_format_bonuses(bonuses, strings))


def _print_final_stat_line(
    strings: dict[str, Any],
    stat: str,
    value: int,
    race_bonuses: dict[str, int],
) -> None:
    """Вывести итоговую характеристику с пометкой расового бонуса (+N)."""
    stat_name = _ability_name(strings, stat)
    bonus = race_bonuses.get(stat, 0)
    if bonus > 0:
        print(
            f"  {stat_name}: {Fore.YELLOW}{value}{Style.RESET_ALL} "
            f"{Fore.GREEN}(+{bonus}){Style.RESET_ALL}"
        )
        return
    print(f"  {stat_name}: {Fore.YELLOW}{value}{Style.RESET_ALL}")


def _format_bonuses(bonuses: dict[str, int], strings: dict[str, Any]) -> str:
    """Отформатировать расовые бонусы для отображения."""
    if not bonuses:
        return (
            f"{Fore.CYAN}"
            f"{get_string(strings, 'character.stats_no_bonuses')}"
            f"{Style.RESET_ALL}"
        )

    bonus_strs = []
    for stat, bonus in bonuses.items():
        stat_name = _ability_name(strings, stat)
        bonus_strs.append(
            get_string(
                strings,
                "character.stats_bonus_format",
                stat=stat_name,
                bonus=bonus,
            )
        )

    bonus_line = ", ".join(bonus_strs)
    race_msg = get_string(
        strings, "character.stats_race_bonuses", bonuses=bonus_line
    )
    return f"{Fore.CYAN}{race_msg}{Style.RESET_ALL}"


def show_load_game_flow(strings: dict[str, Any]) -> None:
    """Flow «Загрузить игру»."""
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
    _press_enter(strings)


def show_languages_menu(
    strings: dict[str, Any], settings: dict[str, Any]
) -> dict[str, Any]:
    """Меню выбора языка."""

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

        lang_codes = ["en", "ru"] if current == "ru" else ["ru", "en"]
        options = [
            get_string(strings, f"languages.lang_{code}")
            for code in lang_codes
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
            strings,
        )

        if choice == 0:
            break

        new_lang = lang_codes[choice - 1]
        settings["language"] = new_lang
        strings = load_strings(new_lang)
        msg = get_string(
            strings,
            "languages.changed",
            name=get_string(strings, f"languages.lang_{new_lang}"),
        )
        print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
        print()
        _press_enter(strings)

    return settings


def show_settings(
    strings: dict[str, Any], settings: dict[str, Any]
) -> dict[str, Any]:
    """Экран настроек."""

    while True:
        print(SEPARATOR)
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'settings.caption').center(78)}"
            f"{Style.RESET_ALL}"
        )
        print(SEPARATOR)
        print()
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'settings.back')}"
        )
        print()

        choice = get_int_input(
            get_string(strings, "settings.prompt", count=0),
            0,
            0,
            strings,
        )

        if choice == 0:
            break

    return settings
