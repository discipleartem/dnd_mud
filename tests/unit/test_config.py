"""Тесты для класса Config."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Добавляем src в Python path для тестов
sys.path.insert(0, 'src')

from core.config import Config
from core.exceptions import ConfigError


def test_config_default_values():
    """Тест значений по умолчанию."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.yaml"

        with patch('core.config.Path') as mock_path:
            mock_path.return_value = config_path
            config = Config()

            # Проверяем значения по умолчанию (YAGNI)
            assert config.get("language") == "ru"
            assert config.get("theme") == "default"
            # Проверяем, что преждевременные настройки отсутствуют
            assert config.get("autosave") is None
            assert config.get("autosave_interval") is None


def test_config_load_existing():
    """Тест загрузки существующего конфига."""
    test_config = {
        "language": "en",
        "theme": "dark"
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.yaml"

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)

        with patch('core.config.Path') as mock_path:
            mock_path.return_value = config_path
            config = Config()

            assert config.get("language") == "en"
            assert config.get("theme") == "dark"


def test_config_save():
    """Тест сохранения конфига."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.yaml"

        with patch('core.config.Path') as mock_path:
            mock_path.return_value = config_path
            config = Config()
            config.set("language", "fr")

            config.save()

            with open(config_path, encoding='utf-8') as f:
                saved_config = yaml.safe_load(f)

            assert saved_config["language"] == "fr"


def test_config_error_handling():
    """Тест обработки ошибок конфига."""
    invalid_yaml = "invalid: yaml: content:"

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.yaml"

        with patch('core.config.Path') as mock_path:
            mock_path.return_value = config_path

            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(invalid_yaml)

            with pytest.raises(ConfigError):
                Config()


def test_config_get_set():
    """Тест методов get и set."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.yaml"

        with patch('core.config.Path') as mock_path:
            mock_path.return_value = config_path
            config = Config()

            config.set("test_key", "test_value")
            assert config.get("test_key") == "test_value"

            assert config.get("nonexistent", "default") == "default"
