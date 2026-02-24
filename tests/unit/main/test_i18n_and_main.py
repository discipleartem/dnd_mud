#!/usr/bin/env python3
"""Тесты для i18n и main.py."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from unittest.mock import Mock, patch

import pytest
import yaml

from i18n import (
    I18nError,
    SimpleI18nManager,
    get_available_languages,
    get_current_language,
    set_language,
    t,
)


class TestI18nError:
    """Тесты для исключения I18nError."""

    def test_i18n_error_inheritance(self) -> None:
        """Тест наследования I18nError."""
        error = I18nError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_i18n_error_with_cause(self) -> None:
        """Тест I18nError с причиной."""
        original_error = ValueError("Original error")
        error = I18nError("Wrapped error") from original_error
        
        assert str(error) == "Wrapped error"
        assert error.__cause__ is original_error


class TestSimpleI18nManager:
    """Тесты для SimpleI18nManager."""

    def create_test_locale_file(self, content: dict[str, Any]) -> Path:
        """Создать тестовый файл локализации."""
        temp_file = NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
        yaml.dump(content, temp_file, allow_unicode=True)
        temp_file.flush()
        temp_file.close()
        return Path(temp_file.name)

    def test_init_default_language(self) -> None:
        """Тест инициализации с языком по умолчанию."""
        # Создаем тестовую директорию локализации
        with NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            test_content = {"test": {"key": "value"}}
            yaml.dump(test_content, f)
            f.flush()
            
            locales_dir = Path(f.name).parent
            locale_file = Path(f.name)
            
            # Переименовываем в ru.yaml
            ru_file = locales_dir / "ru.yaml"
            locale_file.rename(ru_file)
            
            try:
                with patch('pathlib.Path.exists', return_value=True):
                    manager = SimpleI18nManager()
                    manager._locales_dir = locales_dir
                    manager.load_translations("ru")
                    
                    assert manager._default_language == "ru"
                    assert manager._current_language == "ru"
            finally:
                ru_file.unlink()

    def test_load_translations_success(self) -> None:
        """Тест успешной загрузки переводов."""
        test_content = {
            "menu": {
                "title": "Главное меню",
                "items": {
                    "new_game": "Новая игра",
                    "load_game": "Загрузить игру"
                }
            },
            "error": "Ошибка"
        }
        
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            manager._locales_dir = locale_file.parent
            manager.load_translations(locale_file.stem)
            
            assert manager._current_language == locale_file.stem
            assert manager._translations == test_content
        finally:
            locale_file.unlink()

    def test_load_translations_file_not_found(self) -> None:
        """Тест загрузки переводов с несуществующим файлом."""
        manager = SimpleI18nManager()
        manager._locales_dir = Path("/nonexistent")
        
        with pytest.raises(I18nError, match="Файл локализации не найден"):
            manager.load_translations("nonexistent")

    def test_load_translations_invalid_yaml(self) -> None:
        """Тест загрузки переводов с невалидным YAML."""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            
            manager = SimpleI18nManager()
            manager._locales_dir = Path(f.name).parent
            
            try:
                with pytest.raises(I18nError, match="Ошибка парсинга YAML"):
                    manager.load_translations(Path(f.name).stem)
            finally:
                Path(f.name).unlink()

    def test_load_yaml_file_success(self) -> None:
        """Тест успешной загрузки YAML файла."""
        test_content = {"key": "value", "nested": {"key2": "value2"}}
        
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            result = manager._load_yaml_file(locale_file)
            
            assert result == test_content
        finally:
            locale_file.unlink()

    def test_load_yaml_file_empty(self) -> None:
        """Тест загрузки пустого YAML файла."""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()
            
            manager = SimpleI18nManager()
            result = manager._load_yaml_file(Path(f.name))
            
            assert result == {}
            
            Path(f.name).unlink()

    def test_get_simple_key(self) -> None:
        """Тест получения простого ключа."""
        test_content = {"simple": "Простой перевод"}
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            manager._locales_dir = locale_file.parent
            manager.load_translations(locale_file.stem)
            
            result = manager.get("simple")
            assert result == "Простой перевод"
        finally:
            locale_file.unlink()

    def test_get_nested_key(self) -> None:
        """Тест получения вложенного ключа."""
        test_content = {
            "menu": {
                "title": "Главное меню",
                "items": {
                    "new_game": "Новая игра"
                }
            }
        }
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            manager._locales_dir = locale_file.parent
            manager.load_translations(locale_file.stem)
            
            result = manager.get("menu.title")
            assert result == "Главное меню"
            
            result = manager.get("menu.items.new_game")
            assert result == "Новая игра"
        finally:
            locale_file.unlink()

    def test_get_key_not_found(self) -> None:
        """Тест получения несуществующего ключа."""
        test_content = {"existing": "Существующий ключ"}
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            manager._locales_dir = locale_file.parent
            manager.load_translations(locale_file.stem)
            
            result = manager.get("nonexistent")
            assert result == "nonexistent"
            
            result = manager.get("menu.nonexistent")
            assert result == "menu.nonexistent"
        finally:
            locale_file.unlink()

    def test_get_with_formatting(self) -> None:
        """Тест получения с форматированием."""
        test_content = {
            "welcome": "Привет, {name}! У тебя {health} HP.",
            "simple": "Простой текст без форматирования"
        }
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            manager._locales_dir = locale_file.parent
            manager.load_translations(locale_file.stem)
            
            result = manager.get("welcome", name="Арагорн", health=100)
            assert result == "Привет, Арагорн! У тебя 100 HP."
            
            result = manager.get("simple")
            assert result == "Простой текст без форматирования"
        finally:
            locale_file.unlink()

    def test_get_with_formatting_error(self) -> None:
        """Тест получения с ошибкой форматирования."""
        test_content = {
            "broken": "Привет, {missing}!",
            "broken_type": "Привет, {name}!"
        }
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            manager._locales_dir = locale_file.parent
            manager.load_translations(locale_file.stem)
            
            # Отсутствующий параметр
            result = manager.get("broken")
            assert result == "Привет, {missing}!"
            
            # Неверный тип параметра
            result = manager.get("broken_type", name=123)
            assert result == "Привет, {name}!"
        finally:
            locale_file.unlink()

    def test_get_list_value(self) -> None:
        """Тест получения списка."""
        test_content = {
            "items": ["Предмет 1", "Предмет 2", "Предмет 3"]
        }
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            manager._locales_dir = locale_file.parent
            manager.load_translations(locale_file.stem)
            
            result = manager.get("items")
            assert result == ["Предмет 1", "Предмет 2", "Предмет 3"]
        finally:
            locale_file.unlink()

    def test_navigate_to_key_success(self) -> None:
        """Тест успешной навигации к ключу."""
        test_content = {
            "level1": {
                "level2": {
                    "level3": "Глубокое значение"
                }
            }
        }
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            manager._locales_dir = locale_file.parent
            manager.load_translations(locale_file.stem)
            
            result = manager._navigate_to_key("level1.level2.level3")
            assert result == "Глубокое значение"
        finally:
            locale_file.unlink()

    def test_navigate_to_key_not_found(self) -> None:
        """Тест навигации к несуществующему ключу."""
        test_content = {"existing": "value"}
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            manager._locales_dir = locale_file.parent
            manager.load_translations(locale_file.stem)
            
            result = manager._navigate_to_key("nonexistent.key")
            assert result == "nonexistent.key"
            
            result = manager._navigate_to_key("existing.nonexistent")
            assert result == "existing.nonexistent"
        finally:
            locale_file.unlink()

    def test_format_string_success(self) -> None:
        """Тест успешного форматирования строки."""
        manager = SimpleI18nManager()
        
        result = manager._format_string("Привет, {name}!", name="Мир")
        assert result == "Привет, Мир!"
        
        result = manager._format_string("Число: {number}", number=42)
        assert result == "Число: 42"

    def test_format_string_error(self) -> None:
        """Тест форматирования строки с ошибкой."""
        manager = SimpleI18nManager()
        
        # Отсутствующий ключ
        result = manager._format_string("Привет, {missing}!")
        assert result == "Привет, {missing}!"
        
        # Неверный формат
        result = manager._format_string("Привет, {name}!")
        assert result == "Привет, {name}!"

    def test_get_current_language(self) -> None:
        """Тест получения текущего языка."""
        manager = SimpleI18nManager()
        manager._current_language = "en"
        
        result = manager.get_current_language()
        assert result == "en"

    def test_get_available_languages_exists(self) -> None:
        """Тест получения доступных языков когда директория существует."""
        with NamedTemporaryFile(suffix=".yaml", delete=False) as f1:
            with NamedTemporaryFile(suffix=".yaml", delete=False) as f2:
                f1.write("content1")
                f2.write("content2")
                f1.flush()
                f2.flush()
                
                manager = SimpleI18nManager()
                manager._locales_dir = Path(f1.name).parent
                
                try:
                    languages = manager.get_available_languages()
                    assert len(languages) >= 2
                    assert Path(f1.name).stem in languages
                    assert Path(f2.name).stem in languages
                finally:
                    Path(f1.name).unlink()
                    Path(f2.name).unlink()

    def test_get_available_languages_not_exists(self) -> None:
        """Тест получения доступных языков когда директория не существует."""
        manager = SimpleI18nManager()
        manager._locales_dir = Path("/nonexistent/directory")
        
        result = manager.get_available_languages()
        assert result == []

    def test_set_language(self) -> None:
        """Тест установки языка."""
        test_content = {"test": "test value"}
        locale_file = self.create_test_locale_file(test_content)
        
        try:
            manager = SimpleI18nManager()
            manager._locales_dir = locale_file.parent
            
            with patch.object(manager, 'load_translations') as mock_load:
                manager.set_language(locale_file.stem)
                mock_load.assert_called_once_with(locale_file.stem)
        finally:
            locale_file.unlink()


class TestGlobalI18nFunctions:
    """Тесты для глобальных функций i18n."""

    @patch('i18n._i18n_manager')
    def test_t_function(self, mock_manager) -> None:
        """Тест глобальной функции t."""
        mock_manager.get.return_value = "Переведенная строка"
        
        result = t("test.key", param="value")
        
        assert result == "Переведенная строка"
        mock_manager.get.assert_called_once_with("test.key", param="value")

    @patch('i18n._i18n_manager')
    def test_set_language_function(self, mock_manager) -> None:
        """Тест глобальной функции set_language."""
        set_language("en")
        
        mock_manager.set_language.assert_called_once_with("en")

    @patch('i18n._i18n_manager')
    def test_get_current_language_function(self, mock_manager) -> None:
        """Тест глобальной функции get_current_language."""
        mock_manager.get_current_language.return_value = "ru"
        
        result = get_current_language()
        
        assert result == "ru"
        mock_manager.get_current_language.assert_called_once()

    @patch('i18n._i18n_manager')
    def test_get_available_languages_function(self, mock_manager) -> None:
        """Тест глобальной функции get_available_languages."""
        mock_manager.get_available_languages.return_value = ["ru", "en"]
        
        result = get_available_languages()
        
        assert result == ["ru", "en"]
        mock_manager.get_available_languages.assert_called_once()


class TestMainModule:
    """Тесты для main.py."""

    @patch('main.t')
    @patch('builtins.print')
    def test_print_welcome_banner(self, mock_print, mock_t) -> None:
        """Тест вывода приветственного баннера."""
        mock_t.side_effect = lambda key, **kwargs: {
            'main.welcome.title': 'Добро пожаловать в D&D MUD',
            'main.welcome.version': 'Версия 1.0.0'
        }.get(key, key)
        
        from main import _print_welcome_banner
        
        _print_welcome_banner()
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        printed_text = "\n".join(print_calls)
        
        assert "DUNGEONS & DRAGONS MUD" in printed_text
        assert "Добро пожаловать в D&D MUD" in printed_text
        assert "Версия 1.0.0" in printed_text
        assert "Создайте своего героя и начните приключение!" in printed_text

    @patch('main.t')
    @patch('builtins.input')
    @patch('main._print_welcome_banner')
    def test_welcome_screen(self, mock_banner, mock_input, mock_t) -> None:
        """Тест приветственного экрана."""
        mock_t.return_value = "Нажмите Enter для продолжения..."
        mock_input.return_value = ""
        
        from main import welcome_screen
        
        welcome_screen()
        
        mock_banner.assert_called_once()
        mock_input.assert_called_once_with("Нажмите Enter для продолжения...")
        mock_t.assert_called_once_with("main.welcome.press_enter")

    @patch('main.show_main_menu')
    @patch('main.welcome_screen')
    def test_main_success(self, mock_welcome, mock_menu) -> None:
        """Тест успешного выполнения main."""
        from main import main
        
        result = main()
        
        assert result == 0
        mock_welcome.assert_called_once()
        mock_menu.assert_called_once()

    @patch('main.show_main_menu')
    @patch('main.welcome_screen')
    @patch('main.t')
    @patch('builtins.print')
    def test_main_keyboard_interrupt(self, mock_print, mock_t, mock_welcome, mock_menu) -> None:
        """Тест прерывания с клавиатуры в main."""
        mock_t.return_value = "Программа прервана"
        mock_welcome.side_effect = KeyboardInterrupt()
        
        from main import main
        
        result = main()
        
        assert result == 0
        mock_print.assert_called_once_with("\nПрограмма прервана")
        mock_t.assert_called_once_with("main.welcome.interrupted")

    @patch('main.show_main_menu')
    @patch('main.welcome_screen')
    @patch('main.t')
    @patch('builtins.print')
    def test_main_exception(self, mock_print, mock_t, mock_welcome, mock_menu) -> None:
        """Тест обработки исключения в main."""
        mock_t.return_value = "Ошибка: {error}"
        mock_welcome.side_effect = ValueError("Test error")
        
        from main import main
        
        result = main()
        
        assert result == 1
        mock_print.assert_called_once_with("\nОшибка: Test error")
        mock_t.assert_called_once_with("main.welcome.error", error="Test error")

    @patch('main.main')
    @patch('sys.exit')
    def test_run_application(self, mock_exit, mock_main) -> None:
        """Тест запуска приложения."""
        mock_main.return_value = 0
        
        from main import _run_application
        
        _run_application()
        
        mock_main.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch('main.main')
    @patch('sys.exit')
    def test_run_application_with_error(self, mock_exit, mock_main) -> None:
        """Тест запуска приложения с ошибкой."""
        mock_main.return_value = 1
        
        from main import _run_application
        
        _run_application()
        
        mock_main.assert_called_once()
        mock_exit.assert_called_once_with(1)

    @patch('main.t')
    def test_banner_formatting(self, mock_t) -> None:
        """Тест форматирования баннера."""
        mock_t.side_effect = lambda key, **kwargs: {
            'main.welcome.title': 'Очень длинное название',
            'main.welcome.version': 'v1.0.0'
        }.get(key, key)
        
        from main import _print_welcome_banner
        
        with patch('builtins.print') as mock_print:
            _print_welcome_banner()
            
            print_calls = [str(call) for call in mock_print.call_args_list]
            banner_text = "\n".join(print_calls)
            
            # Проверяем, что все строки баннера имеют правильную длину
            lines = banner_text.split('\n')
            for line in lines:
                if line.startswith('║') and line.endswith('║'):
                    # Убираем рамку и проверяем содержимое
                    content = line[1:-1]
                    assert len(content) == 62  # 60 символов содержимого + 2 пробела

    @patch('main.t')
    def test_banner_with_unicode(self, mock_t) -> None:
        """Тест баннера с юникод символами."""
        mock_t.side_effect = lambda key, **kwargs: {
            'main.welcome.title': '🎲 Добро пожаловать 🎲',
            'main.welcome.version': '📜 Версия 1.0.0 📜'
        }.get(key, key)
        
        from main import _print_welcome_banner
        
        with patch('builtins.print') as mock_print:
            _print_welcome_banner()
            
            print_calls = [str(call) for call in mock_print.call_args_list]
            banner_text = "\n".join(print_calls)
            
            assert "🎲 Добро пожаловать 🎲" in banner_text
            assert "📜 Версия 1.0.0 📜" in banner_text