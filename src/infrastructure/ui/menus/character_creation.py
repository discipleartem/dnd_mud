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

from typing import Dict, Optional, List
from enum import Enum
import textwrap

from src.domain.services.character_generation import (
    CharacterBuilder,
    CharacterFactory,
    AttributeGenerator,
    GenerationMethod,
)
from src.domain.services.level_resolver import level_resolver
from src.domain.entities.character import Character
from src.domain.entities.universal_race_factory import UniversalRaceFactory
from src.domain.entities.race_features import RaceDisplayFormatter
from src.domain.entities.class_factory import CharacterClassFactory
from src.domain.value_objects.attributes import StandardAttributes
from ..input_handler import InputHandler
from ..renderer import Renderer


class CreationStep(Enum):
    """Шаги создания персонажа."""

    BASIC_INFO = "basic_info"
    ADVENTURE_SELECTION = "adventure_selection"
    RACE = "race"
    GENERATION_METHOD = "generation_method"
    ATTRIBUTES = "attributes"
    CLASS = "class"
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
        # Определяем начальный уровень через резолвер
        self.temp_level = level_resolver.get_starting_level()
        self.temp_race = "human"
        self.temp_class = "fighter"
        self.temp_attributes: Dict[str, int] = {}
        self.generation_method: Optional[GenerationMethod] = None
        self.point_buy_remaining = 27
        self.temp_adventure: Optional[str] = None

    def _format_text_with_wrapping(self, text: str, width: int = 50, indent: str = "   📖 ") -> str:
        """Форматирует текст с переносами для лучшего отображения.
        
        Args:
            text: Исходный текст
            width: Максимальная ширина строки (уменьшена до 50 для лучшего отображения)
            indent: Отступ для каждой строки
            
        Returns:
            Отформатированный текст с переносами
        """
        if not text:
            return ""
        
        # Разбиваем текст на слова
        words = text.split()
        if not words:
            return ""
        
        lines = []
        current_line = ""
        
        for word in words:
            # Если добавляемое слово превысит ширину
            if current_line and len(current_line) + 1 + len(word) > width:
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
        
        # Добавляем последнюю строку
        if current_line:
            lines.append(current_line)
        
        # Форматируем строки с отступами
        if not lines:
            return f"{indent}"
        
        # Первая строка с полным отступом
        result = f"{indent}{lines[0]}"
        
        # Остальные строки с отступом без эмодзи (ровно по левому краю текста)
        spaces_after_emoji = ' ' * len('📖 ')  # Только пробелы вместо эмодзи
        for line in lines[1:]:
            result += f"\n   {spaces_after_emoji}{line}"
        
        return result

    def run(self) -> Optional[Character]:
        """Запускает процесс создания персонажа."""
        self.renderer.clear_screen()
        self.renderer.render_title("Создание персонажа D&D")

        max_attempts = 20  # Ограничиваем количество попыток
        attempts = 0

        while (
            self.current_step != CreationStep.CONFIRMATION and attempts < max_attempts
        ):
            attempts += 1
            try:
                self._handle_current_step()
            except KeyboardInterrupt:
                self._handle_cancellation()
                return None
            except Exception as e:
                self.renderer.render_error(f"Ошибка: {e}")
                self.input_handler.wait_for_enter()
                # При ошибке не меняем шаг, чтобы избежать зацикливания
                # Но ограничиваем количество попыток

        if attempts >= max_attempts:
            self.renderer.render_error(
                "Превышено количество попыток. Создание отменено."
            )
            return None

        # Если достигли CONFIRMATION, обрабатываем финальное подтверждение
        if self.current_step == CreationStep.CONFIRMATION:
            self._handle_confirmation()

        return self.character

    def _handle_current_step(self) -> None:
        """Обрабатывает текущий шаг создания."""
        step_handlers = {
            CreationStep.BASIC_INFO: self._handle_basic_info,
            CreationStep.ADVENTURE_SELECTION: self._handle_adventure_selection,
            CreationStep.RACE: self._handle_race,
            CreationStep.GENERATION_METHOD: self._handle_generation_method,
            CreationStep.ATTRIBUTES: self._handle_attributes,
            CreationStep.CLASS: self._handle_class,
            CreationStep.REVIEW: self._handle_review,
            CreationStep.CONFIRMATION: self._handle_confirmation,
        }

        handler = step_handlers.get(self.current_step)
        if handler:
            handler()

    def _handle_basic_info(self) -> None:
        """Обрабатывает ввод базовой информации."""
        self.renderer.clear_screen()
        self.renderer.render_title("Шаг 1: Базовая информация")

        # Показываем информацию об определении уровня
        level_info = level_resolver.get_level_info()
        
        # Дополнительная информация об активных настройках
        if level_info['active_source'] == "Активная модификация":
            from ....domain.services.game_config import game_config
            active_mods = game_config.get_active_mods_info()
            if active_mods:
                print(f"\nНачальный уровень: {level_info['final_level']}")
                print(f"Активные моды: {', '.join(mod.name for mod in active_mods)}")
            else:
                print(f"\nНачальный уровень: {level_info['final_level']}")
                print(f"Источник: {level_info['active_source']}")
        elif level_info['active_source'] == "Активное приключение":
            from ....domain.services.game_config import game_config
            active_adventure = game_config.get_active_adventure_info()
            if active_adventure:
                print(f"\nНачальный уровень: {level_info['final_level']}")
                # Добавляем (Tutorial) для учебного приключения
                adventure_name = active_adventure.name
                if active_adventure.file_name == "tutorial_adventure.yaml":
                    adventure_name += " (Tutorial)"
                print(f"Активное приключение: {adventure_name}")
            else:
                print(f"\nНачальный уровень: {level_info['final_level']}")
                print(f"Источник: {level_info['active_source']}")
        else:
            print(f"\nНачальный уровень: {level_info['final_level']}")
            print(f"Источник: {level_info['active_source']}")
        
        print("\nУровень персонажа определяется автоматически на основе активных настроек.")

        # Ввод имени с подтверждением
        while True:
            # Ввод имени
            name = self.input_handler.get_string(
                "Введите имя персонажа: ", default=self.temp_name, allow_empty=False
            )

            # Подтверждение имени
            self.renderer.clear_screen()
            self.renderer.render_title("Подтверждение имени")
            print(f"\nВы ввели имя: {name}")
            print("Это имя действительно для вашего персонажа?")
            
            print("\n1. Да, продолжить")
            print("2. Нет, ввести другое имя")
            print("3. Отменить создание")
            
            choice = self.input_handler.get_int(
                "\nВаш выбор: ", min_value=1, max_value=3
            )
            
            if choice == 1:
                # Подтверждено
                self.temp_name = name
                break
            elif choice == 2:
                # Повторить ввод
                continue
            else:
                # Отмена создания
                raise KeyboardInterrupt()

        # Устанавливаем уровень автоматически из резолвера
        self.temp_level = level_resolver.get_starting_level()
        self.builder.set_name(self.temp_name).set_level(self.temp_level)
        
        # Проверяем, нужно ли показывать выбор приключения
        from ....domain.services.game_config import game_config
        non_tutorial_adventures = game_config.get_non_tutorial_adventures()
        
        if non_tutorial_adventures:
            self.current_step = CreationStep.ADVENTURE_SELECTION
        else:
            self.current_step = CreationStep.RACE

    def _handle_adventure_selection(self) -> None:
        """Обрабатывает выбор приключения."""
        self.renderer.clear_screen()
        self.renderer.render_title("Выбор приключения")

        from ....domain.services.game_config import game_config
        
        # Показываем информацию о текущем уровне
        level_info = level_resolver.get_level_info()
        print(f"\nНачальный уровень: {level_info['final_level']}")
        
        active_adventure = game_config.get_active_adventure_info()
        if active_adventure:
            adventure_name = active_adventure.name
            if active_adventure.file_name == "tutorial_adventure.yaml":
                adventure_name += " (Tutorial)"
            print(f"Текущее приключение: {adventure_name}")
        else:
            print(f"Источник: {level_info['active_source']}")
        
        # Получаем доступные приключения
        adventures = game_config.get_available_adventures()
        
        if not adventures:
            print("\nПриключения не найдены. Используется настройка по умолчанию.")
            self.input_handler.wait_for_enter()
            self.current_step = CreationStep.GENERATION_METHOD
            return

        print("\nДоступные приключения:")
        for i, adventure in enumerate(adventures, 1):
            status = "✓" if adventure.is_active else "○"
            level_info = f" (уровень {adventure.starting_level})" if adventure.starting_level else ""
            # Добавляем (Tutorial) для учебного приключения
            adventure_name = adventure.name
            if adventure.file_name == "tutorial_adventure.yaml":
                adventure_name += " (Tutorial)"
            print(f"{i}. {status} {adventure_name}{level_info}")
            print(f"   {adventure.description}")
            print(f"   Сложность: {adventure.difficulty}")

        print(f"\n{len(adventures) + 1}. Использовать настройку по умолчанию")

        choice = self.input_handler.get_int(
            "\nВыберите приключение: ", min_value=1, max_value=len(adventures) + 1
        )

        if choice == len(adventures) + 1:
            # Используем настройку по умолчанию
            print("\nИспользована настройка по умолчанию.")
        else:
            # Выбираем приключение
            selected_adventure = adventures[choice - 1]
            success = game_config.set_active_adventure(selected_adventure.file_name)
            
            if success:
                print(f"\nВыбрано приключение: {selected_adventure.name}")
                # Обновляем уровень после выбора приключения
                self.temp_level = level_resolver.get_starting_level()
                print(f"Начальный уровень обновлен: {self.temp_level}")
            else:
                print(f"\nНе удалось выбрать приключение {selected_adventure.name}")

        self.input_handler.wait_for_enter()
        self.current_step = CreationStep.RACE

    def _handle_generation_method(self) -> None:
        """Обрабатывает выбор метода генерации характеристик."""
        self.renderer.clear_screen()
        self.renderer.render_title("Шаг 3: Метод генерации характеристик")

        methods = AttributeGenerator.get_available_methods()

        print("\nДоступные методы генерации:")
        for i, method in enumerate(methods, 1):
            print(f"{i}. {method.name}")
            print(f"   {method.description}")

        choice = self.input_handler.get_int(
            "\nВыберите метод генерации: ", min_value=1, max_value=len(methods)
        )

        selected_method = methods[choice - 1]
        self.generation_method = selected_method.method_type

        if self.generation_method == GenerationMethod.STANDARD_ARRAY:
            self._handle_standard_array()
        elif self.generation_method == GenerationMethod.FOUR_D6_DROP_LOWEST:
            self._handle_four_d6()
        elif self.generation_method == GenerationMethod.POINT_BUY:
            self._handle_point_buy()

        self.current_step = CreationStep.ATTRIBUTES

    def _handle_standard_array(self) -> None:
        """Обрабатывает генерацию стандартным набором с ручным распределением."""
        self.renderer.clear_screen()
        self.renderer.render_title("Распределение характеристик (стандартный набор)")

        # Получаем доступные значения
        available_values = AttributeGenerator.get_standard_array_values()
        
        # Инициализируем характеристики
        if not self.temp_attributes:
            self.temp_attributes = {}

        max_attempts = 100  # Ограничиваем количество итераций
        attempts = 0

        while len(self.temp_attributes) < len(StandardAttributes.get_all()) and attempts < max_attempts:
            attempts += 1
            
            self.renderer.clear_screen()
            self.renderer.render_title("Распределение характеристик (стандартный набор)")
            
            # Показываем сводку текущего состояния
            self._display_assignment_summary(self.temp_attributes, available_values)
            
            # Показываем нераспределенные характеристики
            unassigned_attrs = [
                attr_name for attr_name in StandardAttributes.get_all().keys()
                if attr_name not in self.temp_attributes
            ]
            
            print("\nВыберите характеристику для распределения:")
            for i, attr_name in enumerate(unassigned_attrs, 1):
                attr_info = StandardAttributes.get_attribute(attr_name)
                print(f"{i}. {attr_info.short_name} ({attr_info.name})")
            
            # Выбор характеристики
            if len(unassigned_attrs) == 0:
                break
                
            choice = self.input_handler.get_int(
                "\nВаш выбор: ", min_value=1, max_value=len(unassigned_attrs)
            )
            
            selected_attr = unassigned_attrs[choice - 1]
            attr_info = StandardAttributes.get_attribute(selected_attr)
            
            # Выбор значения
            print(f"\nДоступные значения для {attr_info.short_name}:")
            sorted_values = sorted(available_values, reverse=True)
            for i, value in enumerate(sorted_values, 1):
                modifier = (value - 10) // 2
                mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                print(f"{i}. {value} ({mod_str})")
            
            print(f"\nВведите номер значения от 1 до {len(sorted_values)}:")
            value_choice = self.input_handler.get_int(
                f"Выбор для {attr_info.short_name}: ",
                min_value=1,
                max_value=len(sorted_values)
            )
            
            selected_value = sorted_values[value_choice - 1]
            
            # Устанавливаем значение
            self.temp_attributes[selected_attr] = selected_value
            available_values.remove(selected_value)
            
            print(f"\n✓ {attr_info.short_name} установлен на {selected_value}")
            self.input_handler.wait_for_enter()

        # Проверяем, что все характеристики распределены
        if len(self.temp_attributes) == len(StandardAttributes.get_all()):
            # Валидация
            if AttributeGenerator.validate_standard_array_assignment(self.temp_attributes):
                # Показываем финальное окно подтверждения
                if self._handle_standard_array_confirmation():
                    self.builder.set_attributes_standard_array_manual(self.temp_attributes)
                else:
                    # Перераспределение - сбрасываем и начинаем заново
                    self.temp_attributes = {}
                    self._handle_standard_array()
            else:
                self.renderer.render_error("Ошибка валидации характеристик")
                self.input_handler.wait_for_enter()
                # Сбрасываем и начинаем заново
                self.temp_attributes = {}
                self._handle_standard_array()
        else:
            self.renderer.render_error("Не все характеристики были распределены")
            self.input_handler.wait_for_enter()

    def _handle_standard_array_confirmation(self) -> bool:
        """Обрабатывает финальное подтверждение стандартного распределения."""
        self.renderer.clear_screen()
        self.renderer.render_title("Подтверждение характеристик")
        
        print("\nВаши характеристики (стандартный набор):")
        self._display_attributes(self.temp_attributes)
        
        print("\n1. Подтвердить выбор")
        print("2. Перераспределить характеристики")
        
        choice = self.input_handler.get_int(
            "\nВаш выбор: ", min_value=1, max_value=2
        )
        
        return choice == 1

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
            self.temp_attributes = {
                attr: 10 for attr in StandardAttributes.get_all().keys()
            }

        costs = AttributeGenerator.get_point_buy_costs()

        max_attempts = 50  # Ограничиваем количество итераций для point_buy
        attempts = 0

        while attempts < max_attempts:
            attempts += 1
            self.point_buy_remaining = (
                AttributeGenerator.get_point_buy_remaining_points(self.temp_attributes)
            )

            print(f"\nОсталось очков: {self.point_buy_remaining}")
            print("\nТекущие характеристики:")

            for i, (attr_name, value) in enumerate(self.temp_attributes.items()):
                attr_info = StandardAttributes.get_attribute(attr_name)
                cost = costs.get(value, 0)
                print(f"{i + 1}. {attr_info.short_name}: {value} (стоимость: {cost})")

            print("\nВыберите характеристику для изменения или 0 для продолжения:")
            choice = self.input_handler.get_int("Ваш выбор: ", min_value=0, max_value=6)

            if choice == 0:
                if AttributeGenerator.validate_point_buy_attributes(
                    self.temp_attributes
                ):
                    break
                else:
                    self.renderer.render_error(
                        "Невалидные характеристики! Используйте все очки."
                    )
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
                default=current_value,
            )

            self.temp_attributes[selected_attr] = new_value

        self.builder.set_attributes_point_buy(self.temp_attributes)

    def _handle_attributes(self) -> None:
        """Обрабатывает шаг характеристик (уже установлены)."""
        # Характеристики уже установлены на предыдущем шаге
        # Просто переходим к выбору класса
        self.current_step = CreationStep.CLASS

    def _display_race_info(self, race_key: str, race_name: str, choice_num: int, subrace_key: str = None, short: bool = False) -> None:
        """Отображает информацию о расе с описанием и бонусами.
        
        Args:
            race_key: Ключ расы
            race_name: Название расы
            choice_num: Номер выбора
            subrace_key: Ключ подрасы (опционально)
            short: Показывать короткое описание (для списков)
        """
        # Получаем отформатированную информацию из универсальной фабрики
        info = UniversalRaceFactory.get_formatted_race_info(race_key, subrace_key)
        
        print(f"{choice_num}. {info['name']}")
        
        if short:
            # Короткое описание для списка с переносами
            description = info['short_description']
            formatted_desc = self._format_text_with_wrapping(description, width=50, indent="   📖 ")
            print(formatted_desc)
        else:
            # Полное описание с переносами
            description = info['description']
            formatted_desc = self._format_text_with_wrapping(description, width=50, indent="   📖 ")
            print(formatted_desc)
        
        # Показываем бонусы
        if info['bonuses']:
            print(info['bonuses'])
        
        # Показываем особенности для подрас всегда, а для основных рас только при full режиме
        if (subrace_key is not None or not short) and info['features']:
            print(info['features'])
        print()

    def _show_race_details(self, race_key: str, subrace_key: str = None) -> None:
        """Показывает детальную информацию о расе для подтверждения выбора.
        
        Args:
            race_key: Ключ расы
            subrace_key: Ключ подрасы (опционально)
        """
        self.renderer.clear_screen()
        self.renderer.render_title("Детальная информация о расе")
        
        if subrace_key:
            # Показываем информацию о конкретной подрасе
            info = UniversalRaceFactory.get_formatted_race_info(race_key, subrace_key)
            
            print(f"\n🧬 {info['name']}")
            print("=" * 50)
            print(f"\n📖 {info['description']}")
            
            # Показываем бонусы подрасы
            if info['bonuses']:
                # Добавляем заголовок "🎯 Бонусы:" перед бонусами
                bonus_lines = info['bonuses'].strip().split('\n')
                if bonus_lines and not any(line.startswith('🎯 Бонусы:') for line in bonus_lines):
                    # Если нет заголовка, добавляем его
                    print(f"\n🎯 Бонусы:")
                    for line in bonus_lines:
                        if line.strip():
                            print(f"   {line.strip()}")
                else:
                    # Если заголовок уже есть, выводим как есть
                    print(f"\n{info['bonuses']}")
            
            # Показываем особенности
            if info['features']:
                print(f"\n✨ Особенности:")
                print(info['features'])
        else:
            # Показываем информацию о расе и список подрас (без деталей)
            subrace_choices = UniversalRaceFactory.get_subrace_choices(race_key)
            
            if len(subrace_choices) > 1:
                # Есть подрасы - показываем информацию о расе и все особенности
                info = UniversalRaceFactory.get_formatted_race_info(race_key)
                
                print(f"\n{info['name']}")
                print("=" * 50)
                print(f"\n{info['description']}")
                
                # Показываем общие бонусы для основной расы
                if info['bonuses']:
                    print(f"\nОбщие бонусы:")
                    print(info['bonuses'])
                
                # Показываем все особенности основной расы
                if info['features']:
                    print(f"\n✨ Особенности:")
                    print(info['features'])
                
                print(f"\nДоступные варианты:")
                
                for choice_num, subrace_name in subrace_choices.items():
                    print(f"   {choice_num}. {subrace_name}")
            else:
                # Нет подрас - показываем информацию о расе
                info = UniversalRaceFactory.get_formatted_race_info(race_key)
                
                print(f"\n🧬 {info['name']}")
                print("=" * 50)
                print(f"\n📖 {info['description']}")
                
                # Показываем бонусы
                if info['bonuses']:
                    print(f"\nОбщие бонусы:")
                    print(info['bonuses'])
                
                # Показываем особенности
                if info['features']:
                    print(f"\n✨ Особенности:")
                    print(info['features'])
        
        print("\n" + "=" * 50)

    def _handle_race(self) -> None:
        """Обрабатывает выбор расы."""
        self.renderer.clear_screen()
        self.renderer.render_title("Шаг 2: Выбор расы")

        # Выбор расы
        race_choices = UniversalRaceFactory.get_race_choices()
        print("\nДоступные расы:")
        print()
        
        # Показываем информацию о каждой расе
        for choice_num, race_name in race_choices.items():
            race_key = UniversalRaceFactory.get_race_key_by_choice(int(choice_num))
            if race_key:
                self._display_race_info(race_key, race_name, int(choice_num), short=True)

        race_choice = self.input_handler.get_int(
            "\nВыберите расу: ", min_value=1, max_value=len(race_choices)
        )
        # Получаем ключ расы по номеру выбора
        race_key = UniversalRaceFactory.get_race_key_by_choice(race_choice)
        
        # Показываем детальную информацию о выбранной расе
        self._show_race_details(race_key)
        
        # Подтверждение выбора расы
        print("\n1. ✅ Выбрать эту расу")
        print("2. 🔄 Вернуться к списку рас")
        print("3. ❌ Отменить создание персонажа")
        
        confirm_choice = self.input_handler.get_int(
            "\nВаш выбор: ", min_value=1, max_value=3
        )
        
        if confirm_choice == 2:
            # Возвращаемся к выбору расы
            self._handle_race()
            return
        elif confirm_choice == 3:
            # Отмена создания
            raise KeyboardInterrupt()
        
        # Проверяем наличие подрас
        subrace_choices = UniversalRaceFactory.get_subrace_choices(race_key)
        
        if len(subrace_choices) > 1:  # Есть подрасы (только подрасы, без основной расы)
            while True:  # Цикл для возможности возврата к выбору подрасы
                self.renderer.clear_screen()
                self.renderer.render_title("Выбор подрасы")
                
                # Показываем краткую информацию о расе
                base_info = UniversalRaceFactory.get_formatted_race_info(race_key)
                print(f"\n🧬 Раса: {base_info['name']}")
                print(f"📖 {base_info['short_description']}")
                
                # Показываем общие бонусы основной расы
                if base_info['bonuses']:
                    print(f"Общие бонусы:")
                    print(base_info['bonuses'])
                
                print(f"\nДоступные варианты:")
                print()
                
                for choice_num, subrace_name in subrace_choices.items():
                    # Получаем ключ подрасы
                    subrace_key = UniversalRaceFactory.get_subrace_key_by_choice(race_key, int(choice_num))
                    
                    if subrace_key:
                        # Получаем информацию о подрасе
                        subrace_info = UniversalRaceFactory.get_formatted_race_info(race_key, subrace_key)
                        print(f"{choice_num}. {subrace_info['name']}")
                        
                        # Форматируем описание с переносами
                        formatted_desc = self._format_text_with_wrapping(
                            subrace_info['short_description'], width=50, indent="   📖 "
                        )
                        print(formatted_desc)
                        print()  # Пустая строка после описания
                        
                        # Показываем бонусы подрасы
                        if subrace_info['bonuses']:
                            # Форматируем бонусы в нужный формат
                            bonus_lines = subrace_info['bonuses'].strip().split('\n')
                            if bonus_lines:
                                # Собираем все бонусы в одну строку
                                bonus_parts = []
                                for line in bonus_lines:
                                    line = line.strip()
                                    if line.startswith('🎯 '):
                                        # Извлекаем название характеристики и значение
                                        parts = line.replace('🎯 ', '').split(': ')
                                        if len(parts) == 2:
                                            # Убираем возможные лишние эмодзи из названия
                                            clean_name = parts[0].replace('🎯 ', '').strip()
                                            bonus_parts.append(f"{clean_name} {parts[1]}")
                                
                                if bonus_parts:
                                    print(f"   🎯 Бонусы: {', '.join(bonus_parts)}")
                        
                        # Показываем особенности подрасы
                        if subrace_info['features']:
                            print("   ✨ Особенности:")
                            # Форматируем особенности без лишних табуляций
                            feature_lines = subrace_info['features'].split('\n')
                            for line in feature_lines:
                                line = line.strip()
                                if line:
                                    # Убираем табуляцию в начале
                                    if line.startswith('\t'):
                                        line = line[1:]
                                    # Добавляем правильный отступ
                                    print(f"   \t{line}")
                        
                        print()

                subrace_choice = self.input_handler.get_int(
                    f"\nВыберите вариант расы: ", min_value=1, max_value=len(subrace_choices)
                )
                
                # Получаем ключ подрасы
                subrace_key = UniversalRaceFactory.get_subrace_key_by_choice(race_key, subrace_choice)
                
                # Показываем детальную информацию о выбранной подрасе
                self._show_race_details(race_key, subrace_key)
                
                # Подтверждение выбора подрасы
                print("\n1. ✅ Выбрать этот вариант")
                print("2. 🔄 Вернуться к списку вариантов")
                print("3. ❌ Отменить создание персонажа")
                
                confirm_choice = self.input_handler.get_int(
                    "\nВаш выбор: ", min_value=1, max_value=3
                )
                
                if confirm_choice == 1:
                    # Подтверждено - всегда используем подрасу для рас с подрасами
                    self.temp_race = f"{race_key}.{subrace_key}"
                    break
                elif confirm_choice == 2:
                    # Возвращаемся к выбору подрасы
                    continue
                else:
                    # Отмена создания
                    raise KeyboardInterrupt()
        else:
            # Подрас нет, используем основную расу
            self.temp_race = race_key

        # Устанавливаем расу в билдере
        self.builder.set_race(self.temp_race)
        
        # Переходим к выбору метода генерации характеристик
        self.current_step = CreationStep.GENERATION_METHOD

    def _handle_class(self) -> None:
        """Обрабатывает выбор класса."""
        self.renderer.clear_screen()
        self.renderer.render_title("Шаг 4: Выбор класса")

        # Выбор класса
        class_choices = CharacterClassFactory.get_class_choices()
        print("\nДоступные классы:")
        for choice_num, class_name in class_choices.items():
            print(f"{choice_num}. {class_name}")

        class_choice = self.input_handler.get_int(
            "\nВыберите класс: ", min_value=1, max_value=len(class_choices)
        )
        # Получаем ключ класса по номеру выбора
        class_key = CharacterClassFactory.get_class_key_by_choice(class_choice)
        self.temp_class = class_key

        self.builder.set_class(self.temp_class)
        self.current_step = CreationStep.REVIEW

    def _handle_review(self) -> None:
        """Обрабатывает просмотр и подтверждение персонажа."""
        self.renderer.clear_screen()
        self.renderer.render_title("Шаг 5: Просмотр персонажа")

        # Создаем персонажа для предпросмотра
        try:
            self.character = self.builder.build()
            self._display_character_summary(self.character)

            print("\n1. Сохранить персонажа")
            print("2. Вернуться к настройкам")
            print("3. Отменить создание")

            choice = self.input_handler.get_int(
                "\nВаш выбор: ", min_value=1, max_value=3
            )

            if choice == 1:
                self.current_step = CreationStep.CONFIRMATION
            elif choice == 2:
                self.current_step = CreationStep.RACE
            else:
                raise KeyboardInterrupt()

        except KeyboardInterrupt:
            # Не перехватываем KeyboardInterrupt - передаем выше
            raise
        except Exception as e:
            self.renderer.render_error(f"Ошибка при создании персонажа: {e}")
            self.input_handler.wait_for_enter()
            self.current_step = CreationStep.RACE

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

    def _display_available_values(self, values: List[int]) -> None:
        """Отображает доступные значения с модификаторами и нумерацией."""
        print("\nДоступные значения:")
        sorted_values = sorted(values, reverse=True)
        for i, value in enumerate(sorted_values, 1):
            modifier = (value - 10) // 2
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            print(f"  {i}. {value} ({mod_str})")

    def _display_assignment_summary(self, attributes: Dict[str, int], remaining_values: List[int]) -> None:
        """Отображает сводку текущего распределения."""
        print("\n=== Текущее распределение ===")
        
        if attributes:
            print("\nУстановленные характеристики:")
            self._display_attributes(attributes)
        
        if remaining_values:
            print("\nОставшиеся значения:")
            for value in sorted(remaining_values, reverse=True):
                modifier = (value - 10) // 2
                mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                print(f"  {value} ({mod_str})")
        
        # Показываем нераспределенные характеристики
        all_attrs = set(StandardAttributes.get_all().keys())
        assigned_attrs = set(attributes.keys())
        unassigned_attrs = all_attrs - assigned_attrs
        
        if unassigned_attrs:
            print("\nНераспределенные характеристики:")
            for attr_name in sorted(unassigned_attrs):
                attr_info = StandardAttributes.get_attribute(attr_name)
                print(f"  {attr_info.short_name} ({attr_info.name})")
        
        print("=" * 30)

    def _display_character_summary(self, character: Character) -> None:
        """Отображает сводку персонажа."""
        print(f"\n=== {character.name} ===")
        print(f"Раса: {character.race.name}")
        print(f"Класс: {character.character_class.name}")
        print(f"Уровень: {character.level}")

        print("\nХарактеристики:")
        modifiers = character.get_all_modifiers()
        for attr_name in [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]:
            attr_info = StandardAttributes.get_attribute(attr_name)
            value = getattr(character, attr_name).value
            modifier = modifiers[attr_name]
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            print(f"  {attr_info.short_name}: {value} ({mod_str})")

        print("\nПроизводные характеристики:")
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
        # Определяем уровень через резолвер
        starting_level = level_resolver.get_starting_level()
        return CharacterFactory.create_standard_character(name, starting_level)

    def create_default_character(self) -> Character:
        """Создает персонажа по умолчанию с 1 уровнем."""
        return CharacterFactory.create_standard_character("Безымянный", 1)


# Пример использования
if __name__ == "__main__":
    # Для тестирования потребуется мокинг InputHandler и Renderer
    print("Модуль создания персонажа готов к использованию")
