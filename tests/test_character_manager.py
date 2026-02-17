"""
Тесты для CharacterManager и репозитория персонажей.

Тестируем:
- Сохранение и загрузка персонажей
- Список персонажей
- Удаление персонажей
- Singleton паттерн
- Форматы JSON и YAML
- Обработку ошибок
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import sys

# Добавляем src в Python path для тестов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.adapters.repositories.character_repository import (
    CharacterSaveData,
    CharacterRepository,
    CharacterManager,
    save_character,
    load_character,
    list_characters,
    get_character_info,
)
from src.domain.entities.character import Character
from src.domain.entities.race import Race
from src.domain.entities.class_ import CharacterClass

pytestmark = pytest.mark.unit


def create_mock_character_for_manager(name: str = "Тестовый персонаж", level: int = 5):
    """Создает правильный мок персонажа с всеми необходимыми атрибутами для тестов менеджера."""
    mock_character = Mock(spec=Character)
    mock_character.name = name
    mock_character.level = level
    
    # Создаем моки для race и character_class
    mock_race = Mock()
    mock_race.name = "Человек"
    mock_character.race = mock_race
    
    mock_char_class = Mock()
    mock_char_class.name = "Воин"
    mock_character.character_class = mock_char_class
    
    # Настраиваем моки для характеристик
    attributes = {
        "strength": 16,
        "dexterity": 14,
        "constitution": 15,
        "intelligence": 12,
        "wisdom": 13,
        "charisma": 10,
    }
    
    for attr_name, value in attributes.items():
        mock_attr = Mock()
        mock_attr.value = value
        setattr(mock_character, attr_name, mock_attr)
    
    mock_character.hp_max = 45
    mock_character.hp_current = 35
    mock_character.ac = 16
    mock_character.gold = 150
    
    return mock_character


class TestCharacterSaveData:
    """Тесты данных сохранения персонажа."""

    def setup_method(self):
        """Настраивает тесты."""
        self.mock_character = Mock(spec=Character)
        self.mock_character.name = "Тестовый персонаж"
        self.mock_character.level = 5

        # Настраиваем моки для race и character_class
        mock_race = Mock()
        mock_race.name = "Человек"
        self.mock_character.race = mock_race

        mock_char_class = Mock()
        mock_char_class.name = "Воин"
        self.mock_character.character_class = mock_char_class

        # Настраиваем моки для характеристик
        mock_strength = Mock()
        mock_strength.value = 16
        self.mock_character.strength = mock_strength

        mock_dexterity = Mock()
        mock_dexterity.value = 14
        self.mock_character.dexterity = mock_dexterity

        mock_constitution = Mock()
        mock_constitution.value = 15
        self.mock_character.constitution = mock_constitution

        mock_intelligence = Mock()
        mock_intelligence.value = 12
        self.mock_character.intelligence = mock_intelligence

        mock_wisdom = Mock()
        mock_wisdom.value = 13
        self.mock_character.wisdom = mock_wisdom

        mock_charisma = Mock()
        mock_charisma.value = 10
        self.mock_character.charisma = mock_charisma

        self.mock_character.hp_max = 45
        self.mock_character.hp_current = 35
        self.mock_character.ac = 16
        self.mock_character.gold = 150

    def test_from_character(self):
        """Тестирует создание данных сохранения из персонажа."""
        with patch(
            "src.adapters.repositories.character_repository.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = (
                "2023-01-01T00:00:00"
            )

            save_data = CharacterSaveData.from_character(self.mock_character)

            assert save_data.name == "Тестовый персонаж"
            assert save_data.level == 5
            assert save_data.race_name == "Человек"
            assert save_data.class_name == "Воин"
            assert save_data.strength == 16
            assert save_data.dexterity == 14
            assert save_data.constitution == 15
            assert save_data.intelligence == 12
            assert save_data.wisdom == 13
            assert save_data.charisma == 10
            assert save_data.hp_max == 45
            assert save_data.hp_current == 35
            assert save_data.ac == 16
            assert save_data.gold == 150
            assert save_data.created_at == "2023-01-01T00:00:00"
            assert save_data.last_updated == "2023-01-01T00:00:00"
            assert save_data.version == "1.0"

    @patch("src.adapters.repositories.character_repository.RaceFactory")
    @patch("src.adapters.repositories.character_repository.CharacterClassFactory")
    def test_to_character(self, mock_class_factory, mock_race_factory):
        """Тестирует создание персонажа из данных сохранения."""
        # Настройка моков
        mock_race = Mock(spec=Race)
        mock_race.name = "Человек"
        mock_race_factory.create_race.return_value = mock_race
        mock_race_factory.get_race_key_by_name.return_value = "Человек"

        mock_char_class = Mock(spec=CharacterClass)
        mock_char_class.name = "Воин"
        mock_class_factory.create_class.return_value = mock_char_class
        mock_class_factory.get_class_key_by_name.return_value = "Воин"

        save_data = CharacterSaveData(
            name="Тестовый персонаж",
            level=5,
            race_name="Человек",
            class_name="Воин",
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=12,
            wisdom=13,
            charisma=10,
            hp_max=45,
            hp_current=35,
            ac=16,
            gold=150,
            created_at="2023-01-01T00:00:00",
            last_updated="2023-01-01T00:00:00",
        )

        character = save_data.to_character()

        assert character.name == "Тестовый персонаж"
        assert character.level == 5
        assert character.race == mock_race
        assert character.character_class == mock_char_class
        assert character.strength.value == 16
        assert character.dexterity.value == 14
        assert character.constitution.value == 15
        assert character.intelligence.value == 12
        assert character.wisdom.value == 13
        assert character.charisma.value == 10
        assert character.hp_max == 45
        assert character.hp_current == 35
        assert character.ac == 16
        assert character.gold == 150

        mock_race_factory.create_race.assert_called_once_with("Человек")
        mock_class_factory.create_class.assert_called_once_with("Воин")


class TestCharacterRepository:
    """Тесты репозитория персонажей."""

    def setup_method(self):
        """Настраивает тесты."""
        # Используем фиксированную временную директорию для всех тестов
        self.temp_dir = Path(tempfile.mkdtemp(prefix="dnd_test_"))
        self.repository = CharacterRepository(self.temp_dir)

    def teardown_method(self):
        """Очищает после тестов."""
        # Принудительно очищаем временную директорию
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception:
                pass  # Игнорируем ошибки при очистке

    def test_initialization_creates_directory(self):
        """Тестирует создание директории при инициализации."""
        assert self.temp_dir.exists()
        assert self.temp_dir.is_dir()

    def test_initialization_with_default_directory(self):
        """Тестирует инициализацию с директорией по умолчанию."""
        with patch("src.adapters.repositories.character_repository.Path") as mock_path:
            mock_path.return_value = self.temp_dir

            repo = CharacterRepository()

            assert repo.save_directory == self.temp_dir

    @patch("src.adapters.repositories.character_repository.json.dump")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.adapters.repositories.character_repository.datetime")
    def test_save_character_json(self, mock_datetime, mock_file, mock_json_dump):
        """Тестирует сохранение персонажа в JSON."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"

        mock_character = create_mock_character_for_manager()

        result = self.repository.save_character(mock_character, "json")

        assert result is True
        mock_file.assert_called_once()
        mock_json_dump.assert_called_once()

    @patch("src.adapters.repositories.character_repository.yaml.dump")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.adapters.repositories.character_repository.datetime")
    def test_save_character_yaml(self, mock_datetime, mock_file, mock_yaml_dump):
        """Тестирует сохранение персонажа в YAML."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"

        mock_character = create_mock_character_for_manager()

        result = self.repository.save_character(mock_character, "yaml")

        assert result is True
        mock_file.assert_called_once()
        mock_yaml_dump.assert_called_once()

    def test_save_character_unsupported_format(self):
        """Тестирует сохранение в неподдерживаемом формате."""
        mock_character = Mock(spec=Character)

        result = self.repository.save_character(mock_character, "xml")

        assert result is False

    def test_save_character_exception(self):
        """Тестирует обработку исключений при сохранении."""
        mock_character = Mock(spec=Character)
        # Вызываем исключение при создании CharacterSaveData
        with patch(
            "src.adapters.repositories.character_repository.CharacterSaveData.from_character",
            side_effect=Exception("Тестовая ошибка"),
        ):
            result = self.repository.save_character(mock_character, "json")
            assert result is False

    @patch("src.adapters.repositories.character_repository.json.load")
    @patch("builtins.open", new_callable=mock_open)
    @patch("src.adapters.repositories.character_repository.Path.exists")
    def test_load_character_json(self, mock_exists, mock_file, mock_json_load):
        """Тестирует загрузку персонажа из JSON."""
        mock_exists.return_value = True

        # Мокаем данные JSON
        mock_data = {
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
        mock_json_load.return_value = mock_data

        with patch(
            "src.adapters.repositories.character_repository.CharacterSaveData.to_character"
        ) as mock_to_char:
            mock_character = Mock(spec=Character)
            mock_to_char.return_value = mock_character

            result = self.repository.load_character("test.json")

            assert result == mock_character
            mock_to_char.assert_called_once()

    @patch("src.adapters.repositories.character_repository.Path.exists")
    def test_load_character_file_not_found(self, mock_exists):
        """Тестирует загрузку несуществующего файла."""
        mock_exists.return_value = False

        result = self.repository.load_character("nonexistent.json")

        assert result is None

    @patch("src.adapters.repositories.character_repository.Path.exists")
    def test_load_character_unsupported_format(self, mock_exists):
        """Тестирует загрузку файла в неподдерживаемом формате."""
        mock_exists.return_value = True

        result = self.repository.load_character("test.xml")

        assert result is None

    def test_load_character_exception(self):
        """Тестирует обработку исключений при загрузке."""
        with patch(
            "src.adapters.repositories.character_repository.Path.exists",
            return_value=True,
        ):
            with patch("builtins.open", side_effect=Exception("Тестовая ошибка")):
                result = self.repository.load_character("test.json")
                assert result is None

    def test_list_characters_empty(self):
        """Тестирует получение пустого списка персонажей."""
        result = self.repository.list_characters()
        assert result == []

    def test_list_characters_with_files(self):
        """Тестирует получение списка персонажей с файлами."""
        # Создаем тестовые файлы
        (self.temp_dir / "character1.json").touch()
        (self.temp_dir / "character2.yaml").touch()
        (self.temp_dir / "character3.yml").touch()
        (self.temp_dir / "readme.txt").touch()  # Не должен включаться
        (self.temp_dir / "subdir").mkdir()  # Не должен включаться

        result = self.repository.list_characters()

        assert len(result) == 3
        assert "character1.json" in result
        assert "character2.yaml" in result
        assert "character3.yml" in result
        assert "readme.txt" not in result

    def test_list_characters_exception(self):
        """Тестирует обработку исключений при получении списка."""
        with patch("pathlib.Path.glob", side_effect=Exception("Тестовая ошибка")):
            result = self.repository.list_characters()
            assert result == []

    @patch("src.adapters.repositories.character_repository.Path.exists")
    @patch("src.adapters.repositories.character_repository.Path.unlink")
    def test_delete_character_success(self, mock_unlink, mock_exists):
        """Тестирует успешное удаление персонажа."""
        mock_exists.return_value = True

        result = self.repository.delete_character("test.json")

        assert result is True
        mock_unlink.assert_called_once()

    @patch("src.adapters.repositories.character_repository.Path.exists")
    def test_delete_character_not_found(self, mock_exists):
        """Тестирует удаление несуществующего файла."""
        mock_exists.return_value = False

        result = self.repository.delete_character("nonexistent.json")

        assert result is False

    def test_delete_character_exception(self):
        """Тестирует обработку исключений при удалении."""
        with patch(
            "src.adapters.repositories.character_repository.Path.exists",
            return_value=True,
        ):
            with patch(
                "src.adapters.repositories.character_repository.Path.unlink",
                side_effect=Exception("Тестовая ошибка"),
            ):
                result = self.repository.delete_character("test.json")
                assert result is False


class TestCharacterManager:
    """Тесты менеджера персонажей."""

    def setup_method(self):
        """Настраивает тесты."""
        # Сбрасываем singleton перед каждым тестом
        CharacterManager._instance = None
        # Используем фиксированную временную директорию для всех тестов
        self.temp_dir = Path(tempfile.mkdtemp(prefix="dnd_mgr_test_"))

    def teardown_method(self):
        """Очищает после тестов."""
        CharacterManager._instance = None
        # Принудительно очищаем временную директорию
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception:
                pass  # Игнорируем ошибки при очистке

    def test_singleton_pattern(self):
        """Тестирует паттерн Singleton."""
        manager1 = CharacterManager()
        manager2 = CharacterManager()

        assert manager1 is manager2

    def test_get_instance(self):
        """Тестирует получение экземпляра."""
        manager1 = CharacterManager.get_instance()
        manager2 = CharacterManager.get_instance()

        assert manager1 is manager2

    @patch("src.adapters.repositories.character_repository.CharacterRepository")
    def test_save_character(self, mock_repository_class):
        """Тестирует сохранение персонажа."""
        mock_repository = Mock()
        mock_repository.save_character.return_value = True
        mock_repository_class.return_value = mock_repository

        manager = CharacterManager()
        mock_character = Mock(spec=Character)

        result = manager.save_character(mock_character)

        assert result is True
        mock_repository.save_character.assert_called_once_with(mock_character, "json")

    @patch("src.adapters.repositories.character_repository.CharacterRepository")
    def test_load_character(self, mock_repository_class):
        """Тестирует загрузку персонажа."""
        mock_repository = Mock()
        mock_character = Mock(spec=Character)
        mock_repository.load_character.return_value = mock_character
        mock_repository_class.return_value = mock_repository

        manager = CharacterManager()

        result = manager.load_character("test.json")

        assert result == mock_character
        mock_repository.load_character.assert_called_once_with("test.json")

    @patch("src.adapters.repositories.character_repository.CharacterRepository")
    def test_list_characters(self, mock_repository_class):
        """Тестирует получение списка персонажей."""
        mock_repository = Mock()
        mock_repository.list_characters.return_value = ["char1.json", "char2.json"]
        mock_repository_class.return_value = mock_repository

        manager = CharacterManager()

        result = manager.list_characters()

        assert result == ["char1.json", "char2.json"]
        mock_repository.list_characters.assert_called_once()

    @patch("src.adapters.repositories.character_repository.CharacterRepository")
    def test_delete_character(self, mock_repository_class):
        """Тестирует удаление персонажа."""
        mock_repository = Mock()
        mock_repository.delete_character.return_value = True
        mock_repository_class.return_value = mock_repository

        manager = CharacterManager()

        result = manager.delete_character("test.json")

        assert result is True
        mock_repository.delete_character.assert_called_once_with("test.json")

    @patch("src.adapters.repositories.character_repository.CharacterFactory")
    def test_create_new_character(self, mock_factory):
        """Тестирует создание нового персонажа."""
        mock_character = Mock(spec=Character)
        mock_factory.create_standard_character.return_value = mock_character

        manager = CharacterManager()

        result = manager.create_new_character("Тестовый персонаж")

        assert result == mock_character
        mock_factory.create_standard_character.assert_called_once_with(
            "Тестовый персонаж"
        )

    @patch("src.adapters.repositories.character_repository.CharacterRepository")
    def test_get_character_info(self, mock_repository_class):
        """Тестирует получение информации о персонаже."""
        mock_repository = Mock()
        mock_repository.save_directory = self.temp_dir
        mock_repository_class.return_value = mock_repository

        # Создаем тестовый файл
        test_data = {
            "name": "Тестовый персонаж",
            "level": 5,
            "race_name": "Человек",
            "class_name": "Воин",
            "created_at": "2023-01-01T00:00:00",
        }

        test_file = self.temp_dir / "test.json"
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        manager = CharacterManager()

        result = manager.get_character_info("test.json")

        assert result is not None
        assert result["name"] == "Тестовый персонаж"
        assert result["level"] == 5
        assert result["race"] == "Человек"
        assert result["class"] == "Воин"
        assert result["filename"] == "test.json"

    @patch("src.adapters.repositories.character_repository.CharacterRepository")
    def test_get_character_info_file_not_found(self, mock_repository_class):
        """Тестирует получение информации о несуществующем персонаже."""
        mock_repository = Mock()
        mock_repository.save_directory = self.temp_dir
        mock_repository_class.return_value = mock_repository

        manager = CharacterManager()

        result = manager.get_character_info("nonexistent.json")

        assert result is None

    @patch("src.adapters.repositories.character_repository.CharacterRepository")
    def test_get_character_info_unsupported_format(self, mock_repository_class):
        """Тестирует получение информацию о файле в неподдерживаемом формате."""
        mock_repository = Mock()
        mock_repository.save_directory = self.temp_dir
        mock_repository_class.return_value = mock_repository

        # Создаем тестовый файл в неподдерживаемом формате
        test_file = self.temp_dir / "test.xml"
        test_file.touch()

        manager = CharacterManager()

        result = manager.get_character_info("test.xml")

        assert result is None


class TestConvenienceFunctions:
    """Тесты удобных функций."""

    @patch("src.adapters.repositories.character_repository.CharacterManager")
    def test_save_character_function(self, mock_manager_class):
        """Тестирует функцию save_character."""
        mock_manager = Mock()
        mock_manager.save_character.return_value = True
        mock_manager_class.get_instance.return_value = mock_manager

        mock_character = Mock(spec=Character)

        result = save_character(mock_character)

        assert result is True
        mock_manager.save_character.assert_called_once_with(mock_character, "json")

    @patch("src.adapters.repositories.character_repository.CharacterManager")
    def test_load_character_function(self, mock_manager_class):
        """Тестирует функцию load_character."""
        mock_manager = Mock()
        mock_character = Mock(spec=Character)
        mock_manager.load_character.return_value = mock_character
        mock_manager_class.get_instance.return_value = mock_manager

        result = load_character("test.json")

        assert result == mock_character
        mock_manager.load_character.assert_called_once_with("test.json")

    @patch("src.adapters.repositories.character_repository.CharacterManager")
    def test_list_characters_function(self, mock_manager_class):
        """Тестирует функцию list_characters."""
        mock_manager = Mock()
        mock_manager.list_characters.return_value = ["char1.json", "char2.json"]
        mock_manager_class.get_instance.return_value = mock_manager

        result = list_characters()

        assert result == ["char1.json", "char2.json"]
        mock_manager.list_characters.assert_called_once()

    @patch("src.adapters.repositories.character_repository.CharacterManager")
    def test_get_character_info_function(self, mock_manager_class):
        """Тестирует функцию get_character_info."""
        mock_manager = Mock()
        mock_manager.get_character_info.return_value = {"name": "Test"}
        mock_manager_class.get_instance.return_value = mock_manager

        result = get_character_info("test.json")

        assert result == {"name": "Test"}
        mock_manager.get_character_info.assert_called_once_with("test.json")


class TestCharacterRepositoryIntegration:
    """Интеграционные тесты репозитория."""

    def setup_method(self):
        """Настраивает тесты."""
        # Используем фиксированную временную директорию для всех тестов
        self.temp_dir = Path(tempfile.mkdtemp(prefix="dnd_integration_test_"))
        self.repository = CharacterRepository(self.temp_dir)

    def teardown_method(self):
        """Очищает после тестов."""
        # Принудительно очищаем временную директорию
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception:
                pass  # Игнорируем ошибки при очистке

    @patch("src.adapters.repositories.character_repository.RaceFactory")
    @patch("src.adapters.repositories.character_repository.CharacterClassFactory")
    def test_full_save_load_cycle(self, mock_class_factory, mock_race_factory):
        """Тестирует полный цикл сохранения и загрузки."""
        # Настройка моков
        mock_race = Mock(spec=Race)
        mock_race.name = "Человек"
        mock_race_factory.create_race.return_value = mock_race

        mock_char_class = Mock(spec=CharacterClass)
        mock_char_class.name = "Воин"
        mock_class_factory.create_class.return_value = mock_char_class

        # Создаем тестового персонажа
        mock_character = create_mock_character_for_manager("Интеграционный тест", 3)
        mock_character.hp_max = 25
        mock_character.hp_current = 25
        mock_character.ac = 14
        mock_character.gold = 50

        # Сохраняем
        save_result = self.repository.save_character(mock_character, "json")
        assert save_result is True

        # Проверяем, что файл создан
        files = self.repository.list_characters()
        assert len(files) == 1
        assert files[0].endswith(".json")

        # Загружаем
        loaded_character = self.repository.load_character(files[0])
        assert loaded_character is not None

        # Проверяем данные
        assert loaded_character.name == "Интеграционный тест"
        assert loaded_character.level == 3


if __name__ == "__main__":
    pytest.main([__file__])
