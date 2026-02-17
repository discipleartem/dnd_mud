"""
Тесты для меню персонажа (CharacterMenu).

Тестируем:
- Инициализацию меню
- Основные методы
- Обработку исключений
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Добавляем src в Python path для тестов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.infrastructure.ui.menus.character_menu import CharacterMenu

pytestmark = pytest.mark.unit


class TestCharacterMenu:
    """Тесты меню персонажа."""

    def setup_method(self):
        """Настраивает тесты."""
        self.menu = CharacterMenu()
        
    def test_initialization(self):
        """Тестирует инициализацию меню."""
        assert self.menu.character is None
        assert self.menu.current_step == 0
        assert self.menu.max_steps == 5

    @patch("src.infrastructure.ui.menus.character_menu.renderer")
    def test_show(self, mock_renderer):
        """Тестирует отображение меню."""
        self.menu.show()
        
        mock_renderer.clear_screen.assert_called_once()
        mock_renderer.show_title.assert_called_once_with("=== СОЗДАНИЕ ПЕРСОНАЖА ===")

    @patch("builtins.input")
    @patch("src.infrastructure.ui.menus.character_menu.renderer")
    def test_get_choice_keyboard_interrupt(self, mock_renderer, mock_input):
        """Тестирует обработку KeyboardInterrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        
        result = self.menu.get_choice("Тест", 5)
        
        assert result == -1
        mock_renderer.show_info.assert_called_once_with("Возврат в главное меню.")

    @patch("src.infrastructure.ui.menus.character_menu.input_handler")
    @patch("src.infrastructure.ui.menus.character_menu.renderer")
    def test_input_name_custom(self, mock_renderer, mock_input_handler):
        """Тестирует ввод имени пользователем."""
        mock_input_handler.get_text_input.return_value = "Тестовый персонаж"
        
        result = self.menu.input_name()
        
        assert result == "Тестовый персонаж"
        mock_renderer.clear_screen.assert_called_once()
        mock_renderer.show_title.assert_called_once_with("=== ВВЕДИТЕ ИМЯ ПЕРСОНАЖА ===")

    @patch("random.choice")
    @patch("src.infrastructure.ui.menus.character_menu.input_handler")
    @patch("src.infrastructure.ui.menus.character_menu.renderer")
    def test_input_name_random(self, mock_renderer, mock_input_handler, mock_random):
        """Тестирует генерацию случайного имени."""
        mock_input_handler.get_text_input.return_value = ""  # Пустой ввод
        mock_random.return_value = "Артас"
        
        result = self.menu.input_name()
        
        assert result == "Артас"
        mock_random.assert_called_once_with(["Артас", "Лиана", "Гэндальф", "Тирион", "Фродо"])

    @patch("builtins.open")
    @patch("yaml.safe_load")
    @patch("pathlib.Path.exists")
    def test_generate_attributes_fallback(self, mock_exists, mock_yaml, mock_open):
        """Тестирует генерацию характеристик при отсутствии файла конфигурации."""
        mock_exists.return_value = False
        
        result = self.menu.generate_attributes("nonexistent_method")
        
        assert result == {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8,
        }

    @patch("builtins.open")
    @patch("yaml.safe_load")
    @patch("pathlib.Path.exists")
    def test_generate_attributes_standard_array(self, mock_exists, mock_yaml, mock_open):
        """Тестирует генерацию характеристик стандартным набором."""
        mock_exists.return_value = True
        
        mock_config = {
            "generation_methods": {
                "standard_array": {
                    "name": "standard_array",
                    "values": [15, 14, 13, 12, 10, 8]
                }
            }
        }
        mock_yaml.return_value = mock_config
        
        with patch("random.shuffle"):
            result = self.menu.generate_attributes("standard_array")
            
            assert "strength" in result
            assert "dexterity" in result
            assert "constitution" in result
            assert "intelligence" in result
            assert "wisdom" in result
            assert "charisma" in result

    @patch("src.infrastructure.ui.menus.character_menu.renderer")
    def test_show_preview(self, mock_renderer):
        """Тестирует отображение предпросмотра персонажа."""
        mock_character = Mock()
        mock_character.name = "Тестовый персонаж"
        mock_character.level = 1
        mock_character.hp_max = 10
        mock_character.hp_current = 10
        mock_character.ac = 12
        mock_character.gold = 0
        
        mock_race = Mock()
        mock_race.localized_name = "Человек"
        mock_character.race = mock_race
        
        mock_class = Mock()
        mock_class.name = "Воин"
        mock_character.character_class = mock_class
        
        # Настраиваем характеристики
        for attr in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            mock_attr = Mock()
            mock_attr.value = 15 if attr == "strength" else 14
            setattr(mock_character, attr, mock_attr)
        
        mock_character.get_ability_modifier.return_value = 2
        
        self.menu.show_preview(mock_character)
        
        mock_renderer.clear_screen.assert_called_once()
        mock_renderer.show_title.assert_called_once_with("=== ПРЕДПРОСМОТР ПЕРСОНАЖА ===")

    def test_apply_bonuses_standard(self):
        """Тестирует применение стандартных расовых бонусов."""
        mock_race = Mock()
        mock_race.apply_bonuses.return_value = {"strength": 16}
        
        mock_class = Mock()
        
        race_info = {"race": mock_race}
        attributes = {"strength": 15}
        
        result = self.menu.apply_bonuses(attributes, race_info, mock_class)
        
        assert result == {"strength": 16}
        mock_race.apply_bonuses.assert_called_once_with(attributes)

    def test_apply_bonuses_alternative(self):
        """Тестирует применение альтернативных расовых бонусов."""
        mock_race = Mock()
        mock_race.apply_alternative_bonuses.return_value = {"strength": 17}
        
        mock_class = Mock()
        
        alternative_choices = {"ability_scores": ["strength"]}
        race_info = {"race": mock_race, "alternative_choices": alternative_choices}
        attributes = {"strength": 15}
        
        result = self.menu.apply_bonuses(attributes, race_info, mock_class)
        
        assert result == {"strength": 17}
        mock_race.apply_alternative_bonuses.assert_called_once_with(attributes, alternative_choices)

    @patch.object(CharacterMenu, 'input_name')
    @patch.object(CharacterMenu, 'show_race_selection')
    @patch.object(CharacterMenu, 'select_class')
    @patch.object(CharacterMenu, 'generate_attributes')
    @patch.object(CharacterMenu, 'apply_bonuses')
    @patch.object(CharacterMenu, 'show_preview')
    @patch.object(CharacterMenu, 'get_choice')
    @patch("src.infrastructure.ui.menus.character_menu.renderer")
    def test_create_character_success(self, mock_renderer, mock_get_choice, 
                                   mock_preview, mock_apply_bonuses, mock_generate,
                                   mock_select_class, mock_race_selection, mock_input_name):
        """Тестирует успешное создание персонажа."""
        # Настройка моков
        mock_input_name.return_value = "Тестовый персонаж"
        mock_race = Mock()
        mock_race_selection.return_value = {"race": mock_race}
        mock_class = Mock()
        mock_select_class.return_value = mock_class
        mock_generate.return_value = {"strength": 15}
        mock_apply_bonuses.return_value = {"strength": 16}
        mock_get_choice.return_value = 1  # Сохранить
        
        with patch("src.infrastructure.ui.menus.character_menu.Character") as mock_character_class:
            mock_character = Mock()
            mock_character_class.return_value = mock_character
            
            result = self.menu.create_character()
            
            assert result == mock_character
            assert self.menu.character == mock_character
            mock_renderer.show_success.assert_called_once_with("Персонаж сохранен!")

    @patch.object(CharacterMenu, 'input_name')
    def test_create_character_cancel_name(self, mock_input_name):
        """Тестирует отмену создания на этапе ввода имени."""
        mock_input_name.return_value = None
        
        result = self.menu.create_character()
        
        assert result is None

    @patch.object(CharacterMenu, 'create_character')
    def test_run_success(self, mock_create):
        """Тестирует успешный запуск меню."""
        mock_character = Mock()
        mock_create.return_value = mock_character
        
        result = self.menu.run()
        
        assert result == mock_character

    @patch.object(CharacterMenu, 'create_character')
    def test_run_cancel(self, mock_create):
        """Тестирует отмену запуска меню."""
        mock_create.return_value = None
        
        result = self.menu.run()
        
        assert result is None

    @patch.object(CharacterMenu, 'create_character')
    def test_run_max_attempts(self, mock_create):
        """Тестирует превышение максимального количества попыток."""
        mock_create.return_value = None  # Всегда возвращает None
        
        result = self.menu.run()
        
        assert result is None
        # Проверяем, что был вызван хотя бы один раз
        mock_create.assert_called()


class TestCharacterMenuEdgeCases:
    """Тесты граничных случаев для CharacterMenu."""

    def setup_method(self):
        """Настраивает тесты."""
        self.menu = CharacterMenu()

    @patch("src.infrastructure.ui.menus.character_menu.input_handler")
    @patch("src.infrastructure.ui.menus.character_menu.renderer")
    def test_input_name_whitespace_only(self, mock_renderer, mock_input_handler):
        """Тестирует ввод имени, состоящего только из пробелов."""
        mock_input_handler.get_text_input.return_value = "   "
        
        with patch("random.choice", return_value="Лиана"):
            result = self.menu.input_name()
            
            assert result == "Лиана"

    def test_max_steps_boundary(self):
        """Тестирует граничное значение максимальных шагов."""
        menu = CharacterMenu()
        assert menu.max_steps == 5
        
        # Проверяем, что текущий шаг не превышает максимальный
        menu.current_step = 10
        
        # Не должно вызывать ошибку при отображении
        with patch("src.infrastructure.ui.menus.character_menu.renderer") as mock_renderer:
            menu.show()
            mock_renderer.show_title.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
