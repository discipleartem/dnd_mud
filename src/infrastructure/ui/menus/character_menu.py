"""
Меню создания персонажа D&D MUD.

Реализует пошаговое создание персонажа с выбором расы, класса
и генерацией характеристик.
"""

from __future__ import annotations
from typing import Dict, Any, Optional

from src.domain.entities.character import Character
from src.domain.entities.race import Race
from src.domain.entities.class_ import CharacterClass
from src.infrastructure.ui.renderer import renderer
from src.infrastructure.ui.input_handler import input_handler


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
            "6. Назад",
        ]

        for i, step in enumerate(steps, 1):
            status = "✓" if i < self.current_step else " "
            renderer.show_text(f"{status} {i}. {step}")

        renderer.show_text("\n")

    def get_choice(self, prompt: str, max_choice: int) -> int:
        """Получает выбор пользователя."""
        max_attempts = 10
        attempts = 0

        while attempts < max_attempts:
            attempts += 1
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

        # Если превысили количество попыток, возвращаем -1
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
        renderer.clear_screen()
        renderer.show_title("=== ВЫБОР РАСЫ ===")

        # Получаем все расы из фабрики
        races = UniversalRaceFactory.get_all_races()
        race_choices = UniversalRaceFactory.get_race_choices()

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
                result = {"race": selected_race}

                # Если это человек и есть альтернативные особенности
                if (
                    selected_race.name == "Человек"
                    and selected_race.has_alternative_features()
                ):
                    alternative_choice = self.show_alternative_features_selection(
                        selected_race
                    )
                    if alternative_choice:
                        result["alternative_choices"] = alternative_choice

                return result
        else:
            renderer.show_error("Неверный выбор.")
            return None

    def show_alternative_features_selection(
        self, race: "Race"
    ) -> Optional[Dict[str, Any]]:
        """Показывает меню выбора альтернативных особенностей для людей.

        Args:
            race: Объект расы Человек

        Returns:
            Словарь с выбранными альтернативными опциями или None
        """
        renderer.clear_screen()
        renderer.show_title("=== АЛЬТЕРНАТИВНЫЕ ОСОБЕННОСТИ ЛЮДЕЙ ===")

        renderer.show_text(race.alternative_features.get("description", ""))
        renderer.show_text("\nВыберите альтернативную особенность:")

        options = race.get_alternative_options()
        choice_map = {}

        for i, (key, option) in enumerate(options.items(), 1):
            choice_map[str(i)] = key
            renderer.show_text(f"{i}. {option['name']}")
            renderer.show_text(f"   {option['description']}")
            renderer.show_text("")

        renderer.show_text(
            f"{len(options) + 1}. Стандартные бонусы (+1 ко всем характеристикам)"
        )
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

            if selected_option["type"] == "ability_bonus":
                return self.show_ability_bonus_selection(selected_option)
            elif selected_option["type"] == "skill":
                return self.show_skill_selection(selected_option)
            elif selected_option["type"] == "feat":
                return self.show_feat_selection(selected_option)

        renderer.show_error("Неверный выбор.")
        return None

    def show_ability_bonus_selection(self, option: Dict[str, Any]) -> Dict[str, Any]:
        """Показывает выбор увеличения характеристик."""
        renderer.clear_screen()
        renderer.show_title("=== УВЕЛИЧЕНИЕ ХАРАКТЕРИСТИК ===")

        renderer.show_text(option["description"])
        renderer.show_text(f"\nВыберите {option['max_choices']} характеристики:")

        attributes = option["allowed_attributes"]
        attr_names = {
            "strength": "СИЛ",
            "dexterity": "ЛОВ",
            "constitution": "ТЕЛ",
            "intelligence": "ИНТ",
            "wisdom": "МДР",
            "charisma": "ХАР",
        }

        for i, attr in enumerate(attributes, 1):
            renderer.show_text(f"{i}. {attr_names[attr]} ({attr})")

        renderer.show_text("\nВведите номера через пробел:")

        choice = input()
        chosen_indices = [
            int(x.strip()) - 1 for x in choice.split() if x.strip().isdigit()
        ]

        if len(chosen_indices) != option["max_choices"]:
            renderer.show_error(
                f"Нужно выбрать ровно {option['max_choices']} характеристики!"
            )
            return self.show_ability_bonus_selection(option)

        chosen_attrs = []
        for idx in chosen_indices:
            if 0 <= idx < len(attributes):
                chosen_attrs.append(attributes[idx])

        return {"ability_scores": chosen_attrs}

    def show_skill_selection(self, option: Dict[str, Any]) -> Dict[str, Any]:
        """Показывает выбор навыка (заглушка)."""
        renderer.clear_screen()
        renderer.show_title("=== ВЛАДЕНИЕ НАВЫКОМ ===")

        renderer.show_text(option["description"])
        renderer.show_text("\nВ разработке - будет доступно в следующей версии")
        renderer.show_text("\nНажмите Enter для продолжения...")
        input()

        return {"skill": "athletics"}  # Временная заглушка

    def show_feat_selection(self, option: Dict[str, Any]) -> Dict[str, Any]:
        """Показывает выбор черты (заглушка)."""
        renderer.clear_screen()
        renderer.show_title("=== ЧЕРТА ===")

        renderer.show_text(option["description"])
        renderer.show_text("\nВ разработке - будет доступно в следующей версии")
        renderer.show_text("\nНажмите Enter для продолжения...")
        input()

        return {"feat": "heavily_armored"}  # Временная заглушка

    def select_class(self) -> CharacterClass:
        """Выбор класса персонажа."""
        from ...core.entities.class_factory import CharacterClassFactory

        renderer.clear_screen()
        renderer.show_title("=== ВЫБОР КЛАССА ===")

        # Получаем все классы из фабрики
        classes = CharacterClassFactory.get_all_classes()
        class_choices = CharacterClassFactory.get_class_choices()

        # Отображаем классы
        for choice_num, class_name in class_choices.items():
            renderer.show_text(f"{choice_num}. {class_name}")

        renderer.show_text("0. Назад")
        renderer.show_text("\nВведите номер класса:")

        choice = input()

        if choice == "0":
            return None

        if choice in class_choices:
            class_name = class_choices[choice]
            # Находим объект класса
            for character_class in classes:
                if character_class.name == class_name:
                    return character_class

        renderer.show_error("Класс не найден.")
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
                Path(__file__).parent.parent.parent.parent
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
            #             attributes = {
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
            max_value = selected_method.get("max_value", 15)

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

    def apply_bonuses(
        self,
        attributes: Dict[str, int],
        race_info: Dict[str, Any],
        character_class: CharacterClass,
    ) -> Dict[str, int]:
        """Применяет расовые бонусы к характеристикам."""
        race = race_info["race"]
        alternative_choices = race_info.get("alternative_choices")

        # Применяем расовые бонусы
        if alternative_choices:
            # Альтернативные бонусы для людей
            attributes = race.apply_alternative_bonuses(attributes, alternative_choices)
        else:
            # Стандартные расовые бонусы
            attributes = race.apply_bonuses(attributes)

        return attributes

    def show_preview(self, character: Character) -> None:
        """Показывает предпросмотр персонажа."""
        renderer.clear_screen()
        renderer.show_title("=== ПРЕДПРОСМОТР ПЕРСОНАЖА ===")

        renderer.show_text(f"Имя: {character.name}")
        renderer.show_text(f"Раса: {character.race.localized_name}")
        renderer.show_text(f"Класс: {character.character_class.name}")
        renderer.show_text(f"Уровень: {character.level}")

        renderer.show_text("\nХарактеристики:")
        renderer.show_text(
            f"  СИЛ: {character.strength.value} ({character.get_ability_modifier(character.strength.value):+d})"
        )
        renderer.show_text(
            f"  ЛОВ: {character.dexterity.value} ({character.get_ability_modifier(character.dexterity.value):+d})"
        )
        renderer.show_text(
            f"  ТЕЛ: {character.constitution.value} ({character.get_ability_modifier(character.constitution.value):+d})"
        )
        renderer.show_text(
            f"  ИНТ: {character.intelligence.value} ({character.get_ability_modifier(character.intelligence.value):+d})"
        )
        renderer.show_text(
            f"  МДР: {character.wisdom.value} ({character.get_ability_modifier(character.wisdom.value):+d})"
        )
        renderer.show_text(
            f"  ХАР: {character.charisma.value} ({character.get_ability_modifier(character.charisma.value):+d})"
        )

        renderer.show_text("\nПроизводные:")
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
        race_info = self.show_race_selection()
        if not race_info:
            return None

        # Шаг 3: Выбор класса
        character_class = self.select_class()
        if not character_class:
            return None

        # Шаг 4: Генерация характеристик
        attributes = self.generate_attributes()

        # Шаг 5: Применение бонусов
        final_attributes = self.apply_bonuses(attributes, race_info, character_class)

        # Получаем объект расы
        race = race_info["race"]

        # Создаем персонажа с базовыми характеристиками (10)
        character = Character(
            name=name, race=race, character_class=character_class, level=1
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
