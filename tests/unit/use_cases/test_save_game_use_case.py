"""Юнит-тесты для SaveGame Use Case.

Следует Clean Architecture - Use Case содержит бизнес-логику.
Работает с Repository абстракцией, не зная о реализации.
"""

from unittest.mock import Mock

import pytest

from src.entities.save_game_entity import SaveGameEntity
from src.frameworks.repositories.file_save_game_repository import (
    RepositoryError,
)
from src.use_cases.save_game_use_case import SaveGameUseCase


class TestSaveGameUseCase:
    """Тесты Use Case для сохранения игры.

    Use Case - это Application Layer:
    - Содержит бизнес-логику
    - Оркеструет работу сущностей
    - Не зависит от инфраструктуры
    """

    def setup_method(self):
        """Настройка тестовых данных согласно бизнес-правилам."""
        self.mock_repository = Mock()
        self.use_case = SaveGameUseCase(self.mock_repository)

        # Тестовые данные персонажа (бизнес-контекст)
        self.test_character_data = {
            "strength": 16,
            "dexterity": 14,
            "constitution": 15,
            "wisdom": 12,
            "intelligence": 13,
            "charisma": 10,
            "hp": 45,
            "max_hp": 50,
            "inventory": ["sword", "shield", "potion"],
        }

    def test_use_case_initialization(self):
        """Тест инициализации Use Case."""
        assert self.use_case._repository == self.mock_repository

    def test_create_new_save_success(self):
        """Тест успешного создания сохранения через Use Case.

        Use Case должен:
        - Валидировать бизнес-правила
        - Создать Entity
        - Делегировать сохранение репозиторию
        """
        # Arrange: настройка мока репозитория
        expected_save = Mock(spec=SaveGameEntity)
        expected_save.save_id = "test-save-123"
        self.mock_repository.save.return_value = expected_save

        # Act: вызов Use Case
        result = self.use_case.create_new_save(
            character_name="Test Character",
            character_level=5,
            character_class="Warrior",
            character_data=self.test_character_data,
            slot_number=2,
            location="Forest",
        )

        # Assert: проверка результатов
        assert result == expected_save
        self.mock_repository.save.assert_called_once()

        # Проверяем, что была создана валидная Entity
        call_args = self.mock_repository.save.call_args
        save_game_arg = call_args[0][0]  # Первый аргумент - SaveGame
        game_data_arg = call_args[0][1]  # Второй аргумент - game data

        assert save_game_arg.character_name == "Test Character"
        assert save_game_arg.character_level == 5
        assert save_game_arg.character_class == "Warrior"
        assert save_game_arg.slot_number == 2

        # Проверяем структуру данных игры (Use Case добавляет метаданные)
        assert "character" in game_data_arg
        assert game_data_arg["character"] == self.test_character_data
        assert "game_state" in game_data_arg
        assert game_data_arg["game_state"]["current_location"] == "Forest"

    def test_create_new_save_repository_error(self):
        """Тест создания сохранения с ошибкой репозитория."""
        # Настройка мока
        self.mock_repository.save.side_effect = RepositoryError(
            "Database error"
        )

        # Вызов и проверка исключения
        with pytest.raises(RepositoryError, match="Database error"):
            self.use_case.create_new_save(
                character_name="Test",
                character_level=1,
                character_class="Mage",
                character_data={},
                slot_number=1,
            )

    def test_create_new_save_validation_errors(self):
        """Тест валидации данных при создании сохранения."""
        # Тест пустого имени
        with pytest.raises(
            ValueError, match="Имя персонажа не может быть пустым"
        ):
            self.use_case.create_new_save(
                character_name="",
                character_level=1,
                character_class="Warrior",
                character_data={},
                slot_number=1,
            )

        # Тест невалидного уровня
        with pytest.raises(ValueError, match="Уровень должен быть от 1 до 20"):
            self.use_case.create_new_save(
                character_name="Test",
                character_level=0,  # Невалидный уровень
                character_class="Warrior",
                character_data={},
                slot_number=1,
            )

        # Тест невалидного слота
        with pytest.raises(
            ValueError, match="Номер слота должен быть от 1 до 10"
        ):
            self.use_case.create_new_save(
                character_name="Test",
                character_level=1,
                character_class="Warrior",
                character_data={},
                slot_number=0,  # Невалидный слот
            )

        # Репозиторий не должен быть вызван
        self.mock_repository.save.assert_not_called()

    def test_load_save_success(self):
        """Тест успешной загрузки сохранения."""
        # Настройка мока
        expected_data = {
            "character": self.test_character_data,
            "game_state": {"current_location": "Castle"},
        }
        self.mock_repository.load.return_value = expected_data

        # Вызов Use Case
        result = self.use_case.load_game("test-save-123")

        # Проверки
        assert result == expected_data
        self.mock_repository.load.assert_called_once_with("test-save-123")

    def test_load_save_not_found(self):
        """Тест загрузки несуществующего сохранения."""
        # Настройка мока
        self.mock_repository.load.return_value = None

        # Вызов Use Case
        result = self.use_case.load_game("non-existent")

        # Проверки
        assert result is None
        self.mock_repository.load.assert_called_once_with("non-existent")

    def test_load_save_repository_error(self):
        """Тест загрузки с ошибкой репозитория."""
        # Настройка мока
        self.mock_repository.load.side_effect = RepositoryError(
            "File not found"
        )

        # Вызов и проверка исключения
        with pytest.raises(RepositoryError, match="File not found"):
            self.use_case.load_game("test-save")

    def test_find_save_by_id_success(self):
        """Тест поиска сохранения по ID."""
        # Настройка мока
        expected_save = Mock(spec=SaveGameEntity)
        expected_save.save_id = "test-save-123"
        self.mock_repository.find_by_id.return_value = expected_save

        # Вызов Use Case
        result = self.use_case.get_save_by_id("test-save-123")

        # Проверки
        assert result == expected_save
        self.mock_repository.find_by_id.assert_called_once_with(
            "test-save-123"
        )

    def test_find_save_by_slot_success(self):
        """Тест поиска сохранения по слоту."""
        # Настройка мока
        expected_save = Mock(spec=SaveGameEntity)
        expected_save.slot_number = 3
        self.mock_repository.find_by_slot.return_value = expected_save

        # Вызов Use Case
        result = self.use_case.get_save_by_slot(3)

        # Проверки
        assert result == expected_save
        self.mock_repository.find_by_slot.assert_called_once_with(3)

    def test_find_all_saves_success(self):
        """Тест получения всех сохранений."""
        # Настройка мока
        expected_saves = [Mock(spec=SaveGameEntity) for _ in range(3)]
        self.mock_repository.find_all.return_value = expected_saves

        # Вызов Use Case
        result = self.use_case.get_all_saves()

        # Проверки
        assert result == expected_saves
        self.mock_repository.find_all.assert_called_once()

    def test_delete_save_success(self):
        """Тест успешного удаления сохранения."""
        # Настройка мока
        self.mock_repository.delete.return_value = True

        # Вызов Use Case
        result = self.use_case.delete_save("delete-save-123")

        # Проверки
        assert result is True
        self.mock_repository.delete.assert_called_once_with("delete-save-123")

    def test_delete_save_not_found(self):
        """Тест удаления несуществующего сохранения."""
        # Настройка мока
        self.mock_repository.delete.return_value = False

        # Вызов Use Case
        result = self.use_case.delete_save("non-existent")

        # Проверки
        assert result is False
        self.mock_repository.delete.assert_called_once_with("non-existent")

    def test_get_available_slots(self):
        """Тест получения доступных слотов."""
        # Настройка мока - имитируем занятые слоты
        self.mock_repository.find_all.return_value = [
            Mock(spec=SaveGameEntity, slot_number=1),
            Mock(spec=SaveGameEntity, slot_number=3),
        ]

        # Вызов Use Case
        result = self.use_case.get_available_slots()

        # Проверки
        assert 2 in result  # слот 2 свободен
        assert 4 in result  # слот 4 свободен
        assert 1 not in result  # слот 1 занят
        assert 3 not in result  # слот 3 занят
        assert len(result) == 8  # 10 слотов всего, 2 занято

    def test_business_logic_edge_cases(self):
        """Тест граничных случаев бизнес-логики."""
        # Тест с минимальными валидными значениями
        self.use_case.create_new_save(
            character_name="A",  # Минимальная длина
            character_level=1,  # Минимальный уровень
            character_class="W",  # Минимальная длина
            character_data={},
            slot_number=1,  # Минимальный слот
        )
        self.mock_repository.save.assert_called_once()

        # Тест с максимальными валидными значениями
        max_character_data = {
            "key" + str(i): "value" + str(i) for i in range(100)
        }
        self.use_case.create_new_save(
            character_name="A" * 50,  # Длинное имя
            character_level=20,  # Максимальный уровень
            character_class="Class" * 10,  # Длинный класс
            character_data=max_character_data,
            slot_number=10,  # Максимальный слот
            location="Very Long Location Name With Many Words",
        )
        assert self.mock_repository.save.call_count == 2

    def test_character_data_validation(self):
        """Тест валидации данных персонажа."""
        # Тест с пустыми данными персонажа (допустимо)
        self.use_case.create_new_save(
            character_name="Test",
            character_level=1,
            character_class="Warrior",
            character_data={},  # Пустые данные допустимы
            slot_number=1,
        )
        self.mock_repository.save.assert_called_once()

        # Тест с комплексными данными персонажа
        complex_data = {
            "abilities": {
                "strength": {"score": 16, "modifier": 3},
                "dexterity": {"score": 14, "modifier": 2},
            },
            "inventory": [
                {"id": "sword", "name": "Меч", "quantity": 1},
                {"id": "potion", "name": "Зелье", "quantity": 5},
            ],
            "quests": [
                {"id": "quest1", "status": "active"},
                {"id": "quest2", "status": "completed"},
            ],
        }
        self.use_case.create_new_save(
            character_name="Complex Character",
            character_level=10,
            character_class="Paladin",
            character_data=complex_data,
            slot_number=2,
        )
        assert self.mock_repository.save.call_count == 2
