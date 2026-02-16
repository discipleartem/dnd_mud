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
    
    def show_race_selection(self) -> Optional[str]:
        """Показывает меню выбора расы.
        
        Returns:
            Название выбранной расы или None
        """
        renderer.clear_screen()
        renderer.show_title("=== ВЫБОР РАСЫ ===")
        
        # Временные данные рас до создания YAML
        races = {
            "Человек": Race.from_dict({
                'name': 'Человек',
                'description': 'Универсальная раса',
                'bonuses': {'strength': 1, 'dexterity': 1, 'constitution': 1, 'intelligence': 1, 'wisdom': 1, 'charisma': 1}
            }),
            "Высокий эльф": Race.from_dict({
                'name': 'Высокий эльф',
                'description': 'Грациозный эльф с магическими способностями',
                'bonuses': {'dexterity': 2, 'intelligence': 1}
            }),
            "Лесной эльф": Race.from_dict({
                'name': 'Лесной эльф',
                'description': 'Эльф, связанный с природой',
                'bonuses': {'dexterity': 2, 'wisdom': 1}
            }),
            "Полуорк": Race.from_dict({
                'name': 'Полуорк',
                'description': 'Сильный и выносливый воин',
                'bonuses': {'strength': 2, 'constitution': 1}
            })
        }
        
        for i, (race_name, race) in enumerate(races.items(), 1):
            renderer.show_text(f"{i}. {race.name}")
        
        renderer.show_text("0. Назад")
        renderer.show_text("\nВведите номер расы:")
        
        choice = input()
        
        if choice == "0":
            return None
        
        try:
            race_index = int(choice) - 1
            race_names = list(races.keys())
            
            if 0 <= race_index < len(race_names):
                return race_names[race_index]
            else:
                renderer.show_error("Неверный выбор!")
                return None
        except ValueError:
            renderer.show_error("Введите число!")
            return None
    
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
    
    def apply_bonuses(self, attributes: Dict[str, int], race_name: str, class_name: str) -> Dict[str, int]:
        """Применяет расовые и классовые бонусы к характеристикам."""
        # Временные данные до создания YAML
        races_data = {
            "Человек": {'bonuses': {'strength': 1, 'dexterity': 1, 'constitution': 1, 'intelligence': 1, 'wisdom': 1, 'charisma': 1}},
            "Высокий эльф": {'bonuses': {'dexterity': 2, 'intelligence': 1}},
            "Лесной эльф": {'bonuses': {'dexterity': 2, 'wisdom': 1}},
            "Полуорк": {'bonuses': {'strength': 2, 'constitution': 1}}
        }
        
        classes_data = {
            "Воин": {'bonuses': {'strength': 1, 'constitution': 1}},
            "Волшебник": {'bonuses': {'intelligence': 1, 'wisdom': 1}},
            "Плут": {'bonuses': {'dexterity': 1, 'charisma': 1}}
        }
        
        # Применяем расовые бонусы
        race_data = races_data.get(race_name, {})
        for attr, bonus in race_data.get('bonuses', {}).items():
            if attr in attributes:
                attributes[attr] += bonus
        
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
        renderer.show_text(f"Раса: {character.race}")
        renderer.show_text(f"Класс: {character.character_class}")
        renderer.show_text(f"Уровень: {character.level}")
        
        renderer.show_text("\nХарактеристики:")
        renderer.show_text(f"  СИЛ: {character.strength} ({character.get_ability_modifier(character.strength):+d})")
        renderer.show_text(f"  ЛОВ: {character.dexterity} ({character.get_ability_modifier(character.dexterity):+d})")
        renderer.show_text(f"  ТЕЛ: {character.constitution} ({character.get_ability_modifier(character.constitution):+d})")
        renderer.show_text(f"  ИНТ: {character.intelligence} ({character.get_ability_modifier(character.intelligence):+d})")
        renderer.show_text(f"  МДР: {character.wisdom} ({character.get_ability_modifier(character.wisdom):+d})")
        renderer.show_text(f"  ХАР: {character.charisma} ({character.get_ability_modifier(character.charisma):+d})")
        
        renderer.show_text(f"\nПроизводные:")
        renderer.show_text(f"  HP: {character.hp_current}/{character.hp_max}")
        renderer.show_text(f"  AC: {character.ac}")
        renderer.show_text(f"  Золото: {character.gold}")
        
        renderer.show_text("\n")
    
    def create_character(self) -> Optional[Character]:
        """Создает персонажа."""
        # Шаг 1: Ввод имени
        name = self.input_name()
        if not name:
            return None
        
        # Шаг 2: Выбор расы
        race_name = self.select_race()
        if not race_name:
            return None
        
        # Шаг 3: Выбор класса
        class_name = self.select_class()
        if not class_name:
            return None
        
        # Шаг 4: Генерация характеристик
        attributes = self.generate_attributes()
        
        # Шаг 5: Применение бонусов
        final_attributes = self.apply_bonuses(attributes, race_name, class_name)
        
        # Создаем персонажа
        character = Character(
            name=name,
            race=race_name,
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