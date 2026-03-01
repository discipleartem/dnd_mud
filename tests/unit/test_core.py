"""Unit тесты для core модулей."""

import sys
from pathlib import Path
from unittest.mock import mock_open, patch

# Добавляем src в Python path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from core.config import Config
from core.exceptions import ConfigError, DnDMudError, GameError
from core.game import Game


class TestConfig:
    """Тесты класса Config."""

    def test_init_default(self):
        """Тест инициализации с настройками по умолчанию."""
        config = Config()

        assert config.config_path == Path("config.yaml")
        assert config.data_dir == Path("data")
        assert config.saves_dir == Path("saves")
        assert config.settings["language"] == "ru"
        assert config.settings["theme"] == "default"
        assert config.settings["autosave"] is True

    def test_get_existing_key(self):
        """Тест получения существующей настройки."""
        config = Config()
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"

    def test_get_non_existing_key(self):
        """Тест получения несуществующей настройки."""
        config = Config()
        assert config.get("non_existing") is None
        assert config.get("non_existing", "default") == "default"

    def test_set(self):
        """Тест установки настройки."""
        config = Config()
        config.set("test_key", "test_value")
        assert config.settings["test_key"] == "test_value"

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    @patch("yaml.dump")
    def test_load_save_cycle(self, mock_yaml_dump, mock_yaml_load, mock_file):
        """Тест цикла загрузки и сохранения."""
        # Настраиваем моки
        mock_yaml_load.return_value = {"test": "value"}
        mock_file.return_value.__enter__.return_value.read.return_value = "test"

        # Создаём Config с мокированным файлом
        config = Config()

        # Проверяем, что yaml.safe_load был вызван (в __init__ при load())
        mock_yaml_load.assert_called()

        # Проверяем сохранение
        config.save()
        mock_yaml_dump.assert_called()


class TestExceptions:
    """Тесты исключений."""

    def test_dn_d_mud_error(self):
        """Тест базового исключения."""
        error = DnDMudError("Тест")
        assert str(error) == "Тест"

    def test_config_error(self):
        """Тест ошибки конфигурации."""
        error = ConfigError("Тест конфигурации")
        assert str(error) == "Тест конфигурации"

    def test_game_error(self):
        """Тест ошибки игры."""
        error = GameError("Тест игры")
        assert str(error) == "Тест игры"


class TestGame:
    """Тесты класса Game."""

    def test_init(self):
        """Тест инициализации игры."""
        from ui.console import Console
        console = Console()
        game = Game(console)
        assert game.config is not None
        assert game.ui is not None
        assert game.running is False

    def test_run_basic(self):
        """Тест базового запуска игры."""
        from ui.console import Console
        console = Console()
        game = Game(console)

        # Базовая проверка инициализации
        assert game.config is not None
        assert game.ui is not None
        assert game.running is False

        # Проверяем, что Use Case создан
        assert game.game_use_case is not None
