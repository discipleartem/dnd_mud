"""
Конфигурационный файл для pytest.

Настраивает:
- Пути для импортов
- Фикстуры для тестов
- Маркеры для категорий тестов
- Общие настройки
"""

import sys
import os
from pathlib import Path
import pytest

# Добавляем src в Python path для всех тестов
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Устанавливаем переменные окружения для тестов
os.environ["TESTING"] = "true"
os.environ["PYTHONPATH"] = str(src_path)


def pytest_configure(config):
    """Настраивает pytest."""
    # Добавляем пользовательские маркеры
    config.addinivalue_line("markers", "unit: Маркирует unit тесты")
    config.addinivalue_line("markers", "integration: Маркирует интеграционные тесты")
    config.addinivalue_line("markers", "ui: Маркирует тесты UI компонентов")
    config.addinivalue_line("markers", "slow: Маркирует медленные тесты")


@pytest.fixture(scope="session")
def test_data_dir():
    """Фикстура для директории с тестовыми данными."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_dir():
    """Фикстура для временной директории."""
    import tempfile
    import shutil

    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir

    # Очистка после теста
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_character():
    """Фикстура для мока персонажа."""
    from unittest.mock import Mock
    from src.domain.entities.character import Character

    mock_char = Mock(spec=Character)
    mock_char.name = "Тестовый персонаж"
    mock_char.level = 1
    mock_char.hp_max = 10
    mock_char.hp_current = 10
    mock_char.ac = 12
    mock_char.gold = 0

    # Мокируем характеристики
    mock_char.strength.value = 10
    mock_char.dexterity.value = 10
    mock_char.constitution.value = 10
    mock_char.intelligence.value = 10
    mock_char.wisdom.value = 10
    mock_char.charisma.value = 10

    # Мокируем расу и класс
    mock_char.race.name = "Человек"
    mock_char.character_class.name = "Воин"

    # Мокируем методы
    mock_char.get_all_modifiers.return_value = {
        "strength": 0,
        "dexterity": 0,
        "constitution": 0,
        "intelligence": 0,
        "wisdom": 0,
        "charisma": 0,
    }
    mock_char.get_proficiency_bonus.return_value = 2

    return mock_char


@pytest.fixture
def mock_renderer():
    """Фикстура для мока рендерера."""
    from unittest.mock import Mock
    from src.infrastructure.ui.renderer import Renderer

    return Mock(spec=Renderer)


@pytest.fixture
def mock_input_handler():
    """Фикстура для мока обработчика ввода."""
    from unittest.mock import Mock
    from src.infrastructure.ui.input_handler import InputHandler

    return Mock(spec=InputHandler)


@pytest.fixture
def sample_character_data():
    """Фикстура с примером данных персонажа."""
    return {
        "name": "Тестовый персонаж",
        "level": 5,
        "race_name": "Человек",
        "class_name": "Воин",
        "strength": 16,
        "dexterity": 14,
        "constitution": 15,
        "intelligence": 12,
        "wisdom": 13,
        "charisma": 10,
        "hp_max": 45,
        "hp_current": 35,
        "ac": 16,
        "gold": 150,
        "created_at": "2023-01-01T00:00:00",
        "last_updated": "2023-01-01T00:00:00",
        "version": "1.0",
    }


@pytest.fixture(autouse=True)
def cleanup_singletons():
    """Автоматическая очистка singleton'ов после каждого теста."""
    yield

    # Очищаем singleton'ы, которые могут мешать тестам
    singleton_classes = [
        "src.adapters.repositories.character_repository.CharacterManager",
        "src.domain.interfaces.localization.localization",
    ]

    for class_path in singleton_classes:
        try:
            parts = class_path.split(".")
            module_path = ".".join(parts[:-1])
            class_name = parts[-1]

            module = __import__(module_path, fromlist=[class_name])
            singleton_class = getattr(module, class_name)

            if hasattr(singleton_class, "_instance"):
                singleton_class._instance = None
            elif hasattr(singleton_class, "__instances__"):
                singleton_class.__instances__.clear()
        except (ImportError, AttributeError):
            pass

    # Очищаем глобальные экземпляры UI
    try:
        from src.infrastructure.ui.input_handler import input_handler
        from src.infrastructure.ui.renderer import renderer

        # Сбрасываем состояние глобальных экземпляров
        if hasattr(input_handler, "__dict__"):
            input_handler.__dict__.clear()
        if hasattr(renderer, "__dict__"):
            renderer.__dict__.clear()

        # Пересоздаем экземпляры
        from src.infrastructure.ui.input_handler import InputHandler
        from src.infrastructure.ui.renderer import Renderer

        # Заменяем глобальные переменные новыми экземплярами
        import sys

        input_handler_module = sys.modules["src.infrastructure.ui.input_handler"]
        renderer_module = sys.modules["src.infrastructure.ui.renderer"]

        input_handler_module.input_handler = InputHandler()
        renderer_module.renderer = Renderer()

    except (ImportError, AttributeError):
        pass


# Коллекция тестов
collect_ignore_glob = [
    "test_data/**",
    "__pycache__/**",
    ".*",
]
