"""Конфигурация pytest для тестов."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

# Добавляем src в Python path для всех тестов
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_character_data():
    """Фикстура с тестовыми данными персонажа."""
    return {
        "name": "Тестовый персонаж",
        "race": "human",
        "class": "fighter",
        "level": 1,
        "abilities": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 15,
            "intelligence": 12,
            "wisdom": 13,
            "charisma": 10
        },
        "hp": 12,
        "max_hp": 12
    }


@pytest.fixture
def sample_config_data():
    """Фикстура с тестовыми настройками."""
    return {
        "language": "ru",
        "theme": "default",
        "autosave": True,
        "autosave_interval": 300
    }


@pytest.fixture
def temp_yaml_file(tmp_path, sample_character_data):
    """Фикстура для временного YAML файла."""
    yaml_file = tmp_path / "test_character.yaml"
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(sample_character_data, f, default_flow_style=False,
                 allow_unicode=True, indent=2)
    return yaml_file


@pytest.fixture
def mock_console():
    """Фикстура с моком консоли."""
    return Mock()


@pytest.fixture(autouse=True)
def mock_colorama():
    """Отключаем colorama для тестов."""
    from unittest.mock import patch

    # Мокируем colorama полностью
    mock_colorama_module = Mock()

    # Создаем моки для цветов, которые работают как функции
    def mock_color_func(text):
        return text

    mock_colorama_module.Fore = Mock()
    mock_colorama_module.Fore.CYAN = mock_color_func
    mock_colorama_module.Fore.GREEN = mock_color_func
    mock_colorama_module.Fore.RED = mock_color_func
    mock_colorama_module.Fore.WHITE = mock_color_func
    mock_colorama_module.Fore.BLUE = mock_color_func

    mock_colorama_module.Back = Mock()
    mock_colorama_module.Style = Mock()
    mock_colorama_module.Style.RESET_ALL = ""
    mock_colorama_module.Style.BRIGHT = ""
    mock_colorama_module.init = Mock()

    with patch.dict('sys.modules', {
        'colorama': mock_colorama_module,
        'colorama.Fore': mock_colorama_module.Fore,
        'colorama.Back': mock_colorama_module.Back,
        'colorama.Style': mock_colorama_module.Style
    }):
        yield
