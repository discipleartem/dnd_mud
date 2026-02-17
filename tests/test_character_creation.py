"""
Тесты для меню создания персонажа.

Тестируем:
- Пошаговое создание персонажа
- Ввод базовой информации
- Генерацию характеристик
- Выбор расы и класса
- Просмотр и подтверждение
- Обработку ошибок и отмену
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Добавляем src в Python path для тестов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.infrastructure.ui.menus.character_creation import (
    CharacterCreationMenu, CharacterCreationController, CreationStep
)
from src.domain.services.character_generation import GenerationMethod
from src.domain.entities.character import Character

pytestmark = pytest.mark.unit


class TestCharacterCreationMenu:
    """Тесты меню создания персонажа."""
    
    def setup_method(self):
        """Настраивает тесты."""
        self.mock_input_handler = Mock()
        self.mock_renderer = Mock()
        self.menu = CharacterCreationMenu(self.mock_input_handler, self.mock_renderer)
    
    def test_initialization(self):
        """Тестирует инициализацию меню."""
        assert self.menu.input_handler == self.mock_input_handler
        assert self.menu.renderer == self.mock_renderer
        assert self.menu.current_step == CreationStep.BASIC_INFO
        assert self.menu.character is None
        assert self.menu.temp_name == ""
        assert self.menu.temp_level == 1
        assert self.menu.temp_race == "human"
        assert self.menu.temp_class == "fighter"
        assert self.menu.generation_method is None
    
    @patch('src.infrastructure.ui.menus.character_creation.CharacterBuilder')
    def test_run_successful_creation(self, mock_builder_class):
        """Тестирует успешное создание персонажа."""
        # Настройка моков
        mock_builder = Mock()
        mock_character = Mock(spec=Character)
        mock_builder.build.return_value = mock_character
        mock_builder_class.return_value = mock_builder
        
        # Создаем новое меню с замоканным CharacterBuilder
        menu = CharacterCreationMenu(self.mock_input_handler, self.mock_renderer)
        menu.builder = mock_builder
        
        # Мокаем обработчики шагов
        menu._handle_basic_info = Mock()
        menu._handle_generation_method = Mock()
        menu._handle_race_class = Mock()
        menu._handle_review = Mock()
        menu._handle_confirmation = Mock()
        
        # Настраиваем переходы между шагами
        menu._handle_basic_info.side_effect = lambda: setattr(menu, 'current_step', CreationStep.GENERATION_METHOD)
        menu._handle_generation_method.side_effect = lambda: setattr(menu, 'current_step', CreationStep.RACE_CLASS)
        menu._handle_race_class.side_effect = lambda: setattr(menu, 'current_step', CreationStep.REVIEW)
        menu._handle_review.side_effect = lambda: setattr(menu, 'current_step', CreationStep.CONFIRMATION)
        
        result = menu.run()
        
        assert result == mock_character
        menu._handle_basic_info.assert_called_once()
        menu._handle_generation_method.assert_called_once()
        menu._handle_race_class.assert_called_once()
        menu._handle_review.assert_called_once()
        menu._handle_confirmation.assert_called_once()
    
    def test_run_keyboard_interrupt(self):
        """Тестирует обработку KeyboardInterrupt."""
        menu = CharacterCreationMenu(self.mock_input_handler, self.mock_renderer)
        menu._handle_cancellation = Mock()
        
        # Мокаем первый шаг, чтобы вызвать KeyboardInterrupt
        menu._handle_basic_info = Mock(side_effect=KeyboardInterrupt())
        
        result = menu.run()
        
        assert result is None
        menu._handle_cancellation.assert_called_once()
    
    def test_run_general_exception(self):
        """Тестирует обработку общих исключений."""
        menu = CharacterCreationMenu(self.mock_input_handler, self.mock_renderer)
        menu._handle_basic_info = Mock(side_effect=Exception("Тестовая ошибка"))
        menu._handle_cancellation = Mock()
        
        # Мокаем wait_for_enter чтобы избежать зацикливания
        self.mock_input_handler.wait_for_enter.return_value = None
        
        result = menu.run()
        
        assert result is None
        self.mock_renderer.render_error.assert_called_once()
    
    def test_handle_basic_info(self):
        """Тестирует обработку базовой информации."""
        self.mock_input_handler.get_string.return_value = "Тестовый персонаж"
        self.mock_input_handler.get_int.return_value = 5
        
        self.menu._handle_basic_info()
        
        assert self.menu.temp_name == "Тестовый персонаж"
        assert self.menu.temp_level == 5
        assert self.menu.current_step == CreationStep.GENERATION_METHOD
        self.mock_input_handler.get_string.assert_called_once()
        self.mock_input_handler.get_int.assert_called_once()
    
    def test_handle_basic_info_with_defaults(self):
        """Тестирует обработку базовой информации со значениями по умолчанию."""
        self.menu.temp_name = "Существующее имя"
        self.menu.temp_level = 10
        
        self.mock_input_handler.get_string.return_value = "Существующее имя"
        self.mock_input_handler.get_int.return_value = 10
        
        self.menu._handle_basic_info()
        
        assert self.menu.temp_name == "Существующее имя"
        assert self.menu.temp_level == 10
    
    @patch('src.infrastructure.ui.menus.character_creation.AttributeGenerator')
    def test_handle_generation_method(self, mock_generator):
        """Тестирует обработку выбора метода генерации."""
        # Настройка моков
        mock_method = Mock()
        mock_method.name = "Стандартный набор"
        mock_method.description = "Описание"
        mock_method.method_type = GenerationMethod.STANDARD_ARRAY
        
        mock_generator.get_available_methods.return_value = [mock_method]
        self.mock_input_handler.get_int.return_value = 1
        
        self.menu._handle_standard_array = Mock()
        
        self.menu._handle_generation_method()
        
        assert self.menu.generation_method == GenerationMethod.STANDARD_ARRAY
        assert self.menu.current_step == CreationStep.RACE_CLASS
        self.menu._handle_standard_array.assert_called_once()
    
    @patch('src.infrastructure.ui.menus.character_creation.AttributeGenerator')
    def test_handle_generation_method_four_d6(self, mock_generator):
        """Тестирует выбор метода 4d6."""
        mock_method = Mock()
        mock_method.method_type = GenerationMethod.FOUR_D6_DROP_LOWEST
        mock_generator.get_available_methods.return_value = [mock_method]
        self.mock_input_handler.get_int.return_value = 1
        
        self.menu._handle_four_d6 = Mock()
        
        self.menu._handle_generation_method()
        
        assert self.menu.generation_method == GenerationMethod.FOUR_D6_DROP_LOWEST
        self.menu._handle_four_d6.assert_called_once()
    
    @patch('src.infrastructure.ui.menus.character_creation.AttributeGenerator')
    def test_handle_generation_method_point_buy(self, mock_generator):
        """Тестирует выбор метода покупки очков."""
        mock_method = Mock()
        mock_method.method_type = GenerationMethod.POINT_BUY
        mock_generator.get_available_methods.return_value = [mock_method]
        self.mock_input_handler.get_int.return_value = 1
        
        self.menu._handle_point_buy = Mock()
        
        self.menu._handle_generation_method()
        
        assert self.menu.generation_method == GenerationMethod.POINT_BUY
        self.menu._handle_point_buy.assert_called_once()
    
    @patch('src.infrastructure.ui.menus.character_creation.AttributeGenerator')
    def test_handle_standard_array(self, mock_generator):
        """Тестирует генерацию стандартным набором."""
        test_attributes = {'strength': 15, 'dexterity': 14, 'constitution': 13,
                         'intelligence': 12, 'wisdom': 10, 'charisma': 8}
        mock_generator.generate_standard_array.return_value = test_attributes
        
        self.mock_input_handler.wait_for_enter.return_value = None
        
        self.menu._handle_standard_array()
        
        assert self.menu.temp_attributes == test_attributes
        self.mock_renderer.render_title.assert_called_with("Характеристики сгенерированы")
    
    @patch('src.infrastructure.ui.menus.character_creation.AttributeGenerator')
    def test_handle_four_d6(self, mock_generator):
        """Тестирует генерацию методом 4d6."""
        test_attributes = {'strength': 16, 'dexterity': 13, 'constitution': 14,
                         'intelligence': 11, 'wisdom': 12, 'charisma': 9}
        mock_generator.generate_four_d6_drop_lowest.return_value = test_attributes
        
        self.mock_input_handler.wait_for_enter.return_value = None
        
        self.menu._handle_four_d6()
        
        assert self.menu.temp_attributes == test_attributes
        self.mock_renderer.render_title.assert_called_with("Характеристики сгенерированы")
    
    @patch('src.infrastructure.ui.menus.character_creation.AttributeGenerator')
    @patch('src.infrastructure.ui.menus.character_creation.StandardAttributes')
    def test_handle_point_buy(self, mock_attributes, mock_generator):
        """Тестирует покупку очков."""
        # Настройка моков
        test_attributes = {'strength': 10, 'dexterity': 10, 'constitution': 10,
                         'intelligence': 10, 'wisdom': 10, 'charisma': 10}
        mock_attributes.get_all.return_value.keys.return_value = test_attributes.keys()
        mock_generator.get_point_buy_costs.return_value = {10: 0, 11: 1, 12: 2}
        mock_generator.get_point_buy_remaining_points.return_value = 27
        mock_generator.validate_point_buy_attributes.return_value = True
        
        self.mock_input_handler.get_int.side_effect = [0]  # Сразу выходим
        
        self.menu.temp_attributes = test_attributes.copy()
        self.menu._handle_point_buy()
        
        # Проверяем, что характеристики остались без изменений
        assert self.menu.temp_attributes == test_attributes
    
    @patch('src.infrastructure.ui.menus.character_creation.RaceFactory')
    @patch('src.infrastructure.ui.menus.character_creation.CharacterClassFactory')
    def test_handle_race_class(self, mock_class_factory, mock_race_factory):
        """Тестирует выбор расы и класса."""
        # Настройка моков
        mock_race = Mock()
        mock_race.name = "Эльф"
        mock_char_class = Mock()
        mock_char_class.name = "Волшебник"
        
        mock_race_factory.get_available_races.return_value = [mock_race]
        mock_class_factory.get_available_classes.return_value = [mock_char_class]
        
        self.mock_input_handler.get_int.side_effect = [1, 1]  # Выбираем первую расу и класс
        
        self.menu._handle_race_class()
        
        assert self.menu.temp_race == "Эльф"
        assert self.menu.temp_class == "Волшебник"
        assert self.menu.current_step == CreationStep.REVIEW
    
    def test_handle_review_save_character(self):
        """Тестирует просмотр и сохранение персонажа."""
        # Настройка мока персонажа
        mock_character = Mock(spec=Character)
        mock_character.name = "Тестовый персонаж"
        mock_character.race.name = "Человек"
        mock_character.character_class.name = "Воин"
        mock_character.level = 1
        mock_character.hp_current = 10
        mock_character.hp_max = 10
        mock_character.ac = 12
        mock_character.get_all_modifiers.return_value = {
            'strength': 1, 'dexterity': 0, 'constitution': 1,
            'intelligence': 0, 'wisdom': 0, 'charisma': 0
        }
        mock_character.get_proficiency_bonus.return_value = 2
        
        self.menu.builder = Mock()
        self.menu.builder.build.return_value = mock_character
        self.mock_input_handler.get_int.return_value = 1  # Сохранить
        
        self.menu._handle_review()
        
        assert self.menu.character == mock_character
        assert self.menu.current_step == CreationStep.CONFIRMATION
    
    def test_handle_review_return_to_settings(self):
        """Тестирует возврат к настройкам из просмотра."""
        mock_character = Mock(spec=Character)
        self.menu.builder = Mock()
        self.menu.builder.build.return_value = mock_character
        self.mock_input_handler.get_int.return_value = 2  # Вернуться к настройкам
        
        self.menu._handle_review()
        
        assert self.menu.current_step == CreationStep.BASIC_INFO
    
    def test_handle_review_cancel(self):
        """Тестирует отмену создания из просмотра."""
        mock_character = Mock(spec=Character)
        self.menu.builder = Mock()
        self.menu.builder.build.return_value = mock_character
        self.mock_input_handler.get_int.return_value = 3  # Отменить
        
        with pytest.raises(KeyboardInterrupt):
            self.menu._handle_review()
    
    def test_handle_review_build_error(self):
        """Тестирует ошибку при сборке персонажа."""
        self.menu.builder = Mock()
        self.menu.builder.build.side_effect = Exception("Ошибка сборки")
        self.mock_input_handler.wait_for_enter.return_value = None
        
        self.menu._handle_review()
        
        assert self.menu.current_step == CreationStep.BASIC_INFO
        self.mock_renderer.render_error.assert_called_once()
    
    def test_handle_confirmation(self):
        """Тестирует финальное подтверждение."""
        mock_character = Mock(spec=Character)
        mock_character.name = "Тестовый персонаж"
        mock_character.race.name = "Человек"
        mock_character.character_class.name = "Воин"
        mock_character.level = 1
        
        self.menu.character = mock_character
        self.mock_input_handler.wait_for_enter.return_value = None
        
        self.menu._handle_confirmation()
        
        self.mock_renderer.render_success.assert_called_once_with("Персонаж успешно создан!")
    
    def test_handle_cancellation(self):
        """Тестирует обработку отмены."""
        self.menu._handle_cancellation()
        self.mock_renderer.render_info.assert_called_once_with("Создание персонажа отменено")
    
    @patch('src.infrastructure.ui.menus.character_creation.StandardAttributes')
    def test_display_attributes(self, mock_attributes):
        """Тестирует отображение характеристик."""
        # Настройка мока
        mock_attr_info = Mock()
        mock_attr_info.short_name = "СИЛ"
        mock_attributes.get_attribute.return_value = mock_attr_info
        
        test_attributes = {'strength': 15}
        
        # Перехватываем вывод print
        with patch('builtins.print') as mock_print:
            self.menu._display_attributes(test_attributes)
            
            # Проверяем, что print был вызван с правильными данными
            mock_print.assert_called()
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("СИЛ: 15 (+2)" in call for call in calls)
    
    @patch('src.infrastructure.ui.menus.character_creation.StandardAttributes')
    def test_display_character_summary(self, mock_attributes):
        """Тестирует отображение сводки персонажа."""
        # Настройка мока персонажа
        mock_character = Mock(spec=Character)
        mock_character.name = "Тестовый персонаж"
        mock_character.race.name = "Человек"
        mock_character.character_class.name = "Воин"
        mock_character.level = 1
        mock_character.hp_current = 10
        mock_character.hp_max = 10
        mock_character.ac = 12
        mock_character.get_all_modifiers.return_value = {'strength': 1}
        mock_character.get_proficiency_bonus.return_value = 2
        mock_character.strength.value = 12
        
        mock_attr_info = Mock()
        mock_attr_info.short_name = "СИЛ"
        mock_attributes.get_attribute.return_value = mock_attr_info
        
        with patch('builtins.print') as mock_print:
            self.menu._display_character_summary(mock_character)
            
            mock_print.assert_called()
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Тестовый персонаж" in call for call in calls)
            assert any("Человек" in call for call in calls)
            assert any("Воин" in call for call in calls)


class TestCharacterCreationController:
    """Тесты контроллера создания персонажа."""
    
    def setup_method(self):
        """Настраивает тесты."""
        self.mock_input_handler = Mock()
        self.mock_renderer = Mock()
        self.controller = CharacterCreationController(self.mock_input_handler, self.mock_renderer)
    
    def test_initialization(self):
        """Тестирует инициализацию контроллера."""
        assert self.controller.input_handler == self.mock_input_handler
        assert self.controller.renderer == self.mock_renderer
    
    @patch('src.infrastructure.ui.menus.character_creation.CharacterCreationMenu')
    def test_create_character(self, mock_menu_class):
        """Тестирует создание персонажа."""
        mock_menu = Mock()
        mock_character = Mock(spec=Character)
        mock_menu.run.return_value = mock_character
        mock_menu_class.return_value = mock_menu
        
        result = self.controller.create_character()
        
        assert result == mock_character
        mock_menu_class.assert_called_once_with(self.mock_input_handler, self.mock_renderer)
        mock_menu.run.assert_called_once()
    
    @patch('src.infrastructure.ui.menus.character_creation.CharacterCreationMenu')
    def test_create_character_cancellation(self, mock_menu_class):
        """Тестирует отмену создания персонажа."""
        mock_menu = Mock()
        mock_menu.run.return_value = None
        mock_menu_class.return_value = mock_menu
        
        result = self.controller.create_character()
        
        assert result is None
    
    @patch('src.infrastructure.ui.menus.character_creation.CharacterFactory')
    def test_create_quick_character(self, mock_factory):
        """Тестирует быстрое создание персонажа."""
        mock_character = Mock(spec=Character)
        mock_factory.create_standard_character.return_value = mock_character
        
        result = self.controller.create_quick_character("Быстрый персонаж")
        
        assert result == mock_character
        mock_factory.create_standard_character.assert_called_once_with("Быстрый персонаж")
    
    @patch('src.infrastructure.ui.menus.character_creation.CharacterFactory')
    def test_create_quick_character_default_name(self, mock_factory):
        """Тестирует быстрое создание персонажа с именем по умолчанию."""
        mock_character = Mock(spec=Character)
        mock_factory.create_standard_character.return_value = mock_character
        
        result = self.controller.create_quick_character()
        
        assert result == mock_character
        mock_factory.create_standard_character.assert_called_once_with("Безымянный")


class TestCreationStep:
    """Тесты шагов создания."""
    
    def test_creation_step_values(self):
        """Тестирует значения шагов создания."""
        assert CreationStep.BASIC_INFO.value == "basic_info"
        assert CreationStep.GENERATION_METHOD.value == "generation_method"
        assert CreationStep.ATTRIBUTES.value == "attributes"
        assert CreationStep.RACE_CLASS.value == "race_class"
        assert CreationStep.REVIEW.value == "review"
        assert CreationStep.CONFIRMATION.value == "confirmation"
    
    def test_creation_step_uniqueness(self):
        """Тестирует уникальность шагов создания."""
        values = [step.value for step in CreationStep]
        assert len(values) == len(set(values))


class TestCharacterCreationIntegration:
    """Интеграционные тесты создания персонажа."""
    
    @patch('src.infrastructure.ui.menus.character_creation.RaceFactory')
    @patch('src.infrastructure.ui.menus.character_creation.CharacterClassFactory')
    @patch('src.infrastructure.ui.menus.character_creation.AttributeGenerator')
    @patch('src.infrastructure.ui.menus.character_creation.CharacterBuilder')
    def test_full_creation_flow(self, mock_builder_class, mock_generator, 
                               mock_class_factory, mock_race_factory):
        """Тестирует полный поток создания персонажа."""
        # Настройка всех моков
        mock_builder = Mock()
        mock_character = Mock(spec=Character)
        mock_builder.build.return_value = mock_character
        mock_builder_class.return_value = mock_builder
        
        mock_method = Mock()
        mock_method.method_type = GenerationMethod.STANDARD_ARRAY
        mock_generator.get_available_methods.return_value = [mock_method]
        mock_generator.generate_standard_array.return_value = {
            'strength': 15, 'dexterity': 14, 'constitution': 13,
            'intelligence': 12, 'wisdom': 10, 'charisma': 8
        }
        
        mock_race = Mock()
        mock_race.name = "Человек"
        mock_race_factory.get_available_races.return_value = [mock_race]
        
        mock_char_class = Mock()
        mock_char_class.name = "Воин"
        mock_class_factory.get_available_classes.return_value = [mock_char_class]
        
        # Настройка input handler
        mock_input_handler = Mock()
        mock_input_handler.get_string.return_value = "Интеграционный тест"
        mock_input_handler.get_int.side_effect = [1, 1, 1, 1]  # level, method, race, class, save
        mock_input_handler.wait_for_enter.return_value = None
        
        # Настройка renderer
        mock_renderer = Mock()
        
        # Создаем меню и запускаем пошагово
        menu = CharacterCreationMenu(mock_input_handler, mock_renderer)
        
        # Шаг 1: Базовая информация
        menu._handle_basic_info()
        assert menu.temp_name == "Интеграционный тест"
        assert menu.current_step == CreationStep.GENERATION_METHOD
        
        # Шаг 2: Метод генерации
        menu._handle_generation_method()
        assert menu.generation_method == GenerationMethod.STANDARD_ARRAY
        assert menu.current_step == CreationStep.RACE_CLASS
        
        # Шаг 3: Раса и класс
        menu._handle_race_class()
        assert menu.temp_race == "Человек"
        assert menu.temp_class == "Воин"
        assert menu.current_step == CreationStep.REVIEW
        
        # Проверяем, что все зависимости были вызваны
        mock_generator.get_available_methods.assert_called_once()
        mock_generator.generate_standard_array.assert_called_once()
        mock_race_factory.get_available_races.assert_called_once()
        mock_class_factory.get_available_classes.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
