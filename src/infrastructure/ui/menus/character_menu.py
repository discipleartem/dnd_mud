# src/infrastructure/ui/menus/character_menu.py
"""
Меню создания персонажа D&D MUD.

Реализует пошаговое создание персонажа с выбором расы, класса
и генерацией характеристик.
"""

from __future__ import annotations
from typing import Dict, List, Union, Optional, TYPE_CHECKING, TypedDict

from ....domain.entities.character import Character
from ....domain.entities.race import Race, AlternativeFeature
from ....domain.entities.class_ import CharacterClass
from ....domain.entities.universal_race_factory import UniversalRaceFactory
from ..renderer import Renderer
from ..input_handler import InputHandler

if TYPE_CHECKING:
    from ....domain.entities.race_features import RaceInfo
else:
    RaceInfo = dict


class AbilityBonusOption(TypedDict):
    """Опция увеличения характеристики."""

    name: str
    description: str
    type: str
    max_choices: int
    allowed_attributes: List[str]


class SkillOption(TypedDict):
    """Опция навыка."""

    name: str
    description: str
    type: str


class FeatOption(TypedDict):
    """Опция черты."""

    name: str
    description: str
    type: str


class CharacterMenu:
    """Меню создания персонажа."""

    def __init__(self, renderer: Renderer, input_handler: InputHandler) -> None:
        """Инициализация меню."""
        self.renderer = renderer
        self.input_handler = input_handler
        self.character: Optional[Character] = None
        self.current_step: int = 0
        self.max_steps: int = 5

    def show(self) -> None:
        """Отображает текущее меню."""
        self.renderer.clear_screen()

        title = "=== СОЗДАНИЕ ПЕРСОНАЖА ==="
        self.renderer.show_title(title)

        steps = [
            "1. Ввести имя персонажа",
            "2. Выбрать расу",
            "3. Выбрать класс",
            "4. Сгенерировать характеристики",
            "5. Подтвердить создание",
            "6. Назад",
        ]

        for i, step in enumerate(steps, 1):
            status = "✓" if i < self.current_step else " "
            self.renderer.show_text(f"{status} {i}. {step}")

        self.renderer.show_text("\n")

    def get_choice(self, prompt: str, max_choice: int) -> int:
        """Получает выбор пользователя."""
        return self.input_handler.get_menu_choice(max_choice)

    def input_name(self) -> str:
        """Ввод имени персонажа."""
        self.renderer.clear_screen()
        self.renderer.show_title("=== ВВЕДИТЕ ИМЯ ПЕРСОНАЖА ===")
        self.renderer.show_text("Имя персонажа (оставьте пустым для случайного имени):")

        name = self.input_handler.get_text_input("> ")

        if not name.strip():
            import random

            names = ["Артас", "Лиана", "Гэндальф", "Тирион", "Фродо"]
            name = random.choice(names)
            self.renderer.show_text(f"Сгенерировано имя: {name}")

        self.renderer.show_text("\n")
        return name

    def show_race_selection(self) -> Optional[Dict[str, object]]:
        """Показывает меню выбора расы.

        Returns:
            Словарь с информацией о выбранной расе или None
        """
        self.renderer.clear_screen()
        self.renderer.show_title("=== ВЫБОР РАСЫ ===")

        # Получаем все расы из фабрики
        races = UniversalRaceFactory.get_all_races()
        race_choices = UniversalRaceFactory.get_race_choices()

        # Отображаем расы
        for choice_num, race_name in race_choices.items():
            if choice_num != "0":
                self.renderer.show_text(f"{choice_num}. {race_name}")

        self.renderer.show_text("0. Назад")
        self.renderer.show_text("\nВведите номер расы:")

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
                # Если это человек и есть альтернативные особенности
                if (
                    selected_race.name == "Человек"
                    and selected_race.alternative_features
                ):
                    alternative_choice = self.show_alternative_features_selection(
                        selected_race
                    )
                    if alternative_choice:
                        return {
                            "race": selected_race,
                            "alternative_choices": alternative_choice,
                        }

                return {"race": selected_race}
        else:
            self.renderer.show_error("Неверный выбор.")
            return None

        return None

    def show_alternative_features_selection(
        self, race: Race
    ) -> Optional[Dict[str, AlternativeFeature]]:
        """Показывает меню выбора альтернативных особенностей для людей.

        Args:
            race: Объект расы Человек

        Returns:
            Словарь с выбранными альтернативными опциями или None
        """
        self.renderer.clear_screen()
        self.renderer.show_title("=== АЛЬТЕРНАТИВНЫЕ ОСОБЕННОСТИ ЛЮДЕЙ ===")

        alternative_features: Optional[AlternativeFeature] = race.alternative_features
        if alternative_features:
            self.renderer.show_text(str(alternative_features.get("description", "")))
        self.renderer.show_text("\nВыберите альтернативную особенность:")

        options = race.get_alternative_options()
        choice_map = {}

        for i, (key, option) in enumerate(options.items(), 1):
            choice_map[str(i)] = key
            self.renderer.show_text(f"{i}. {str(option['name'])}")
            self.renderer.show_text(f"   {str(option['description'])}")
            self.renderer.show_text("")

        self.renderer.show_text(
            f"{len(options) + 1}. Стандартные бонусы (+1 ко всем характеристикам)"
        )
        self.renderer.show_text("0. Назад")
        self.renderer.show_text("\nВведите номер:")

        choice = input()

        if choice == "0":
            return None

        if choice == str(len(options) + 1):
            # Стандартные бонусы
            return None

        if choice in choice_map:
            selected_key = choice_map[choice]
            selected_option = options[selected_key]

            # Проверяем тип опции по полю type
            option_type = selected_option.get("type", "")

            if option_type == "ability_bonus":
                # Извлекаем нужные поля для ability_bonus
                ability_option = {
                    "name": selected_option.get("name", ""),
                    "description": selected_option.get("description", ""),
                    "type": option_type,
                    "max_choices": selected_option.get("max_choices", 2),
                    "allowed_attributes": selected_option.get("allowed_attributes", []),
                }
                return self.show_ability_bonus_selection(ability_option)  # type: ignore
            elif option_type == "skill":
                # Извлекаем нужные поля для skill
                skill_option = {
                    "name": selected_option.get("name", ""),
                    "description": selected_option.get("description", ""),
                    "type": option_type,
                }
                return self.show_skill_selection(skill_option)  # type: ignore
            elif option_type == "feat":
                # Извлекаем нужные поля для feat
                feat_option = {
                    "name": selected_option.get("name", ""),
                    "description": selected_option.get("description", ""),
                    "type": option_type,
                }
                return self.show_feat_selection(feat_option)  # type: ignore

        self.renderer.show_error("Неверный выбор.")
        return None

    def show_ability_bonus_selection(
        self, option: Dict[str, Union[str, int, List[str]]]
    ) -> AlternativeFeature:
        """Показывает выбор увеличения характеристик."""
        self.renderer.clear_screen()
        self.renderer.show_title("=== УВЕЛИЧЕНИЕ ХАРАКТЕРИСТИК ===")

        self.renderer.show_text(str(option["description"]))
        max_choices = option.get("max_choices", 2)
        allowed_attrs = option.get(
            "allowed_attributes",
            [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ],
        )
        self.renderer.show_text(f"\nВыберите {max_choices} характеристики:")
        attributes: List[str] = (
            allowed_attrs if isinstance(allowed_attrs, list) else [str(allowed_attrs)]
        )
        attr_names = {
            "strength": "СИЛ",
            "dexterity": "ЛОВ",
            "constitution": "ТЕЛ",
            "intelligence": "ИНТ",
            "wisdom": "МДР",
            "charisma": "ХАР",
        }

        for i, attr in enumerate(attributes, 1):
            self.renderer.show_text(f"{i}. {attr_names.get(attr, attr)} ({str(attr)})")

        self.renderer.show_text("\nВведите номера через пробел:")

        choice = input()
        chosen_indices = [
            int(x.strip()) - 1 for x in choice.split() if x.strip().isdigit()
        ]

        if len(chosen_indices) != max_choices:
            self.renderer.show_error(
                f"Нужно выбрать ровно {max_choices} характеристики!"
            )
            return self.show_ability_bonus_selection(option)

        chosen_attrs = []
        for idx in chosen_indices:
            if 0 <= idx < len(attributes):
                chosen_attrs.append(attributes[idx])

        return {
            "ability_choice": {
                "name": "Выбранные характеристики",
                "description": f"Выбраны характеристики: {', '.join(chosen_attrs)}",
                "type": "ability_choice",
            },
            "skill_choice": {},
            "feat_choice": {},
            "traits": [],
            "proficiencies": [],
            "name": None,
            "description": None,
            "type": None,
        }

    def show_skill_selection(
        self, option: Dict[str, Union[str, int]]
    ) -> AlternativeFeature:
        """Показывает выбор навыка (заглушка)."""
        self.renderer.clear_screen()
        self.renderer.show_title("=== ВЛАДЕНИЕ НАВЫКОМ ===")

        self.renderer.show_text(str(option["description"]))
        self.renderer.show_text("\nВ разработке - будет доступно в следующей версии")
        self.renderer.show_text("\nНажмите Enter для продолжения...")
        input()

        return {
            "ability_choice": {},
            "skill_choice": {
                "name": "Выбранный навык",
                "description": "Выбран навык: athletics",
                "type": "skill_choice",
            },
            "feat_choice": {},
            "traits": [],
            "proficiencies": [],
            "name": None,
            "description": None,
            "type": None,
        }  # Временная заглушка

    def show_feat_selection(
        self, option: Dict[str, Union[str, int]]
    ) -> AlternativeFeature:
        """Показывает выбор черты (заглушка)."""
        self.renderer.clear_screen()
        self.renderer.show_title("=== ЧЕРТА ===")

        self.renderer.show_text(str(option["description"]))
        self.renderer.show_text("\nВ разработке - будет доступно в следующей версии")
        self.renderer.show_text("\nНажмите Enter для продолжения...")
        input()

        return {
            "ability_choice": {},
            "skill_choice": {},
            "feat_choice": {
                "name": "Выбранная черта",
                "description": "Выбрана черта: heavily_armored",
                "type": "feat_choice",
            },
            "traits": [],
            "proficiencies": [],
            "name": None,
            "description": None,
            "type": None,
        }  # Временная заглушка

    def select_class(self) -> Optional[CharacterClass]:
        """Выбор класса персонажа."""
        from ....domain.entities.class_factory import CharacterClassFactory

        self.renderer.clear_screen()
        self.renderer.show_title("=== ВЫБОР КЛАССА ===")

        # Получаем все классы из фабрики
        classes = CharacterClassFactory.get_all_classes()
        class_choices = CharacterClassFactory.get_class_choices()

        # Отображаем классы
        for choice_num, class_name in class_choices.items():
            self.renderer.show_text(f"{choice_num}. {class_name}")

        self.renderer.show_text("0. Назад")
        self.renderer.show_text("\nВведите номер класса:")

        choice = input()

        if choice == "0":
            return None

        if choice in class_choices:
            class_name = class_choices[choice]
            # Находим объект класса
            for character_class in classes:
                if character_class.name == class_name:
                    return character_class

        self.renderer.show_error("Класс не найден.")
        return None

    def generate_attributes(self, method: str = "standard_array") -> Dict[str, int]:
        """Генерирует характеристики для персонажа.

        Args:
            method: Метод генерации ('standard_array', 'four_d6_drop_lowest', 'point_buy')

        Returns:
            Словарь сгенерированных характеристик
        """
        # StandardAttributes будет использован позже

        # Загружаем методы генерации из конфигурации
        # localization будет использован позже

        try:
            import yaml
            from pathlib import Path

            config_path = (
                Path(__file__).parent.parent.parent
                / "data"
                / "yaml"
                / "attributes"
                / "core_attributes.yaml"
            )
            with open(config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                generation_methods = config.get("generation_methods", {})
        except FileNotFoundError:
            generation_methods = {}

        # Выбираем метод генерации
        selected_method = generation_methods.get(
            method, generation_methods.get("standard_array", {})
        )

        if selected_method.get("name") == "standard_array":
            attributes = {
                "strength": selected_method["values"][0],
                "dexterity": selected_method["values"][1],
                "constitution": selected_method["values"][2],
                "intelligence": selected_method["values"][3],
                "wisdom": selected_method["values"][4],
                "charisma": selected_method["values"][5],
            }
        elif selected_method.get("name") == "four_d6_drop_lowest":
            # 4d6 drop lowest
            import random

            attributes = {}
            attr_names = [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ]

            for attr_name in attr_names:
                # Бросаем 4d6 и отбрасываем наименьший
                rolls = [random.randint(1, 6) for _ in range(4)]
                rolls.sort()
                result = sum(rolls[1:])  # Отбрасываем наименьший
                attributes[attr_name] = result
        elif selected_method.get("name") == "point_buy":
            # Покупка очков (простая реализация)
            total_points = selected_method.get("total_points", 27)
            min_value = selected_method.get("min_value", 8)

            # Равномерное распределение
            points_per_attr = total_points // 6
            attributes = {
                "strength": min_value + points_per_attr,
                "dexterity": min_value + points_per_attr,
                "constitution": min_value + points_per_attr,
                "intelligence": min_value + points_per_attr,
                "wisdom": min_value + points_per_attr,
                "charisma": min_value + points_per_attr,
            }
        else:
            # Fallback на старый метод
            attributes = {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            }
            # Перемешиваем для случайного распределения (кроме point_buy)
        if selected_method.get("name") != "point_buy":
            import random

            attr_names = list(attributes.keys())
            random.shuffle(attr_names)

            shuffled_attrs = {}
            for i, attr_name in enumerate(attr_names):
                shuffled_attrs[attr_name] = attributes[attr_names[i]]
            attributes = shuffled_attrs

        return attributes

    def apply_race_bonuses(
        self,
        race_info: Dict[str, object],
        character_class: CharacterClass,
    ) -> Dict[str, int]:
        """Применяет расовые бонусы к характеристикам."""
        # TODO: Реализовать применение расовых бонусов
        return {}

    def show_preview(self, character: Character) -> None:
        """Показывает предпросмотр персонажа."""
        self.renderer.clear_screen()
        self.renderer.show_title("=== ПРЕДПРОСМОТР ПЕРСОНАЖА ===")

        self.renderer.show_text(f"Имя: {character.name}")
        self.renderer.show_text(f"Раса: {character.race.localized_name}")
        self.renderer.show_text(f"Класс: {character.character_class.name}")
        self.renderer.show_text(f"Уровень: {character.level}")

        self.renderer.show_text("\nХарактеристики:")
        self.renderer.show_text(
            f"  СИЛ: {character.strength.value} ({character.get_ability_modifier(character.strength.value):+d})"
        )
        self.renderer.show_text(
            f"  ЛОВ: {character.dexterity.value} ({character.get_ability_modifier(character.dexterity.value):+d})"
        )
        self.renderer.show_text(
            f"  ТЕЛ: {character.constitution.value} ({character.get_ability_modifier(character.constitution.value):+d})"
        )
        self.renderer.show_text(
            f"  ИНТ: {character.intelligence.value} ({character.get_ability_modifier(character.intelligence.value):+d})"
        )
        self.renderer.show_text(
            f"  МДР: {character.wisdom.value} ({character.get_ability_modifier(character.wisdom.value):+d})"
        )
        self.renderer.show_text(
            f"  ХАР: {character.charisma.value} ({character.get_ability_modifier(character.charisma.value):+d})"
        )

        self.renderer.show_text("\nПроизводные:")
        self.renderer.show_text(f"  HP: {character.hp_current}/{character.hp_max}")
        self.renderer.show_text(f"  AC: {character.ac}")
        self.renderer.show_text(f"  Золото: {character.gold}")

        self.renderer.show_text("\n")

    def create_character(self) -> Optional[Character]:
        """Создает персонажа."""

        # Шаг 1: Ввод имени
        name = self.input_name()
        if not name:
            return None

        # Шаг 2: Выбор расы
        race_info: Optional[Dict[str, object]] = self.show_race_selection()
        if not race_info:
            return None

        # Шаг 3: Выбор класса
        character_class = self.select_class()
        if not character_class:
            return None

        # Шаг 4: Генерация характеристик
        attributes = self.generate_attributes()
        if not attributes:
            return None

        # Применяем расовые бонусы
        final_attributes = self.apply_race_bonuses(race_info, character_class)

        race_obj = race_info["race"]
        if not isinstance(race_obj, Race):
            from ....domain.entities.universal_race_factory import UniversalRaceFactory

            race_name = str(race_info.get("race", "human"))
            race_obj = UniversalRaceFactory.create_race(race_name)

        character = Character(
            name=name, race=race_obj, character_class=character_class, level=1
        )

        # Применяем финальные характеристики (базовые + расовые + классовые бонусы)
        for attr_name, value in final_attributes.items():
            if hasattr(character, attr_name):
                getattr(character, attr_name).value = value

        # Рассчитываем производные характеристики
        character.calculate_derived_stats()

        # Шаг 6: Предпросмотр
        self.show_preview(character)

        # Шаг 7: Подтверждение
        self.renderer.clear_screen()
        self.renderer.show_title("=== ПОДТВЕРЖДЕНИЕ СОЗДАНИЯ ===")
        self.renderer.show_text("Сохранить персонажа?")
        self.renderer.show_text("1. Да")
        self.renderer.show_text("2. Нет (ввести заново)")
        self.renderer.show_text("3. В главное меню")

        choice = self.get_choice("Ваш выбор", 3)

        if choice == 1:
            # Сохраняем персонажа
            self.character = character
            self.renderer.show_success("Персонаж сохранен!")
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
        self.renderer.show_info("=== МЕНЮ СОЗДАНИЯ ПЕРСОНАЖА ===")

        max_attempts = 5  # Ограничиваем количество попыток создания
        attempts = 0

        while attempts < max_attempts:
            attempts += 1
            character = self.create_character()
            if character is None:
                break

            return character

        # Если превысили количество попыток, возвращаем None
        return None
