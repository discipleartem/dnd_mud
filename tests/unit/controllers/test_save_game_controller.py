"""Тесты для SaveGameController.

Следует Clean Architecture - тестирование контроллера.
"""

from unittest.mock import Mock

import pytest

from src.controllers.save_game_controller import SaveGameController
from src.dto.save_game_dto import SaveGameRequest
from src.interfaces.repositories.save_game_repository import RepositoryError
from src.use_cases.save_game_use_case import SaveGameUseCase


class TestSaveGameController:
    """Тесты контроллера сохранений."""

    @pytest.fixture
    def mock_use_case(self) -> Mock:
        """Фикстура мок Use Case."""
        return Mock(spec=SaveGameUseCase)

    @pytest.fixture
    def controller(self, mock_use_case: Mock) -> SaveGameController:
        """Фикстура контроллера с мок Use Case."""
        return SaveGameController(mock_use_case)

    def test_handle_save_request_success(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест успешной обработки запроса сохранения."""
        # Настраиваем мок
        mock_save_game = Mock()
        mock_save_game.save_id = "test-id"
        mock_save_game.character_name = "Тестовый воин"
        mock_save_game.character_level = 1
        mock_save_game.character_class = "Воин"
        mock_save_game.save_time = "2026-03-11T23:00:00"
        mock_save_game.slot_number = 1
        mock_save_game.game_version = "1.0.0"
        mock_save_game.playtime_minutes = 0
        mock_save_game.location = "Начало пути"

        mock_use_case.create_new_save.return_value = mock_save_game

        # Создаем запрос
        request = SaveGameRequest(
            action="save",
            character_name="Тестовый воин",
            character_level=1,
            character_class="Воин",
            character_data={"name": "Тестовый воин"},
            slot_number=1,
        )

        # Обрабатываем запрос
        response = controller.handle_request(request)

        # Проверяем результат
        assert response.success is True
        assert "Игра успешно сохранена" in response.message
        assert response.save_game is not None
        assert response.save_game["character_name"] == "Тестовый воин"

        # Проверяем вызовы мока
        mock_use_case.create_new_save.assert_called_once()

    def test_handle_save_request_missing_data(
        self, controller: SaveGameController
    ) -> None:
        """Тест обработки запроса сохранения с отсутствующими данными."""
        request = SaveGameRequest(
            action="save",
            character_name="Тест",
            # Отсутствуют остальные обязательные поля
        )

        response = controller.handle_request(request)

        assert response.success is False
        assert "Отсутствуют обязательные данные" in response.message

    def test_handle_load_request_success(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест успешной обработки запроса загрузки."""
        # Настраиваем мок
        game_data = {
            "character": {"name": "Тестовый воин", "level": 1},
            "game_state": {"location": "Таверна"},
        }
        mock_save_game = Mock()
        mock_save_game.save_id = "test-id"
        mock_save_game.character_name = "Тестовый воин"
        mock_save_game.character_level = 1
        mock_save_game.character_class = "Воин"
        mock_save_game.save_time = "2026-03-11T23:00:00"
        mock_save_game.slot_number = 1
        mock_save_game.game_version = "1.0.0"
        mock_save_game.playtime_minutes = 0
        mock_save_game.location = "Начало пути"

        mock_use_case.load_game.return_value = game_data
        mock_use_case.get_save_by_id.return_value = mock_save_game

        request = SaveGameRequest(action="load", save_id="test-id")

        response = controller.handle_request(request)

        assert response.success is True
        assert "Игра успешно загружена" in response.message
        assert response.game_data == game_data
        assert response.save_game is not None

        mock_use_case.load_game.assert_called_once_with("test-id")
        mock_use_case.get_save_by_id.assert_called_once_with("test-id")

    def test_handle_load_request_not_found(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест обработки запроса загрузки несуществующего сохранения."""
        mock_use_case.load_game.return_value = None

        request = SaveGameRequest(action="load", save_id="non-existent-id")

        response = controller.handle_request(request)

        assert response.success is False
        assert "Сохранение не найдено" in response.message

    def test_handle_load_request_missing_id(
        self, controller: SaveGameController
    ) -> None:
        """Тест обработки запроса загрузки без ID."""
        request = SaveGameRequest(action="load")

        response = controller.handle_request(request)

        assert response.success is False
        assert "Отсутствует ID сохранения" in response.message

    def test_handle_delete_request_success(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест успешной обработки запроса удаления."""
        mock_use_case.delete_save.return_value = True

        request = SaveGameRequest(action="delete", save_id="test-id")

        response = controller.handle_request(request)

        assert response.success is True
        assert "Сохранение успешно удалено" in response.message

        mock_use_case.delete_save.assert_called_once_with("test-id")

    def test_handle_delete_request_not_found(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест обработки запроса удаления несуществующего сохранения."""
        mock_use_case.delete_save.return_value = False

        request = SaveGameRequest(action="delete", save_id="non-existent-id")

        response = controller.handle_request(request)

        assert response.success is False
        assert "Сохранение не найдено" in response.message

    def test_handle_list_request_success(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест успешной обработки запроса списка сохранений."""
        # Настраиваем мок
        mock_save1 = Mock()
        mock_save1.save_id = "id1"
        mock_save1.character_name = "Тест1"
        mock_save1.character_level = 1
        mock_save1.character_class = "Воин"
        mock_save1.save_time = "2026-03-11T23:00:00"
        mock_save1.slot_number = 1
        mock_save1.game_version = "1.0.0"
        mock_save1.playtime_minutes = 0
        mock_save1.location = "Начало пути"

        mock_save2 = Mock()
        mock_save2.save_id = "id2"
        mock_save2.character_name = "Тест2"
        mock_save2.character_level = 2
        mock_save2.character_class = "Плут"
        mock_save2.save_time = "2026-03-11T23:00:00"
        mock_save2.slot_number = 2
        mock_save2.game_version = "1.0.0"
        mock_save2.playtime_minutes = 30
        mock_save2.location = "Лес"

        mock_use_case.get_all_saves.return_value = [mock_save1, mock_save2]

        request = SaveGameRequest(action="list")

        response = controller.handle_request(request)

        assert response.success is True
        assert "Найдено сохранений: 2" in response.message
        assert response.all_saves is not None
        assert len(response.all_saves) == 2
        assert response.all_saves[0]["character_name"] == "Тест1"
        assert response.all_saves[1]["character_name"] == "Тест2"

        mock_use_case.get_all_saves.assert_called_once()

    def test_handle_get_available_slots_success(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест успешной обработки запроса доступных слотов."""
        mock_use_case.get_available_slots.return_value = [
            2,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
        ]

        request = SaveGameRequest(action="get_available_slots")

        response = controller.handle_request(request)

        assert response.success is True
        assert response.available_slots == [2, 4, 5, 6, 7, 8, 9, 10]

        mock_use_case.get_available_slots.assert_called_once()

    def test_handle_unknown_action(
        self, controller: SaveGameController
    ) -> None:
        """Тест обработки неизвестного действия."""
        request = SaveGameRequest(action="unknown")

        response = controller.handle_request(request)

        assert response.success is False
        assert "Неизвестное действие: unknown" in response.message

    def test_handle_repository_error(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест обработки ошибки репозитория."""
        mock_use_case.get_all_saves.side_effect = RepositoryError(
            "Ошибка доступа к файлам"
        )

        request = SaveGameRequest(action="list")

        response = controller.handle_request(request)

        assert response.success is False
        assert (
            "Ошибка получения списка: Ошибка доступа к файлам"
            in response.message
        )

    def test_handle_validation_error(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест обработки ошибки валидации."""
        mock_use_case.create_new_save.side_effect = ValueError(
            "Неверный уровень"
        )

        request = SaveGameRequest(
            action="save",
            character_name="Тест",
            character_level=0,  # Невалидный уровень
            character_class="Воин",
            character_data={},
        )

        response = controller.handle_request(request)

        assert response.success is False
        assert (
            "Отсутствуют обязательные данные для сохранения"
            in response.message
        )

    def test_get_save_slots_info(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест получения информации о слотах."""
        # Настраиваем мок
        mock_save = Mock()
        mock_save.save_id = "test-id"
        mock_save.character_name = "Тест"
        mock_save.character_level = 1
        mock_save.character_class = "Воин"
        mock_save.save_time = "2026-03-11T23:00:00"
        mock_save.slot_number = 1
        mock_save.game_version = "1.0.0"
        mock_save.playtime_minutes = 0
        mock_save.location = "Начало пути"

        mock_use_case.get_all_saves.return_value = [mock_save]

        slots = controller.get_save_slots_info()

        assert len(slots) == 10  # 10 слотов всего
        assert slots[0].is_occupied is True  # Слот 1 занят
        assert slots[0].save_info is not None
        assert slots[1].is_occupied is False  # Слот 2 свободен
        assert slots[1].save_info is None

    def test_get_character_preview(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест получения предпросмотра персонажа."""
        # Настраиваем мок
        game_data = {
            "character": {
                "name": "Тестовый воин",
                "level": 1,
                "class": "Воин",
                "race": "Человек",
                "background": "Воин",
                "abilities": {"strength": 16, "dexterity": 14},
                "hp": 12,
                "ac": 16,
            }
        }
        mock_use_case.load_game.return_value = game_data

        preview = controller.get_character_preview("test-id")

        assert preview is not None
        assert preview.name == "Тестовый воин"
        assert preview.level == 1
        assert preview.character_class == "Воин"
        assert preview.race == "Человек"
        assert preview.background == "Воин"
        assert preview.abilities == {"strength": 16, "dexterity": 14}
        assert preview.hp == 12
        assert preview.ac == 16

    def test_get_character_preview_not_found(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест получения предпросмотра для несуществующего сохранения."""
        mock_use_case.load_game.return_value = None

        preview = controller.get_character_preview("non-existent-id")

        assert preview is None

    def test_quick_save_success(
        self, controller: SaveGameController, mock_use_case: Mock
    ) -> None:
        """Тест успешного быстрого сохранения."""
        # Настраиваем мок
        mock_save_game = Mock()
        mock_save_game.save_id = "test-id"
        mock_save_game.character_name = "Тестовый воин"
        mock_save_game.character_level = 1
        mock_save_game.character_class = "Воин"
        mock_save_game.save_time = "2026-03-11T23:00:00"
        mock_save_game.slot_number = 1
        mock_save_game.game_version = "1.0.0"
        mock_save_game.playtime_minutes = 0
        mock_save_game.location = "Начало пути"

        mock_use_case.quick_save.return_value = mock_save_game

        response = controller.quick_save(
            character_name="Тестовый воин",
            character_level=1,
            character_class="Воин",
            character_data={"name": "Тестовый воин"},
            location="Таверна",
        )

        assert response.success is True
        assert "Игра быстро сохранена в слот 1" in response.message
        assert response.save_game is not None

        mock_use_case.quick_save.assert_called_once()
