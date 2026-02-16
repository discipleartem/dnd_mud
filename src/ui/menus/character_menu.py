"""
Меню создания персонажа D&D MUD.

Реализует пошаговое создание персонажа с выбором расы, класса
и генерацией характеристик.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List

from src.core.entities.character import Character 
from src.core.entities.race import Race
from src.core.entities.class_ import CharacterClass
from src.ui.renderer import renderer 


class CharacterMenu:
    """Меню создания персонажа."""
    
    def __init__(self) -> None:
        """Инициализация меню."""
        self.character: Optional[Character] = None
        self.current_step: int = 0
        self.max_steps: int = 5
    
    def show(self) -> None:
        """Отображает текущее меню."""
        renderer.clear_screen()
        
        title = "=== СОЗДАНИЕ ПЕРСОНАЖА ==="
        renderer.show_title(title)
        
        steps = [
            "1. Ввести имя персонажа",
            "2. Выбрать расу",
            "3. Выбрать класс",
            "4. Сгенерировать характеристики",
            "5. Подтвердить создание",
            "6. Назад"
        ]
        
        for i, step in enumerate(steps, 1):
            status = "✓" if i < self.current_step else " "
            renderer.show_text(f"{status} {i}. {step}")
        
        renderer.show_text("\n")
    
    def get_choice(self, prompt: str, max_choice: int) -> int:
        """Получает выбор пользователя."""
        while True:
            try:
                choice = input(f"{prompt} (1-{max_choice}): ")
                choice = int(choice)
                
                if 1 <= choice <= max_choice:
                    return choice
                else:
                    renderer.show_error("Неверный выбор. Попробуйте снова.")
            except ValueError:
                renderer.show_error("Пожалуйста, введите число.")
            except KeyboardInterrupt:
                renderer.show_info("Возврат в главное меню.")
                return -1
    
    def input_name(self) -> str:
        """Ввод имени персонажа."""
        renderer.clear_screen()
        renderer.show_title("=== ВВЕДИТЕ ИМЯ ПЕРСОНАЖА ===")
        renderer.show_text("Имя персонажа (оставьте пустым для случайного имени):")
        
        name = input_handler.get_text_input("> ")
        
        if not name.strip():
            import random
            names = ["Артас", "Лиана", "Гэндальф", "Тирион", "Фродо"]
            name = random.choice(names)
            renderer.show_text(f"Сгенерировано имя: {name}")
        
        renderer.show_text("\n")
        return name
    
    def show_race_selection(self) -> Optional[Dict[str, Any]]:
        """Показывает меню выбора расы.
        
        Returns:
            Словарь с информацией о выбранной расе или None
        """
        from ...core.entities.race_factory import RaceFactory
        
        renderer.clear_screen()
        renderer.show_title("=== ВЫБОР РАСЫ ===")
        
        # Получаем все расы из фабрики
        races = RaceFactory.get_all_races()
        race_choices = RaceFactory.get_race_choices()
        
        # Отображаем расы
        for choice_num, race_name in race_choices.items():
            if choice_num != "0":
                renderer.show_text(f"{choice_num}. {race_name}")
        
        renderer.show_text("0. Назад")
        renderer.show_text("\nВведите номер расы:")
        
        choice = input()
        
        if choice == "0":
            return None
        
        if choice in race_choices:
            race_name = race_choices[choice]
            
            # Находим объект расы
            selected_race = None
            for r in races:
                if r.name == race_name:
                    selected_race = r
                    break
                # Проверяем подрасы
                for subrace in r.subraces.values():
                    if subrace.name == race_name:
                        selected_race = subrace
                        break
                if selected_race:
                    break
            
            if selected_race:
                result = {'race': selected_race}
                
                # Если это человек и есть альтернативные особенности
                if selected_race.name == "Человек" and selected_race.has_alternative_features():
                    alternative_choice = self.show_alternative_features_selection(selected_race)
                    if alternative_choice:
                        result['alternative_choices'] = alternative_choice
                
                return result
        else:
            renderer.show_error("Неверный выбор.")
            return None
    
    def show_alternative_features_selection(self, race: 'Race') -> Optional[Dict[str, Any]]:
        """Показывает меню выбора альтернативных особенностей для людей.
        
        Args:
            race: Объект расы Человек
            
        Returns:
            Словарь с выбранными альтернативными опциями или None
        """
        renderer.clear_screen()
        renderer.show_title("=== АЛЬТЕРНАТИВНЫЕ ОСОБЕННОСТИ ЛЮДЕЙ ===")
        
        renderer.show_text(race.alternative_features.get('description', ''))
        renderer.show_text("\nВыберите альтернативную особенность:")
        
        options = race.get_alternative_options()
        choice_map = {}
        
        for i, (key, option) in enumerate(options.items(), 1):
            choice_map[str(i)] = key
            renderer.show_text(f"{i}. {option['name']}")
            renderer.show_text(f"   {option['description']}")
            renderer.show_text("")
        
        renderer.show_text(f"{len(options) + 1}. Стандартные бонусы (+1 ко всем характеристикам)")
        renderer.show_text("0. Назад")
        renderer.show_text("\nВведите номер:")
        
        choice = input()
        
        if choice == "0":
            return None
        
        if choice == str(len(options) + 1):
            # Стандартные бонусы
            return None
        
        if choice in choice_map:
            selected_key = choice_map[choice]
            selected_option = options[selected_key]
            
            if selected_option['type'] == 'ability_bonus':
                return self.show_ability_bonus_selection(selected_option)
            elif selected_option['type'] == 'skill':
                return self.show_skill_selection(selected_option)
            elif selected_option['type'] == 'feat':
                return self.show_feat_selection(selected_option)
        
        renderer.show_error("Неверный выбор.")
        return None
    
    def show_ability_bonus_selection(self, option: Dict[str, Any]) -> Dict[str, Any]:
        """Показывает выбор увеличения характеристик."""
        renderer.clear_screen()
        renderer.show_title("=== УВЕЛИЧЕНИЕ ХАРАКТЕРИСТИК ===")
        
        renderer.show_text(option['description'])
        renderer.show_text(f"\nВыберите {option['max_choices']} характеристики:")
        
        attributes = option['allowed_attributes']
        attr_names = {
            'strength': 'СИЛ',
            'dexterity': 'ЛОВ', 
            'constitution': 'ТЕЛ',
            'intelligence': 'ИНТ',
            'wisdom': 'МДР',
            'charisma': 'ХАР'
        }
        
        for i, attr in enumerate(attributes, 1):
            renderer.show_text(f"{i}. {attr_names[attr]} ({attr})")
        
        renderer.show_text("\nВведите номера через пробел:")
        
        choice = input()
        chosen_indices = [int(x.strip()) - 1 for x in choice.split() if x.strip().isdigit()]
        
        if len(chosen_indices) != option['max_choices']:
            renderer.show_error(f"Нужно выбрать ровно {option['max_choices']} характеристики!")
            return self.show_ability_bonus_selection(option)
        
        chosen_attrs = []
        for idx in chosen_indices:
            if 0 <= idx < len(attributes):
                chosen_attrs.append(attributes[idx])
        
        return {'ability_scores': chosen_attrs}
    
    def show_skill_selection(self, option: Dict[str, Any]) -> Dict[str, Any]:
        """Показывает выбор навыка (заглушка)."""
        renderer.clear_screen()
        renderer.show_title("=== ВЛАДЕНИЕ НАВЫКОМ ===")
        
        renderer.show_text(option['description'])
        renderer.show_text("\nВ разработке - будет доступно в следующей версии")
        renderer.show_text("\nНажмите Enter для продолжения...")
        input()
        
        return {'skill': 'athletics'}  # Временная заглушка
    
    def show_feat_selection(self, option: Dict[str, Any]) -> Dict[str, Any]:
        """Показывает выбор черты (заглушка)."""
        renderer.clear_screen()
        renderer.show_title("=== ЧЕРТА ===")
        
        renderer.show_text(option['description'])
        renderer.show_text("\nВ разработке - будет доступно в следующей версии")
        renderer.show_text("\nНажмите Enter для продолжения...")
        input()
        
        return {'feat': 'heavily_armored'}  # Временная заглушка
    
    def select_class(self) -> str:
        """Выбор класса персонажа."""
        renderer.clear_screen()
        renderer.show_title("=== ВЫБОР КЛАССА ===")
        
        # Временные данные классов до создания YAML
        classes = {
            "Воин": CharacterClass.from_dict({
                'name': 'Воин',
                'description': 'Мастер боевых искусств',
                'bonuses': {'strength': 1, 'constitution': 1},
                'hit_die': 'd10'
            }),
            "Волшебник": CharacterClass.from_dict({
                'name': 'Волшебник',
                'description': 'Маг могущественных заклинаний',
                'bonuses': {'intelligence': 1, 'wisdom': 1},
                'hit_die': 'd6'
            }),
            "Плут": CharacterClass.from_dict({
                'name': 'Плут',
                'description': 'Мастер скрытности и ловкости',
                'bonuses': {'dexterity': 1, 'charisma': 1},
                'hit_die': 'd8'
            })
        }
        
        for i, (class_name, character_class) in enumerate(classes.items(), 1):
            renderer.show_text(f"{i}. {class_name}")
            renderer.show_text(f"   {character_class.description}")
        
        choice = self.get_choice("Выберите класс", len(classes))
        
        class_list = list(classes.keys())
        if 1 <= choice <= len(class_list):
            selected_class = class_list[choice - 1]
            
            renderer.show_text(f"\nВыбран класс: {selected_class}")
            renderer.show_text("")
            
            return selected_class
        
        renderer.show_error("Выбор отменен.")
        return None
    
    def generate_attributes(self) -> Dict[str, int]:
        """Генерирует характеристики для персонажа."""
        from ...core.mechanics.attributes import StandardAttributes
        
        # Стандартный набор (15, 14, 13, 12, 10, 8)
        attributes = {
            'strength': 15,
            'dexterity': 14,
            'constitution': 13,
            'intelligence': 12,
            'wisdom': 10,
            'charisma': 8
        }
        
        # Перемешиваем для случайного распределения
        import random
        attr_names = list(attributes.keys())
        random.shuffle(attr_names)
        
        for i, attr_name in enumerate(attr_names):
            attributes[attr_names[i]] = attributes[attr_name]
        
        return attributes
    
    def apply_bonuses(self, attributes: Dict[str, int], race_info: Dict[str, Any], class_name: str) -> Dict[str, int]:
        """Применяет расовые и классовые бонусы к характеристикам."""
        from ...core.entities.race_factory import RaceFactory
        
        race = race_info['race']
        alternative_choices = race_info.get('alternative_choices')
        
        # Применяем расовые бонусы
        if alternative_choices:
            # Альтернативные бонусы для людей
            attributes = race.apply_alternative_bonuses(attributes, alternative_choices)
        else:
            # Стандартные расовые бонусы
            attributes = race.apply_bonuses(attributes)
        
        # Временные данные классов до создания YAML
        classes_data = {
            "Воин": {'bonuses': {'strength': 1, 'constitution': 1}},
            "Волшебник": {'bonuses': {'intelligence': 1, 'wisdom': 1}},
            "Плут": {'bonuses': {'dexterity': 1, 'charisma': 1}}
        }
        
        # Применяем классовые бонусы
        class_data = classes_data.get(class_name, {})
        for attr, bonus in class_data.get('bonuses', {}).items():
            if attr in attributes:
                attributes[attr] += bonus
        
        return attributes
    
    def show_preview(self, character: Character) -> None:
        """Показывает предпросмотр персонажа."""
        renderer.clear_screen()
        renderer.show_title("=== ПРЕДПРОСМОТР ПЕРСОНАЖА ===")
        
        renderer.show_text(f"Имя: {character.name}")
        renderer.show_text(f"Раса: {character.race.localized_name}")
        renderer.show_text(f"Класс: {character.character_class}")
        renderer.show_text(f"Уровень: {character.level}")
        
        renderer.show_text("\nХарактеристики:")
        renderer.show_text(f"  СИЛ: {character.strength.value} ({character.get_ability_modifier(character.strength.value):+d})")
        renderer.show_text(f"  ЛОВ: {character.dexterity.value} ({character.get_ability_modifier(character.dexterity.value):+d})")
        renderer.show_text(f"  ТЕЛ: {character.constitution.value} ({character.get_ability_modifier(character.constitution.value):+d})")
        renderer.show_text(f"  ИНТ: {character.intelligence.value} ({character.get_ability_modifier(character.intelligence.value):+d})")
        renderer.show_text(f"  МДР: {character.wisdom.value} ({character.get_ability_modifier(character.wisdom.value):+d})")
        renderer.show_text(f"  ХАР: {character.charisma.value} ({character.get_ability_modifier(character.charisma.value):+d})")
        
        renderer.show_text(f"\nПроизводные:")
        renderer.show_text(f"  HP: {character.hp_current}/{character.hp_max}")
        renderer.show_text(f"  AC: {character.ac}")
        renderer.show_text(f"  Золото: {character.gold}")
        
        renderer.show_text("\n")
    
    def create_character(self) -> Optional[Character]:
        """Создает персонажа."""
        from ...core.entities.race_factory import RaceFactory
        
        # Шаг 1: Ввод имени
        name = self.input_name()
        if not name:
            return None
        
        # Шаг 2: Выбор расы
        race_info = self.show_race_selection()
        if not race_info:
            return None
        
        # Шаг 3: Выбор класса
        class_name = self.select_class()
        if not class_name:
            return None
        
        # Шаг 4: Генерация характеристик
        attributes = self.generate_attributes()
        
        # Шаг 5: Применение бонусов
        final_attributes = self.apply_bonuses(attributes, race_info, class_name)
        
        # Получаем объект расы
        race = race_info['race']
        
        # Создаем персонажа
        character = Character(
            name=name,
            race=race,
            character_class=class_name,
            level=1,
            **final_attributes
        )
        
        # Шаг 6: Предпросмотр
        self.show_preview(character)
        
        # Шаг 7: Подтверждение
        renderer.clear_screen()
        renderer.show_title("=== ПОДТВЕРЖДЕНИЕ СОЗДАНИЯ ===")
        renderer.show_text("Сохранить персонажа?")
        renderer.show_text("1. Да")
        renderer.show_text("2. Нет (ввести заново)")
        renderer.show_text("3. В главное меню")
        
        choice = self.get_choice("Ваш выбор", 3)
        
        if choice == 1:
            # Сохраняем персонажа
            self.character = character
            renderer.show_success("Персонаж сохранен!")
            return character
        elif choice == 2:
            # Повторяем создание
            return self.create_character()
        elif choice == 3:
            # Возврат в главное меню
            return None
        
        return None
    
    def run(self) -> Optional[Character]:
        """Запускает меню создания персонажа."""
        renderer.show_info("=== МЕНЮ СОЗДАНИЯ ПЕРСОНАЖА ===")
        
        while True:
            character = self.create_character()
            if character is None:
                break
            
            return character