"""UI меню создания персонажа D&D MUD."""

from typing import Dict, Optional, List
from enum import Enum

from ...domain.services.character_generation import CharacterGenerator, GenerationMethod
from ...domain.entities.character import Character
from ...domain.entities.universal_race_factory import UniversalRaceFactory
from ...domain.entities.class_factory import CharacterClassFactory
from ...domain.value_objects.attributes import StandardAttributes
from ..input_handler import InputHandler
from ..renderer import Renderer


class CreationStep(Enum):
    """Шаги создания персонажа."""
    BASIC_INFO = "basic_info"
    RACE = "race"
    CLASS = "class"
    ATTRIBUTES = "attributes"
    REVIEW = "review"


class CharacterCreationController:
    """Простой контроллер создания персонажа."""
    
    def __init__(self, input_handler: InputHandler, renderer: Renderer):
        self.input_handler = input_handler
        self.renderer = renderer
        self.creation_data = {}
    
    def create_character(self) -> Optional[Character]:
        """Запускает процесс создания персонажа."""
        try:
            self._collect_basic_info()
            self._select_race()
            self._select_class()
            self._select_generation_method()
            self._generate_attributes()
            
            if self._review_character():
                return self._create_final_character()
            else:
                return None
        except KeyboardInterrupt:
            return None
    
    def _collect_basic_info(self) -> None:
        """Собирает базовую информацию."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа - Базовая информация")
        
        name = self.input_handler.get_text("Имя персонажа: ")
        if not name:
            name = "Безымянный"
        
        self.creation_data["name"] = name
    
    def _select_race(self) -> None:
        """Выбор расы."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа - Выбор расы")
        
        races = list(UniversalRaceFactory.get_available_races().keys())
        print("\\nДоступные расы:")
        for i, race in enumerate(races, 1):
            print(f"{i}. {race}")
        
        choice = self.input_handler.get_int(
            "Выберите расу (номер): ", min_value=1, max_value=len(races)
        )
        
        self.creation_data["race"] = races[choice - 1]
    
    def _select_class(self) -> None:
        """Выбор класса."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа - Выбор класса")
        
        classes = list(CharacterClassFactory.get_available_classes().keys())
        print("\\nДоступные классы:")
        for i, class_name in enumerate(classes, 1):
            print(f"{i}. {class_name}")
        
        choice = self.input_handler.get_int(
            "Выберите класс (номер): ", min_value=1, max_value=len(classes)
        )
        
        self.creation_data["class"] = classes[choice - 1]
    
    def _select_generation_method(self) -> None:
        """Выбор метода генерации характеристик."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа - Генерация характеристик")
        
        methods = [
            (GenerationMethod.STANDARD_ARRAY, "Стандартный набор (15, 14, 13, 12, 10, 8)"),
            (GenerationMethod.FOUR_D6_DROP_LOWEST, "4d6 отбросить низший"),
            (GenerationMethod.POINT_BUY, "Покупка очков (все по 10)"),
        ]
        
        print("\\nМетоды генерации:")
        for i, (method, description) in enumerate(methods, 1):
            print(f"{i}. {description}")
        
        choice = self.input_handler.get_int(
            "Выберите метод (номер): ", min_value=1, max_value=len(methods)
        )
        
        self.creation_data["generation_method"] = methods[choice - 1][0]
    
    def _generate_attributes(self) -> None:
        """Генерирует характеристики."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа - Характеристики")
        
        attributes = CharacterGenerator.generate_attributes(self.creation_data["generation_method"])
        
        print("\\nСгенерированные характеристики:")
        for attr_name, value in attributes.items():
            attr_info = StandardAttributes.get_attribute(attr_name)
            print(f"  {attr_info.short_name}: {value}")
        
        self.input_handler.wait_for_enter()
        self.creation_data["attributes"] = attributes
    
    def _review_character(self) -> bool:
        """Показывает предварительный просмотр персонажа."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа - Проверка")
        
        print(f"\\nИмя: {self.creation_data['name']}")
        print(f"Раса: {self.creation_data['race']}")
        print(f"Класс: {self.creation_data['class']}")
        
        print("\\nХарактеристики:")
        attributes = self.creation_data["attributes"]
        for attr_name, value in attributes.items():
            attr_info = StandardAttributes.get_attribute(attr_name)
            modifier = (value - 10) // 2
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            print(f"  {attr_info.short_name}: {value} ({mod_str})")
        
        confirm = self.input_handler.get_text("\\nСоздать персонажа? (д/н): ").lower()
        return confirm in ['д', 'y', 'yes']
    
    def _create_final_character(self) -> Character:
        """Создает финального персонажа."""
        return CharacterGenerator.create_character(
            name=self.creation_data["name"],
            race_name=self.creation_data["race"],
            class_name=self.creation_data["class"],
            generation_method=self.creation_data["generation_method"]
        )
