"""UI меню создания персонажа D&D MUD."""

from typing import Optional, Dict, TypedDict, List
from enum import Enum

from src.domain.services.character_generation import (
    CharacterGenerator,
    GenerationMethod,
)
from src.domain.entities.character import Character
from src.domain.entities.universal_race_factory import UniversalRaceFactory
from src.domain.entities.class_factory import CharacterClassFactory
from src.domain.value_objects.attributes import get_standard_attributes
from ..input_handler import InputHandler
from ..renderer import Renderer


class CreationStep(Enum):
    """Шаги создания персонажа."""

    BASIC_INFO = "basic_info"
    RACE = "race"
    CLASS = "class"
    ATTRIBUTES = "attributes"
    REVIEW = "review"


class CreationData(TypedDict):
    """Данные создания персонажа."""

    name: str
    race_name: str
    class_name: str
    generation_method: str
    attributes: Dict[str, int]
    race_choices: Dict[str, str]
    class_choices: Dict[str, str]
    level: int
    background: Optional[str]
    alignment: Optional[str]
    personality_traits: Optional[List[str]]
    ideals: Optional[List[str]]
    bonds: Optional[List[str]]
    flaws: Optional[List[str]]


class CharacterCreationController:
    """Простой контроллер создания персонажа."""

    def __init__(self, input_handler: InputHandler, renderer: Renderer) -> None:
        self.input_handler = input_handler
        self.renderer = renderer
        self.creation_data: CreationData = {
            "name": "",
            "race_name": "",
            "class_name": "",
            "generation_method": "",
            "attributes": {},
            "race_choices": {},
            "class_choices": {},
            "level": 1,
            "background": None,
            "alignment": None,
            "personality_traits": None,
            "ideals": None,
            "bonds": None,
            "flaws": None,
        }

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

        races = list(UniversalRaceFactory.get_available_races())
        print("\\nДоступные расы:")
        for i, race in enumerate(races, 1):
            print(f"{i}. {race}")

        choice = self.input_handler.get_int(
            "Выберите расу (номер): ", min_value=1, max_value=len(races)
        )

        self.creation_data["race_name"] = races[choice - 1]

    def _select_class(self) -> None:
        """Выбор класса."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа - Выбор класса")

        classes = CharacterClassFactory.get_available_classes()
        class_names = [cls.name for cls in classes]
        print("\nДоступные классы:")
        for i, class_name in enumerate(class_names, 1):
            print(f"{i}. {class_name}")

        choice = self.input_handler.get_int(
            "Выберите класс (номер): ", min_value=1, max_value=len(class_names)
        )

        self.creation_data["class_name"] = class_names[choice - 1]

    def _select_generation_method(self) -> None:
        """Выбор метода генерации характеристик."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа - Генерация характеристик")

        methods = [
            (
                GenerationMethod.STANDARD_ARRAY,
                "Стандартный набор (15, 14, 13, 12, 10, 8)",
            ),
            (GenerationMethod.FOUR_D6_DROP_LOWEST, "4d6 отбросить низший"),
            (GenerationMethod.POINT_BUY, "Покупка очков (все по 10)"),
        ]

        print("\\nМетоды генерации:")
        for i, (method, description) in enumerate(methods, 1):
            print(f"{i}. {description}")

        choice = self.input_handler.get_int(
            "Выберите метод (номер): ", min_value=1, max_value=len(methods)
        )

        self.creation_data["generation_method"] = methods[choice - 1][0].value

    def _generate_attributes(self) -> None:
        """Генерирует характеристики."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа - Характеристики")

        attributes = CharacterGenerator.generate_attributes(
            GenerationMethod(self.creation_data["generation_method"])
        )

        print("\\nСгенерированные характеристики:")
        for attr_name, value in attributes.items():
            attr_info = get_standard_attributes().get_attribute(attr_name)
            if attr_info:
                print(f"  {attr_info.short_name}: {value}")
            else:
                print(f"  {attr_name}: {value}")

        self.input_handler.wait_for_enter()
        self.creation_data["attributes"] = attributes

    def _review_character(self) -> bool:
        """Показывает предварительный просмотр персонажа."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа - Проверка")

        print(f"\\nИмя: {self.creation_data['name']}")
        print(f"Раса: {self.creation_data['race_name']}")
        print(f"Класс: {self.creation_data['class_name']}")

        print("\\nХарактеристики:")
        attributes = self.creation_data["attributes"]
        for attr_name, value in attributes.items():
            attr_info = get_standard_attributes().get_attribute(attr_name)
            if attr_info:
                modifier = (value - 10) // 2
                mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                print(f"  {attr_info.short_name}: {value} ({mod_str})")
            else:
                modifier = (value - 10) // 2
                mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                print(f"  {attr_name}: {value} ({mod_str})")

        confirm = self.input_handler.get_text("\\nСоздать персонажа? (д/н): ").lower()
        return confirm in ["д", "y", "yes"]

    def _create_final_character(self) -> Character:
        """Создает финального персонажа."""
        return CharacterGenerator.create_character(
            name=self.creation_data["name"],
            race_name=self.creation_data["race_name"],
            class_name=self.creation_data["class_name"],
            generation_method=GenerationMethod(self.creation_data["generation_method"]),
        )
