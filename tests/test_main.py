"""
Тесты для main.py - точки входа в приложение.

Тестируем:
- Запуск приложения
- Обработку исключений
- Настройку логирования
- Главное меню и его опции
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import logging

# Добавляем корень проекта в Python path для импортов
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import (
    setup_logging, show_splash_screen, handle_new_game, 
    handle_load_game, handle_settings, main
)
from src.infrastructure.ui.menus.main_menu import show_main_menu, MenuOption


pytestmark = pytest.mark.unit


class TestLoggingSetup:
    """Тесты настройки логирования."""
    
    def test_setup_logging_configures_basic_logging(self):
        """Тестирует базовую настройку логирования."""
        with patch('logging.basicConfig') as mock_config:
            setup_logging()
            
            # Проверяем, что basicConfig был вызван
            mock_config.assert_called_once()
            call_args = mock_config.call_args
            
            # Проверяем основные параметры
            assert call_args.kwargs['level'] == logging.INFO
            assert 'format' in call_args.kwargs
            assert 'handlers' in call_args.kwargs
            assert len(call_args.kwargs['handlers']) == 2
    
    def test_setup_logging_creates_file_handler(self):
        """Тестирует создание файлового обработчика."""
        with patch('logging.FileHandler') as mock_file_handler:
            setup_logging()
            mock_file_handler.assert_called_once_with("dnd_mud.log", encoding="utf-8")


class TestSplashScreen:
    """Тесты заставки игры."""
    
    @patch('src.infrastructure.ui.renderer.renderer')
    def test_show_splash_screen_displays_content(self, mock_renderer):
        """Тестирует отображение заставки."""
        mock_renderer.get_input.return_value = ""
        
        show_splash_screen()
        
        mock_renderer.clear_screen.assert_called_once()
        # Проверяем, что get_input был вызван для ожидания нажатия Enter
        mock_renderer.get_input.assert_called_once_with()


class TestMainMenuHandlers:
    """Тесты обработчиков главного меню."""
    
    @patch('src.infrastructure.ui.renderer.renderer')
    @patch('src.infrastructure.ui.input_handler.input_handler')
    @patch('src.adapters.repositories.character_repository.CharacterManager')
    def test_handle_new_game_success(self, mock_manager_class, mock_input, mock_renderer):
        """Тестирует успешную обработку новой игры."""
        # Настройка моков
        mock_character = Mock()
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
        
        mock_creation_controller = Mock()
        mock_creation_controller.create_character.return_value = mock_character
        
        mock_manager_instance = Mock()
        mock_manager_instance.save_character.return_value = True
        mock_manager_class.get_instance.return_value = mock_manager_instance
        
        with patch('src.infrastructure.ui.menus.character_creation.CharacterCreationController', 
                  return_value=mock_creation_controller):
            handle_new_game()
        
        # Проверяем, что персонаж был создан и сохранен
        mock_creation_controller.create_character.assert_called_once()
        mock_manager_instance.save_character.assert_called_once_with(mock_character)
        mock_renderer.show_success.assert_called_once()
    
    @patch('src.infrastructure.ui.renderer.renderer')
    @patch('src.infrastructure.ui.input_handler.input_handler')
    @patch('src.adapters.repositories.character_repository.CharacterManager')
    def test_handle_new_game_cancellation(self, mock_manager_class, mock_input, mock_renderer):
        """Тестирует отмену создания персонажа."""
        mock_creation_controller = Mock()
        mock_creation_controller.create_character.return_value = None
        
        with patch('src.infrastructure.ui.menus.character_creation.CharacterCreationController', 
                  return_value=mock_creation_controller):
            handle_new_game()
        
        mock_renderer.show_info.assert_called_once_with("Создание персонажа отменено")
    
    @patch('src.infrastructure.ui.renderer.renderer')
    @patch('src.infrastructure.ui.input_handler.input_handler')
    @patch('src.adapters.repositories.character_repository.CharacterManager')
    def test_handle_load_game_with_characters(self, mock_manager_class, mock_input, mock_renderer):
        """Тестирует загрузку игры с сохраненными персонажами."""
        # Настройка моков
        mock_characters = ["character1.json", "character2.json"]
        mock_manager_instance = Mock()
        mock_manager_instance.list_characters.return_value = mock_characters
        mock_manager_instance.get_character_info.side_effect = [
            {
                'name': 'Персонаж 1',
                'race': 'Человек',
                'class': 'Воин',
                'level': 1
            },
            {
                'name': 'Персонаж 2',
                'race': 'Эльф',
                'class': 'Волшебник',
                'level': 2
            }
        ]
        
        mock_loaded_character = Mock()
        mock_loaded_character.name = "Персонаж 1"
        mock_loaded_character.race.name = "Человек"
        mock_loaded_character.character_class.name = "Воин"
        mock_loaded_character.level = 1
        mock_loaded_character.hp_current = 10
        mock_loaded_character.hp_max = 10
        mock_loaded_character.ac = 12
        mock_loaded_character.gold = 100
        mock_loaded_character.get_all_modifiers.return_value = {
            'strength': 1, 'dexterity': 0, 'constitution': 1,
            'intelligence': 0, 'wisdom': 0, 'charisma': 0
        }
        
        mock_manager_instance.load_character.return_value = mock_loaded_character
        mock_manager_class.get_instance.return_value = mock_manager_instance
        
        # Имитируем выбор первого персонажа
        mock_input.get_int.return_value = 1
        
        handle_load_game()
        
        # Проверяем вызовы
        mock_manager_instance.list_characters.assert_called_once()
        mock_manager_instance.load_character.assert_called_once_with("character1.json")
        mock_renderer.show_success.assert_called_once()
    
    @patch('src.infrastructure.ui.renderer.renderer')
    @patch('src.infrastructure.ui.input_handler.input_handler')
    @patch('src.adapters.repositories.character_repository.CharacterManager')
    def test_handle_load_game_no_characters(self, mock_manager_class, mock_input, mock_renderer):
        """Тестирует загрузку игры без сохраненных персонажей."""
        mock_manager_instance = Mock()
        mock_manager_instance.list_characters.return_value = []
        mock_manager_class.get_instance.return_value = mock_manager_instance
        
        handle_load_game()
        
        mock_renderer.show_info.assert_called_once_with("Сохраненные персонажи не найдены")
    
    @patch('src.infrastructure.ui.renderer.renderer')
    @patch('src.infrastructure.ui.input_handler.input_handler')
    def test_handle_settings(self, mock_input, mock_renderer):
        """Тестирует обработку настроек."""
        handle_settings()
        
        mock_renderer.show_info.assert_called()
        mock_renderer.get_input.assert_called_once()


class TestMainFunction:
    """Тесты основной функции приложения."""
    
    @patch('main.handle_settings')
    @patch('main.handle_load_game')
    @patch('main.handle_new_game')
    @patch('main.show_main_menu')
    @patch('main.show_splash_screen')
    @patch('main.setup_logging')
    def test_main_normal_exit(self, mock_setup, mock_splash, mock_menu, 
                           mock_new_game, mock_load_game, mock_settings):
        """Тестирует нормальный выход из программы."""
        mock_menu.return_value = MenuOption.EXIT
        
        result = main()
        
        assert result == 0
        mock_setup.assert_called_once()
        mock_splash.assert_called_once()
        mock_menu.assert_called_once()
    
    @patch('main.handle_settings')
    @patch('main.handle_load_game')
    @patch('main.handle_new_game')
    @patch('main.show_main_menu')
    @patch('main.show_splash_screen')
    @patch('main.setup_logging')
    def test_main_new_game_flow(self, mock_setup, mock_splash, mock_menu,
                              mock_new_game, mock_load_game, mock_settings):
        """Тестирует поток новой игры."""
        # Сначала выбираем новую игру, потом выход
        mock_menu.side_effect = [MenuOption.NEW_GAME, MenuOption.EXIT]
        
        result = main()
        
        assert result == 0
        mock_new_game.assert_called_once()
        assert mock_menu.call_count == 2
    
    @patch('main.handle_settings')
    @patch('main.handle_load_game')
    @patch('main.handle_new_game')
    @patch('main.show_main_menu')
    @patch('main.show_splash_screen')
    @patch('main.setup_logging')
    def test_main_keyboard_interrupt(self, mock_setup, mock_splash, mock_menu,
                                 mock_new_game, mock_load_game, mock_settings):
        """Тестирует обработку KeyboardInterrupt."""
        mock_menu.side_effect = [
            KeyboardInterrupt(),  # Первое прерывание
            MenuOption.EXIT      # Затем выход
        ]
        
        with patch('builtins.input', return_value='д'):
            result = main()
        
        assert result == 0
    
    @patch('main.setup_logging')
    def test_main_critical_error(self, mock_setup):
        """Тестирует обработку критической ошибки."""
        mock_setup.side_effect = Exception("Критическая ошибка")
        
        with patch('builtins.print') as mock_print:
            result = main()
        
        assert result == 1
        mock_print.assert_called_once()
    
    @patch('main.handle_settings')
    @patch('main.handle_load_game')
    @patch('main.handle_new_game')
    @patch('main.show_main_menu')
    @patch('main.show_splash_screen')
    @patch('main.setup_logging')
    def test_main_menu_exception_handling(self, mock_setup, mock_splash, mock_menu,
                                      mock_new_game, mock_load_game, mock_settings):
        """Тестирует обработку исключений в меню."""
        mock_menu.side_effect = [
            Exception("Ошибка меню"),
            MenuOption.EXIT
        ]
        
        with patch('src.infrastructure.ui.renderer.renderer') as mock_renderer:
            with patch('src.infrastructure.ui.input_handler.input_handler') as mock_input:
                result = main()
        
        assert result == 0
        mock_renderer.show_error.assert_called_once()


class TestIntegration:
    """Интеграционные тесты."""
    
    @patch('main.show_splash_screen')
    @patch('main.setup_logging')
    def test_full_menu_navigation(self, mock_setup, mock_splash):
        """Тестирует полную навигацию по меню."""
        with patch('src.infrastructure.ui.renderer.renderer') as mock_renderer:
            with patch('src.infrastructure.ui.input_handler.input_handler') as mock_input:
                # Мокаем show_main_menu для возврата разных опций
                with patch('main.show_main_menu') as mock_menu:
                    mock_menu.side_effect = [
                        MenuOption.SETTINGS,
                        MenuOption.LOAD_GAME,
                        MenuOption.NEW_GAME,
                        MenuOption.EXIT
                    ]
                    
                    with patch('main.handle_settings'), \
                         patch('main.handle_load_game'), \
                         patch('main.handle_new_game'):
                        
                        result = main()
                        
                        assert result == 0
                        assert mock_menu.call_count == 4


if __name__ == "__main__":
    pytest.main([__file__])
