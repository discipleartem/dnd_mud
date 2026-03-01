"""Конфигурация pytest для тестов.

Следует принципам:
- KISS: Простые фикстуры без избыточности
- YAGNI: Только необходимый функционал для текущего этапа
"""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Добавляем src в Python path для всех тестов
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_character_data():
    """Фикстура с базовыми тестовыми данными персонажа.

    Только необходимые поля для текущего этапа разработки.
    """
    return {
        "name": "Тестовый персонаж",
        "level": 1,
        "hit_points": 10,
        "max_hit_points": 10,
    }


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

    with patch.dict(
        "sys.modules",
        {
            "colorama": mock_colorama_module,
            "colorama.Fore": mock_colorama_module.Fore,
            "colorama.Back": mock_colorama_module.Back,
            "colorama.Style": mock_colorama_module.Style,
        },
    ):
        yield
