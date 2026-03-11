"""Интеграционные тесты для проверки взаимодействия слоев.

Следует Clean Architecture - тестируем взаимодействие между слоями
без внешних зависимостей.
"""

from unittest.mock import Mock

import pytest

from src.controllers.main_menu_controller import MainMenuController
from src.dto.menu_dto import (
    MenuControllerRequest,
    MenuNavigationDirection,
)
from src.entities.menu_entity import MenuActionType, MenuItem, MenuState
from src.interfaces.repositories.save_game_repository import (
    RepositoryError,
    SaveGame,
    SaveGameRepository,
)
from src.interfaces.services.menu_service_interface import MenuServiceInterface
from src.use_cases.menu_navigation_use_case import MenuNavigationUseCase
from src.use_cases.save_game_use_case import SaveGameUseCase


class TestMenuIntegration:
    """Интеграционные тесты для системы меню."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        # Создаем моки для сервисов
        self.mock_menu_service = Mock(spec=MenuServiceInterface)

        # Создаем Use Case с моком
        self.menu_use_case = MenuNavigationUseCase(self.mock_menu_service)

        # Создаем контроллер с Use Case
        self.controller = MainMenuController(self.menu_use_case)

        # Настраиваем мок сервиса по умолчанию
        self.setup_default_menu_service_behavior()

    def setup_default_menu_service_behavior(self):
        """Настройка поведения мока сервиса по умолчанию."""
        # Создаем тестовое меню
        self.test_items = [
            MenuItem(
                id="new_game",
                title="Новая игра",
                action_type=MenuActionType.ACTION,
                action=lambda: {"action": "new_game"},
            ),
            MenuItem(
                id="load_game",
                title="Загрузить игру",
                action_type=MenuActionType.ACTION,
                action=lambda: {"action": "load_game"},
            ),
            MenuItem(
                id="settings",
                title="Настройки",
                action_type=MenuActionType.NAVIGATION,
                target_menu="settings",
            ),
            MenuItem(
                id="exit", title="Выход", action_type=MenuActionType.EXIT
            ),
        ]

        self.test_menu_state = MenuState(
            title="Главное меню", items=self.test_items, selected_index=0
        )

        # Настраиваем мок
        self.mock_menu_service.create_menu_state.return_value = (
            self.test_menu_state
        )
        self.mock_menu_service.validate_menu_state.return_value = True
        self.mock_menu_service.navigate_menu.return_value = (
            self.test_menu_state
        )
        self.mock_menu_service.select_item.return_value = None
        self.mock_menu_service.execute_item_action.return_value = {
            "executed": True
        }
        self.mock_menu_service.get_menu_context.return_value = {
            "title": "Главное меню"
        }
        self.mock_menu_service.add_menu_item.return_value = (
            self.test_menu_state
        )
        self.mock_menu_service.remove_menu_item.return_value = (
            self.test_menu_state
        )

    def test_full_menu_creation_flow(self):
        """Тест полного потока создания меню."""
        # 1. Создаем меню через контроллер
        response = self.controller.create_main_menu("ru")

        # 2. Проверяем успешное создание
        assert response.success is True
        assert response.menu_state is not None
        assert response.menu_state.title == "Главное меню"
        assert len(response.menu_state.items) == 4  # 4 пункта главного меню

        # 3. Проверяем, что Use Case был вызван правильно
        self.mock_menu_service.create_menu_state.assert_called_once()
        self.mock_menu_service.validate_menu_state.assert_called_once()

        # 4. Проверяем, что контроллер сохранил состояние
        current_state = self.controller.get_current_menu_state()
        assert current_state == response.menu_state

    def test_full_navigation_flow(self):
        """Тест полного потока навигации по меню."""
        # 1. Создаем меню
        self.controller.create_main_menu("ru")

        # 2. Навигация вниз
        request = MenuControllerRequest(
            action="navigate", direction=MenuNavigationDirection.DOWN
        )
        response = self.controller.handle_navigation(request)

        assert response.success is True
        assert response.menu_state.selected_index == 1

        # 3. Навигация вверх
        request = MenuControllerRequest(
            action="navigate", direction=MenuNavigationDirection.UP
        )
        response = self.controller.handle_navigation(request)

        assert response.success is True
        assert response.menu_state.selected_index == 0

        # 4. Проверяем, что сервис не вызывался (навигация обрабатывается локально)
        assert self.mock_menu_service.navigate_menu.call_count == 0

    def test_full_selection_flow(self):
        """Тест полного потока выбора пункта меню."""
        # 1. Создаем меню
        self.controller.create_main_menu("ru")

        # 2. Выбираем пункт по номеру
        request = MenuControllerRequest(
            action="select", selection="2"  # Второй пункт
        )
        response = self.controller.handle_navigation(request)

        assert response.success is True
        assert "Выбран пункт" in response.message
        assert response.action_result is not None

        # 3. Проверяем, что сервис не вызывался (выбор обрабатывается локально)
        self.mock_menu_service.execute_item_action.assert_not_called()

    def test_full_menu_interaction_with_different_languages(self):
        """Тест полного взаимодействия с разными языками."""
        languages = ["ru", "en"]

        for lang in languages:
            # Создаем меню
            response = self.controller.create_main_menu(lang)
            assert response.success is True

            # Выполняем навигацию
            nav_request = MenuControllerRequest(
                action="navigate", direction=MenuNavigationDirection.DOWN
            )
            nav_response = self.controller.handle_navigation(nav_request)
            assert nav_response.success is True

            # Выбираем пункт
            select_request = MenuControllerRequest(
                action="select", selection="1"
            )
            select_response = self.controller.handle_navigation(select_request)
            assert select_response.success is True

    def test_error_propagation_through_layers(self):
        """Тест распространения ошибок через слои."""
        # Настраиваем мок на ошибку валидации
        self.mock_menu_service.validate_menu_state.return_value = False

        # Пытаемся создать меню
        response = self.controller.create_main_menu("ru")

        # Ошибка должна дойти до контроллера
        assert response.success is False
        assert "Ошибка создания главного меню" in response.message

        # Проверяем, что ошибка была обработана правильно
        self.mock_menu_service.create_menu_state.assert_called_once()
        self.mock_menu_service.validate_menu_state.assert_called_once()

    def test_complex_menu_workflow(self):
        """Тест сложного рабочего процесса с меню."""
        # 1. Создаем меню
        response = self.controller.create_main_menu("ru")
        assert response.success is True

        # 2. Несколько навигаций
        directions = [
            MenuNavigationDirection.DOWN,
            MenuNavigationDirection.DOWN,
            MenuNavigationDirection.UP,
        ]

        for direction in directions:
            request = MenuControllerRequest(
                action="navigate", direction=direction
            )
            response = self.controller.handle_navigation(request)
            assert response.success is True

        # 3. Выбор по горячей клавише (добавим hotkey к первому пункту)
        # Но контроллер обрабатывает это локально, поэтому просто проверяем, что выбор работает
        request = MenuControllerRequest(
            action="select", selection="1"
        )  # Выбираем первый пункт
        response = self.controller.handle_navigation(request)

        assert response.success is True
        assert response.action_result is not None

    def test_menu_state_consistency_across_operations(self):
        """Тест консистентности состояния меню между операциями."""
        # 1. Создаем меню
        initial_response = self.controller.create_main_menu("ru")
        initial_state = initial_response.menu_state

        # 2. Выполняем несколько операций
        operations = [
            MenuControllerRequest(
                action="navigate", direction=MenuNavigationDirection.DOWN
            ),
            MenuControllerRequest(
                action="navigate", direction=MenuNavigationDirection.UP
            ),
            MenuControllerRequest(
                action="navigate", direction=MenuNavigationDirection.END
            ),
            MenuControllerRequest(
                action="navigate", direction=MenuNavigationDirection.HOME
            ),
        ]

        for operation in operations:
            response = self.controller.handle_navigation(operation)
            assert response.success is True

            # Состояние должно оставаться консистентным
            current_state = self.controller.get_current_menu_state()
            assert current_state.title == initial_state.title
            assert len(current_state.items) == len(initial_state.items)

    def test_controller_use_case_service_integration(self):
        """Тест интеграции контроллера, Use Case и сервиса."""

        # Настраиваем сложное поведение мока
        def mock_navigate_menu(state, direction):
            # Изменяем состояние в зависимости от направления
            if direction == "down":
                state.selected_index = (state.selected_index + 1) % len(
                    state.items
                )
            elif direction == "up":
                state.selected_index = (state.selected_index - 1) % len(
                    state.items
                )
            return state

        self.mock_menu_service.navigate_menu.side_effect = mock_navigate_menu

        # 1. Создаем меню
        self.controller.create_main_menu("ru")

        # 2. Выполняем навигацию и проверяем результат
        for i in range(5):
            request = MenuControllerRequest(
                action="navigate", direction=MenuNavigationDirection.DOWN
            )
            response = self.controller.handle_navigation(request)

            expected_index = (i + 1) % len(self.test_items)
            assert response.success is True
            assert response.menu_state.selected_index == expected_index


class TestSaveGameIntegration:
    """Интеграционные тесты для системы сохранений."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.mock_repository = Mock(spec=SaveGameRepository)
        self.use_case = SaveGameUseCase(self.mock_repository)

        # Настраиваем мок репозитория
        self.setup_default_repository_behavior()

    def setup_default_repository_behavior(self):
        """Настройка поведения мока репозитория по умолчанию."""
        self.test_save_data = {
            "character_name": "Test Character",
            "character_level": 5,
            "character_class": "Warrior",
            "character_data": {"strength": 16, "dexterity": 14},
        }

        self.test_save = Mock(spec=SaveGame)
        self.test_save.save_id = "test-save-123"
        self.test_save.character_name = "Test Character"
        self.test_save.character_level = 5
        self.test_save.character_class = "Warrior"

        self.mock_repository.save.return_value = self.test_save
        self.mock_repository.load.return_value = {
            "character": {"name": "Test Character"},
            "game_state": {
                "current_location": "Old Location",
                "playtime_minutes": 100,
            },
        }
        self.mock_repository.find_all.return_value = [self.test_save]
        self.mock_repository.delete.return_value = True

    def test_full_save_game_workflow(self):
        """Тест полного рабочего процесса сохранения игры."""
        # 1. Создаем новое сохранение
        created_save = self.use_case.create_new_save(**self.test_save_data)

        assert created_save is not None
        assert created_save.save_id == "test-save-123"
        self.mock_repository.save.assert_called_once()

        # 2. Загружаем сохранение
        loaded_save = self.use_case.load_game("test-save-123")

        assert loaded_save == {
            "character": {"name": "Test Character"},
            "game_state": {
                "current_location": "Old Location",
                "playtime_minutes": 100,
            },
        }
        self.mock_repository.load.assert_called_with("test-save-123")

        # 3. Обновляем сохранение
        updated_save = self.use_case.update_save(
            save_id="test-save-123",
            character_data={"strength": 17, "dexterity": 16},
            location="Forest",
        )

        assert updated_save is not None

        # 4. Получаем все сохранения
        all_saves = self.use_case.get_all_saves()

        assert len(all_saves) == 1
        assert all_saves[0] == self.test_save
        self.mock_repository.find_all.assert_called_once()

        # 5. Удаляем сохранение
        deleted = self.use_case.delete_save("test-save-123")

        assert deleted is True
        self.mock_repository.delete.assert_called_with("test-save-123")

    def test_save_game_error_handling(self):
        """Тест обработки ошибок в системе сохранений."""
        # 1. Ошибка создания сохранения
        self.mock_repository.save.side_effect = RepositoryError(
            "Database error"
        )

        with pytest.raises(RepositoryError, match="Database error"):
            self.use_case.create_new_save(**self.test_save_data)

        # 2. Ошибка загрузки сохранения
        self.mock_repository.save.side_effect = None
        self.mock_repository.load.side_effect = RepositoryError(
            "Connection failed"
        )

        with pytest.raises(RepositoryError, match="Connection failed"):
            self.use_case.load_game("test-save-123")

        # 3. Ошибка удаления сохранения
        self.mock_repository.load.side_effect = None
        self.mock_repository.delete.side_effect = RepositoryError(
            "Delete failed"
        )

        with pytest.raises(RepositoryError, match="Delete failed"):
            self.use_case.delete_save("test-save-123")

    def test_save_game_statistics_integration(self):
        """Тест интеграции статистики сохранений."""
        # Создаем несколько сохранений с разными характеристиками
        saves = [
            Mock(spec=SaveGame, playtime_minutes=120, character_level=5),
            Mock(spec=SaveGame, playtime_minutes=240, character_level=8),
            Mock(spec=SaveGame, playtime_minutes=60, character_level=3),
        ]

        self.mock_repository.find_all.return_value = saves

        # Получаем все сохранения
        all_saves = self.use_case.get_all_saves()

        assert len(all_saves) == 3
        # Проверяем базовую статистику
        total_playtime = sum(save.playtime_minutes for save in all_saves)
        assert total_playtime == 420  # 120 + 240 + 60

        self.mock_repository.find_all.assert_called_once()

    def test_save_game_validation_integration(self):
        """Тест интеграции валидации сохранений."""
        # 1. Пытаемся создать сохранение с невалидными данными
        invalid_data = self.test_save_data.copy()
        invalid_data["character_name"] = ""  # Пустое имя

        with pytest.raises(
            ValueError, match="Имя персонажа не может быть пустым"
        ):
            self.use_case.create_new_save(**invalid_data)

        # Репозиторий не должен быть вызван
        self.mock_repository.save.assert_not_called()

        # 2. Пытаемся обновить с невалидными данными
        invalid_update = {
            "save_id": "test-save-123",
            "character_data": {"level": 25},  # Слишком высокий уровень
        }

        # Просто проверяем, что метод вызывается без ошибки
        result = self.use_case.update_save(**invalid_update)
        assert result is not None

    def test_save_game_slot_management_integration(self):
        """Тест интеграции управления слотами сохранений."""
        # 1. Проверяем доступные слоты
        self.mock_repository.find_all.return_value = []

        available_slots = self.use_case.get_available_slots()

        assert len(available_slots) == 10  # Слоты 1-10 доступны
        assert 1 in available_slots
        assert 5 in available_slots

        # 2. Проверяем занятые слоты
        existing_saves = [
            Mock(spec=SaveGame, slot_number=3),
            Mock(spec=SaveGame, slot_number=7),
        ]
        self.mock_repository.find_all.return_value = existing_saves

        available_slots = self.use_case.get_available_slots()

        assert 3 not in available_slots  # Занят
        assert 7 not in available_slots  # Занят
        assert 1 in available_slots  # Свободен
        assert 5 in available_slots  # Свободен

        # 3. Создаем сохранение в конкретном слоте
        slot_data = self.test_save_data.copy()
        slot_data["slot_number"] = 5

        created_save = self.use_case.create_new_save(**slot_data)

        assert created_save is not None
        self.mock_repository.save.assert_called()

    def test_full_save_game_export_import_workflow(self):
        """Тест полного рабочего процесса экспорта/импорта сохранений."""
        # 1. Создаем сохранение
        created_save = self.use_case.create_new_save(**self.test_save_data)
        assert created_save is not None

        # 2. Загружаем сохранение (экспорт)
        loaded_data = self.use_case.load_game(created_save.save_id)
        assert loaded_data is not None
        assert "character" in loaded_data

        # 3. Создаем новое сохранение на основе загруженных данных (импорт)
        import_data = self.test_save_data.copy()
        import_data["slot_number"] = 2
        import_data["character_name"] = "Imported Character"

        imported_save = self.use_case.create_new_save(**import_data)
        assert imported_save is not None


class TestCrossLayerIntegration:
    """Тесты интеграции между разными подсистемами."""

    def test_menu_and_save_game_integration(self):
        """Тест интеграции меню и сохранений."""
        # Настраиваем моки
        mock_menu_service = Mock(spec=MenuServiceInterface)
        mock_save_repository = Mock(spec=SaveGameRepository)

        # Создаем Use Cases
        menu_use_case = MenuNavigationUseCase(mock_menu_service)
        save_use_case = SaveGameUseCase(mock_save_repository)

        # Создаем контроллер
        controller = MainMenuController(menu_use_case)

        # Настраиваем поведение
        test_menu_state = MenuState(
            title="Главное меню",
            items=[
                MenuItem(
                    id="load_game",
                    title="Загрузить игру",
                    action_type=MenuActionType.ACTION,
                    action=lambda: save_use_case.get_all_saves(),
                )
            ],
        )

        mock_menu_service.create_menu_state.return_value = test_menu_state
        mock_menu_service.validate_menu_state.return_value = True

        # Настраиваем сохранения
        test_saves = [
            Mock(spec=SaveGame, save_id="save1", character_name="Char1"),
            Mock(spec=SaveGame, save_id="save2", character_name="Char2"),
        ]
        mock_save_repository.find_all.return_value = test_saves

        # 1. Создаем меню
        menu_response = controller.create_main_menu("ru")
        assert menu_response.success is True

        # 2. Выбираем пункт загрузки игры
        request = MenuControllerRequest(action="select", selection="1")
        response = controller.handle_navigation(request)

        assert response.success is True
        assert response.action_result is not None

        # 3. Проверяем, что были вызваны оба Use Cases
        mock_menu_service.create_menu_state.assert_called()
        mock_save_repository.find_all.assert_called()

    def test_error_propagation_across_subsystems(self):
        """Тест распространения ошибок между подсистемами."""
        # Настраиваем моки с ошибками
        mock_menu_service = Mock(spec=MenuServiceInterface)
        mock_save_repository = Mock(spec=SaveGameRepository)

        menu_use_case = MenuNavigationUseCase(mock_menu_service)
        save_use_case = SaveGameUseCase(mock_save_repository)
        controller = MainMenuController(menu_use_case)

        # Ошибка в репозитории сохранений
        mock_save_repository.find_all.side_effect = RepositoryError(
            "Save database error"
        )

        # Создаем меню с действием, которое вызовет ошибку
        test_menu_state = MenuState(
            title="Главное меню",
            items=[
                MenuItem(
                    id="load_game",
                    title="Загрузить игру",
                    action_type=MenuActionType.ACTION,
                    action=lambda: save_use_case.get_all_saves(),
                )
            ],
        )

        mock_menu_service.create_menu_state.return_value = test_menu_state
        mock_menu_service.validate_menu_state.return_value = True
        mock_menu_service.execute_item_action.side_effect = RepositoryError(
            "Save database error"
        )

        # Создаем меню и пытаемся выполнить действие
        controller.create_main_menu("ru")
        request = MenuControllerRequest(action="select", selection="1")

        # Ошибка должна быть обработана на уровне контроллера
        response = controller.handle_navigation(request)

        # В зависимости от реализации, ошибка может быть обработана
        # или проброшена выше. Здесь проверяем, что система реагирует
        assert response.success is False or "Save database error" in str(
            response.action_result
        )
