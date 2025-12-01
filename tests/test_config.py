"""
Тесты для D&D MUD Game

tests/test_config.py
"""
import pytest
from pathlib import Path
from config.config_manager import ConfigManager


class TestConfigManager:
    """Тесты для ConfigManager"""

    def test_load_default_config(self, tmp_path):
        """Тест загрузки дефолтной конфигурации"""
        # Создаем временный конфиг
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        default_config = config_dir / "default_config.yaml"
        default_config.write_text("""
display:
  colored_text: true
game:
  language: ru
        """)

        manager = ConfigManager()
        config = manager.load_config()

        assert config is not None
        assert 'display' in config
        assert 'game' in config

    def test_get_config_value(self):
        """Тест получения значений из конфига"""
        manager = ConfigManager()
        manager.load_config()

        # Тест существующего ключа
        value = manager.get('game.language', 'en')
        assert value in ['ru', 'en']

        # Тест несуществующего ключа
        value = manager.get('nonexistent.key', 'default')
        assert value == 'default'

    def test_set_config_value(self):
        """Тест установки значений в конфиг"""
        manager = ConfigManager()
        manager.load_config()

        manager.set('game.test_value', 'test')
        assert manager.get('game.test_value') == 'test'