from typing import Optional
from src.ui.entities.race import Race, SubRace
from src.ui.entities.character import Character
from src.ui.main_menu.ability_generation import generate_ability_scores

# Импорт локализации
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from i18n import t


def get_character_name() -> str:
    """Получить и валидировать имя персонажа."""
    while True:
        name = input(t('new_game.character_name.prompt')).strip()
        if not name:
            print(t('new_game.character_name.error_empty'))
            continue
        if len(name) < 2:
            print(t('new_game.character_name.error_too_short'))
            continue
        if len(name) > 15:
            print(t('new_game.character_name.error_too_long'))
            continue
        return name


def display_races(races: dict) -> None:
    """Отобразить список доступных рас."""
    print(f"\n{t('new_game.race_selection.title')}")
    print("=" * 40)
    for i, (race_id, race) in enumerate(races.items(), 1):
        print(f"{i}. {race.name}")
        if race.ability_bonuses_description:
            print(f"   🎯 {race.ability_bonuses_description}")
        print()


def select_race(races: dict) -> Race:
    """Выбрать расу из списка."""
    while True:
        try:
            choice = input(t('new_game.race_selection.prompt')).strip()
            
            # Попытка выбора по номеру
            if choice.isdigit():
                race_index = int(choice) - 1
                race_list = list(races.values())
                if 0 <= race_index < len(race_list):
                    return race_list[race_index]
                else:
                    print(t('new_game.race_selection.error_number'))
                    continue
            
            # Попытка выбора по названию
            selected_race = Race.get_race_by_name(choice)
            if selected_race:
                return selected_race
            else:
                print(t('new_game.race_selection.error_not_found'))
                
        except ValueError:
            print(t('new_game.race_selection.error_invalid'))


def display_race_details(race: Race) -> None:
    """Отобразить подробную информацию о расе."""
    title = t('new_game.race_details.title', race_name=race.name)
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
            print(f"   • {feature.name}")
            print(f"     {feature.description}")
    
    print(f"\n{t('new_game.race_details.other_stats_label')}")
    print(f"   {t('new_game.race_details.size_label')} {race.size.get_localized_name()}")
    print(f"   {t('new_game.race_details.speed_label')} {race.speed} {t('new_game.race_details.speed_unit')}")
    print(f"   {t('new_game.race_details.languages_label')} {race.get_languages_display()}")


def select_subrace(race: Race) -> Optional[SubRace]:
    """Универсально выбрать подрасу для любой расы."""
    if not race.subraces:
        return None
    
    title = t('new_game.subrace_selection.title', race_name=race.name)
    print(f"\n{title}")
    print("=" * 40)
    
    # Создаём список опций выбора
    options = []
    
    # Добавляем основную расу как вариант выбора только если разрешено
    if race.allow_base_race_choice:
        base_option = t('new_game.subrace_selection.base_race_option', race_name=race.name)
        options.append((base_option, None, "👤"))
        print(f"1. 👤 {base_option}")
        start_number = 2
    else:
        start_number = 1
    
    # Добавляем доступные подрасы
    subrace_list = list(race.subraces.values())
    for i, subrace in enumerate(subrace_list, start_number):
        emoji = _get_subrace_emoji(subrace.name)
        options.append((subrace.name, subrace, emoji))
        print(f"{i}. {emoji} {subrace.name}")
    
    # Показываем подробности о всех опциях
    details_title = t('new_game.details_section.title')
    print(f"\n{details_title}")
    print("-" * 40)
    
    # Детали базовой расы (только если разрешено выбирать)
    if race.allow_base_race_choice:
        base_option = t('new_game.subrace_selection.base_race_option', race_name=race.name)
        base_desc = t('new_game.subrace_selection.base_race_description', race_name=race.name)
        print(f"\n1. 👤 {base_option}")
        print(f"   {base_desc}")
        if race.ability_bonuses_description:
            abilities_label = t('new_game.details_section.abilities_label')
            print(f"   {abilities_label} {race.ability_bonuses_description}")
        if race.features:
            features_label = t('new_game.details_section.features_label')
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
            abilities_label = t('new_game.details_section.abilities_label')
            print(f"   {abilities_label} {subrace.ability_bonuses_description}")
        
        if subrace.features:
            features_label = t('new_game.details_section.features_label')
            print(f"   {features_label}")
            for feature in subrace.features:
                feature_emoji = _get_feature_emoji(feature.name)
                print(f"      • {feature_emoji} {feature.name}")
                print(f"        {feature.description}")
    
    # Цикл выбора
    while True:
        try:
            prompt = t('new_game.subrace_selection.prompt', race_name=race.name)
            choice = input(f"\n{prompt}").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(options):
                    selected_option = options[choice_num - 1]
                    return selected_option[1]  # Возвращаем SubRace или None
                else:
                    print(t('new_game.subrace_selection.error_number'))
            else:
                print(t('new_game.subrace_selection.error_invalid'))
                
        except ValueError:
            print(t('new_game.subrace_selection.error_invalid'))


def _get_subrace_emoji(subrace_name: str) -> str:
    """Получить эмодзи для подрасы на основе названия."""
    return "⚡"


def _get_feature_emoji(feature_name: str) -> str:
    """Получить эмодзи для особенности на основе названия."""
    return "⚡"


def new_game():
    """Новая игра."""
    print(t('new_game.title'))
    print(t('new_game.subtitle'))

    # 1. Присвоить имя персонажа
    character = Character()
    character.name = get_character_name()
    success_msg = t('new_game.character_name.success', name=character.name)
    print(success_msg)

    # 2. Получить список рас
    races = Race.get_all_races()
    
    # 3. Выбор из доступных рас
    display_races(races)
    selected_race = select_race(races)
    character.race = selected_race
    race_success = t('new_game.race_selection.success', race=selected_race.name)
    print(race_success)
    
    # Показываем подробную информацию о расе
    display_race_details(selected_race)

    # 4. Выбор подрасы, если есть
    selected_subrace = select_subrace(selected_race)
    if selected_subrace:
        character.subrace = selected_subrace
        subrace_success = t('new_game.subrace_selection.success', subrace=selected_subrace.name)
        print(subrace_success)
    else:
        print(t('new_game.subrace_selection.not_selected'))

    # 5. Генерация характеристик
    print(f"\n{'='*50}")
    print(f"🎲 {t('ability_generation.title')} 🎲")
    print(f"{'='*50}")
    
    # TODO: Добавить проверку на hardcore режим из настроек
    hardcore_mode = False  # Временно выключен
    
    character.ability_scores = generate_ability_scores(
        selected_race, 
        selected_subrace, 
        hardcore_mode
    )
    
    print(f"\n✅ {t('ability_generation.final.title')}")
    print(f"📊 {t('ability_generation.final.completed')}")
    
    return character
    
 