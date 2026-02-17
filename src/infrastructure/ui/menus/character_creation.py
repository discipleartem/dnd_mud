# src/ui/menus/character_creation.py
"""
UI меню создания персонажа D&D MUD.

Применяемые паттерны:
- Menu (Меню) — пошаговый интерфейс создания
- Controller (Контроллер) — обработка пользовательского ввода
- Observer (Наблюдатель) — обновление интерфейса при изменениях

Применяемые принципы:
- Single Responsibility — каждый класс отвечает за свой этап создания
- Open/Closed — легко добавлять новые шаги создания
- Dependency Inversion — зависимость от абстракций бизнес-логики
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from ....domain.services.character_generation import (
    CharacterBuilder, CharacterFactory, AttributeGenerator, GenerationMethod
)
from ....domain.entities.character import Character
from ....domain.entities.race_factory import RaceFactory
from ....domain.entities.class_factory import CharacterClassFactory
from ....domain.value_objects.attributes import StandardAttributes
from ....adapters.gateways.localization.loader import localization
from ..input_handler import InputHandler
from ..renderer import Renderer


class CreationStep(Enum):
    """Шаги создания персонажа."""
    BASIC_INFO = "basic_info"
    GENERATION_METHOD = "generation_method"
    ATTRIBUTES = "attributes"
    RACE_CLASS = "race_class"
    REVIEW = "review"
    CONFIRMATION = "confirmation"


class CharacterCreationMenu:
    """Меню создания персонажа."""
    
    def __init__(self, input_handler: InputHandler, renderer: Renderer):
        """Инициализирует меню создания."""
        self.input_handler = input_handler
        self.renderer = renderer
        self.builder = CharacterBuilder()
        self.current_step = CreationStep.BASIC_INFO
        self.character: Optional[Character] = None
        
        # Данные для текущего создания
        self.temp_name = ""
        self.temp_level = 1
        self.temp_race = "human"
        self.temp_class = "fighter"
        self.temp_attributes: Dict[str, int] = {}
        self.generation_method: Optional[GenerationMethod] = None
        self.point_buy_remaining = 27
    
    def run(self) -> Optional[Character]:
        """Запускает процесс создания персонажа."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа D&D")
        
        while self.current_step != CreationStep.CONFIRMATION:
            try:
                self._handle_current_step()
            except KeyboardInterrupt:
                self._handle_cancellation()
                return None
            except Exception as e:
                self.renderer.render_error(f"Ошибка: {e}")
                self.input_handler.wait_for_enter()
        
        return self.character
    
    def _handle_current_step(self) -> None:
        """Обрабатывает текущий шаг создания."""
        step_handlers = {
            CreationStep.BASIC_INFO: self._handle_basic_info,
            CreationStep.GENERATION_METHOD: self._handle_generation_method,
            CreationStep.RACE_CLASS: self._handle_race_class,
            CreationStep.REVIEW: self._handle_review,
            CreationStep.CONFIRMATION: self._handle_confirmation
        }
        
        handler = step_handlers.get(self.current_step)
        if handler:
            handler()
    
    def _handle_basic_info(self) -> None:
        """Обрабатывает ввод базовой информации."""
        self.renderer.clear_screen()
        self.renderer.render_title("Шаг 1: Базовая информация")
        
        # Ввод имени
        self.temp_name = self.input_handler.get_string(
            "Введите имя персонажа: ",
            default=self.temp_name,
            allow_empty=False
        )
        
        # Ввод уровня
        self.temp_level = self.input_handler.get_int(
            "Введите уровень (1-20): ",
            min_value=1,
            max_value=20,
            default=self.temp_level
        )
        
        self.builder.set_name(self.temp_name).set_level(self.temp_level)
        self.current_step = CreationStep.GENERATION_METHOD
    
    def _handle_generation_method(self) -> None:
        """Обрабатывает выбор метода генерации характеристик."""
        self.renderer.clear_screen()
        self.renderer.render_title("Шаг 2: Метод генерации характеристик")
        
        methods = AttributeGenerator.get_available_methods()
        
        print("\nДоступные методы генерации:")
        for i, method in enumerate(methods, 1):
            print(f"{i}. {method.name}")
            print(f"   {method.description}")
        
        choice = self.input_handler.get_int(
            "\nВыберите метод генерации: ",
            min_value=1,
            max_value=len(methods)
        )
        
        selected_method = methods[choice - 1]
        self.generation_method = selected_method.method_type
        
        if self.generation_method == GenerationMethod.STANDARD_ARRAY:
            self._handle_standard_array()
        elif self.generation_method == GenerationMethod.FOUR_D6_DROP_LOWEST:
            self._handle_four_d6()
        elif self.generation_method == GenerationMethod.POINT_BUY:
            self._handle_point_buy()
        
        self.current_step = CreationStep.RACE_CLASS
    
    def _handle_standard_array(self) -> None:
        """Обрабатывает генерацию стандартным набором."""
        self.temp_attributes = AttributeGenerator.generate_standard_array()
        self.builder.set_attributes_manual(self.temp_attributes)
        
        self.renderer.clear_screen()
        self.renderer.render_title("Характеристики сгенерированы")
        
        print("\nВаши характеристики (стандартный набор):")
        self._display_attributes(self.temp_attributes)
        
        self.input_handler.wait_for_enter()
    
    def _handle_four_d6(self) -> None:
        """Обрабатывает генерацию методом 4d6."""
        self.temp_attributes = AttributeGenerator.generate_four_d6_drop_lowest()
        self.builder.set_attributes_manual(self.temp_attributes)
        
        self.renderer.clear_screen()
        self.renderer.render_title("Характеристики сгенерированы")
        
        print("\nВаши характеристики (4d6 drop lowest):")
        self._display_attributes(self.temp_attributes)
        
        self.input_handler.wait_for_enter()
    
    def _handle_point_buy(self) -> None:
        """Обрабатывает покупку очков."""
        self.renderer.clear_screen()
        self.renderer.render_title("Покупка характеристик")
        
        # Инициализируем значениями по умолчанию
        if not self.temp_attributes:
            self.temp_attributes = {attr: 10 for attr in StandardAttributes.get_all().keys()}
        
        costs = AttributeGenerator.get_point_buy_costs()
        
        while True:
            self.point_buy_remaining = AttributeGenerator.get_point_buy_remaining_points(self.temp_attributes)
            
            print(f"\nОсталось очков: {self.point_buy_remaining}")
            print("\nТекущие характеристики:")
            
            for i, (attr_name, value) in enumerate(self.temp_attributes.items()):
                attr_info = StandardAttributes.get_attribute(attr_name)
                cost = costs.get(value, 0)
                print(f"{i+1}. {attr_info.short_name}: {value} (стоимость: {cost})")
            
            print("\nВыберите характеристику для изменения или 0 для продолжения:")
            choice = self.input_handler.get_int("Ваш выбор: ", min_value=0, max_value=6)
            
            if choice == 0:
                if AttributeGenerator.validate_point_buy_attributes(self.temp_attributes):
                    break
                else:
                    self.renderer.render_error("Невалидные характеристики! Используйте все очки.")
                    self.input_handler.wait_for_enter()
                    continue
            
            # Выбираем характеристику
            attr_names = list(self.temp_attributes.keys())
            selected_attr = attr_names[choice - 1]
            current_value = self.temp_attributes[selected_attr]
            
            # Новое значение
            new_value = self.input_handler.get_int(
                f"Новое значение для {StandardAttributes.get_attribute(selected_attr).short_name} (8-15): ",
                min_value=8,
                max_value=15,
                default=current_value
            )
            
            self.temp_attributes[selected_attr] = new_value
        
        self.builder.set_attributes_point_buy(self.temp_attributes)
    
    def _handle_race_class(self) -> None:
        """Обрабатывает выбор расы и класса."""
        self.renderer.clear_screen()
        self.renderer.render_title("Шаг 3: Раса и класс")
        
        # Выбор расы
        races = RaceFactory.get_available_races()
        print("\nДоступные расы:")
        for i, race in enumerate(races, 1):
            print(f"{i}. {race.name}")
        
        race_choice = self.input_handler.get_int(
            "\nВыберите расу: ",
            min_value=1,
            max_value=len(races)
        )
        self.temp_race = races[race_choice - 1].name
        
        # Выбор класса
        classes = CharacterClassFactory.get_available_classes()
        print("\nДоступные классы:")
        for i, char_class in enumerate(classes, 1):
            print(f"{i}. {char_class.name}")
        
        class_choice = self.input_handler.get_int(
            "\nВыберите класс: ",
            min_value=1,
            max_value=len(classes)
        )
        self.temp_class = classes[class_choice - 1].name
        
        self.builder.set_race(self.temp_race).set_class(self.temp_class)
        self.current_step = CreationStep.REVIEW
    
    def _handle_review(self) -> None:
        """Обрабатывает просмотр и подтверждение персонажа."""
        self.renderer.clear_screen()
        self.renderer.render_title("Шаг 4: Просмотр персонажа")
        
        # Создаем персонажа для предпросмотра
        try:
            self.character = self.builder.build()
            self._display_character_summary(self.character)
            
            print("\n1. Сохранить персонажа")
            print("2. Вернуться к настройкам")
            print("3. Отменить создание")
            
            choice = self.input_handler.get_int("\nВаш выбор: ", min_value=1, max_value=3)
            
            if choice == 1:
                self.current_step = CreationStep.CONFIRMATION
            elif choice == 2:
                self.current_step = CreationStep.BASIC_INFO
            else:
                raise KeyboardInterrupt()
                
        except Exception as e:
            self.renderer.render_error(f"Ошибка при создании персонажа: {e}")
            self.input_handler.wait_for_enter()
            self.current_step = CreationStep.BASIC_INFO
    
    def _handle_confirmation(self) -> None:
        """Обрабатывает финальное подтверждение."""
        self.renderer.clear_screen()
        self.renderer.render_success("Персонаж успешно создан!")
        print(f"\nИмя: {self.character.name}")
        print(f"Раса: {self.character.race.name}")
        print(f"Класс: {self.character.character_class.name}")
        print(f"Уровень: {self.character.level}")
        
        self.input_handler.wait_for_enter()
    
    def _handle_cancellation(self) -> None:
        """Обрабатывает отмену создания."""
        self.renderer.render_info("Создание персонажа отменено")
    
    def _display_attributes(self, attributes: Dict[str, int]) -> None:
        """Отображает характеристики."""
        for attr_name, value in attributes.items():
            attr_info = StandardAttributes.get_attribute(attr_name)
            modifier = (value - 10) // 2
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            print(f"  {attr_info.short_name}: {value} ({mod_str})")
    
    def _display_character_summary(self, character: Character) -> None:
        """Отображает сводку персонажа."""
        print(f"\n=== {character.name} ===")
        print(f"Раса: {character.race.name}")
        print(f"Класс: {character.character_class.name}")
        print(f"Уровень: {character.level}")
        
        print(f"\nХарактеристики:")
        modifiers = character.get_all_modifiers()
        for attr_name in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            attr_info = StandardAttributes.get_attribute(attr_name)
            value = getattr(character, attr_name).value
            modifier = modifiers[attr_name]
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            print(f"  {attr_info.short_name}: {value} ({mod_str})")
        
        print(f"\nПроизводные характеристики:")
        print(f"  HP: {character.hp_current}/{character.hp_max}")
        print(f"  AC: {character.ac}")
        print(f"  Бонус мастерства: +{character.get_proficiency_bonus()}")


class CharacterCreationController:
    """Контроллер создания персонажа."""
    
    def __init__(self, input_handler: InputHandler, renderer: Renderer):
        """Инициализирует контроллер."""
        self.input_handler = input_handler
        self.renderer = renderer
    
    def create_character(self) -> Optional[Character]:
        """Создает нового персонажа."""
        menu = CharacterCreationMenu(self.input_handler, self.renderer)
        return menu.run()
    
    def create_quick_character(self, name: str = "Безымянный") -> Character:
        """Создает персонажа быстро (с настройками по умолчанию)."""
        return CharacterFactory.create_standard_character(name)


# Пример использования
if __name__ == "__main__":
    # Для тестирования потребуется мокинг InputHandler и Renderer
    print("Модуль создания персонажа готов к использованию")
