"""Тесты для создания персонажа."""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Добавляем src в Python path для тестов
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.ui.menus.character_creation import CharacterCreationController
from domain.services.character_generation import CharacterGenerator, GenerationMethod
from domain.entities.character import Character


def create_mock_input_handler():
    """Создает мок для обработчика ввода."""
    mock = Mock()
    mock.get_text.return_value = "Тестовый персонаж"
    mock.get_int.return_value = 1
    mock.get_key.return_value = 'enter'
    return mock


def create_mock_renderer():
    """Создает мок для рендерера."""
    mock = Mock()
    mock.clear_screen.return_value = None
    mock.render_title.return_value = None
    return mock


@pytest.fixture
def character_controller():
    """Фикстура для контроллера создания персонажа."""
    input_handler = create_mock_input_handler()
    renderer = create_mock_renderer()
    return CharacterCreationController(input_handler, renderer)


class TestCharacterCreationController:
    """Тесты контроллера создания персонажа."""
    
    def test_init(self, character_controller):
        """Тест инициализации контроллера."""
        assert character_controller.input_handler is not None
        assert character_controller.renderer is not None
        assert character_controller.creation_data == {}
    
    def test_collect_basic_info(self, character_controller):
        """Тест сбора базовой информации."""
        character_controller._collect_basic_info()
        
        assert character_controller.creation_data["name"] == "Тестовый персонаж"
        character_controller.input_handler.get_text.assert_called_with("Имя персонажа: ")
    
    @patch('infrastructure.ui.menus.character_creation.UniversalRaceFactory')
    def test_select_race(self, mock_race_factory, character_controller):
        """Тест выбора расы."""
        mock_race_factory.get_available_races.return_value = {"human": "Человек"}
        
        character_controller._select_race()
        
        assert character_controller.creation_data["race"] == "human"
    
    @patch('infrastructure.ui.menus.character_creation.CharacterClassFactory')
    def test_select_class(self, mock_class_factory, character_controller):
        """Тест выбора класса."""
        mock_class_factory.get_available_classes.return_value = {"fighter": "Воин"}
        
        character_controller._select_class()
        
        assert character_controller.creation_data["class"] == "fighter"
    
    def test_select_generation_method(self, character_controller):
        """Тест выбора метода генерации."""
        character_controller._select_generation_method()
        
        assert character_controller.creation_data["generation_method"] == GenerationMethod.STANDARD_ARRAY
    
    @patch('infrastructure.ui.menus.character_creation.CharacterGenerator')
    def test_generate_attributes(self, mock_generator, character_controller):
        """Тест генерации характеристик."""
        mock_generator.generate_attributes.return_value = {"strength": 15}
        character_controller.creation_data["generation_method"] = GenerationMethod.STANDARD_ARRAY
        
        character_controller._generate_attributes()
        
        assert character_controller.creation_data["attributes"] == {"strength": 15}
    
    def test_review_character(self, character_controller):
        """Тест проверки персонажа."""
        character_controller.creation_data = {
            "name": "Тест",
            "race": "human",
            "class": "fighter",
            "attributes": {"strength": 15}
        }
        character_controller.input_handler.get_text.return_value = 'д'
        
        result = character_controller._review_character()
        
        assert result is True
        character_controller.input_handler.get_text.assert_called_with("\nСоздать персонажа? (д/н): ")
    
    def test_review_character_cancel(self, character_controller):
        """Тест отмены создания персонажа."""
        character_controller.creation_data = {"name": "Тест"}
        character_controller.input_handler.get_text.return_value = 'н'
        
        result = character_controller._review_character()
        
        assert result is False


class TestCharacterGenerator:
    """Тесты генератора персонажей."""
    
    def test_generate_attributes_standard_array(self):
        """Тест генерации стандартным набором."""
        attributes = CharacterGenerator.generate_attributes(GenerationMethod.STANDARD_ARRAY)
        
        assert attributes["strength"] == 15
        assert attributes["dexterity"] == 14
        assert attributes["constitution"] == 13
    
    def test_generate_attributes_four_d6(self):
        """Тест генерации 4d6."""
        attributes = CharacterGenerator.generate_attributes(GenerationMethod.FOUR_D6_DROP_LOWEST)
        
        assert "strength" in attributes
        assert all(3 <= val <= 18 for val in attributes.values())
    
    def test_generate_attributes_point_buy(self):
        """Тест генерации покупкой очков."""
        attributes = CharacterGenerator.generate_attributes(GenerationMethod.POINT_BUY)
        
        assert all(attributes[attr] == 10 for attr in attributes)
    
    @patch('infrastructure.ui.menus.character_creation.UniversalRaceFactory')
    @patch('infrastructure.ui.menus.character_creation.CharacterClassFactory')
    def test_create_character(self, mock_class_factory, mock_race_factory):
        """Тест создания персонажа."""
        mock_race_factory.create_race.return_value = Mock(name="Человек")
        mock_class_factory.create_class.return_value = Mock(name="Воин")
        
        character = CharacterGenerator.create_character(
            name="Тестовый",
            race_name="human",
            class_name="fighter"
        )
        
        assert character.name == "Тестовый"
        mock_race_factory.create_race.assert_called_with("human")
        mock_class_factory.create_class.assert_called_with("fighter")


if __name__ == "__main__":
    pytest.main([__file__])
