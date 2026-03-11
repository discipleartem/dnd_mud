"""Юнит-тесты для контроллера главного меню.

Следует Clean Architecture - Controller это адаптер интерфейса.
Преобразует данные между слоями и вызывает Use Cases.
"""

from unittest.mock import Mock

from src.controllers.main_menu_controller import MainMenuController
from src.dto.menu_dto import (
    MenuControllerRequest,
    MenuControllerResponse,
    MenuNavigationDirection,
    MenuStateDTO,
)
from src.entities.menu_entity import MenuActionType, MenuItem, MenuState
from src.use_cases.menu_navigation_use_case import MenuNavigationUseCase


class TestMainMenuController:
    """Тесты контроллера главного меню.

    Controller - это Interface Adapter, который:
    - Преобразует DTO в вызовы Use Cases
    - Обрабатывает ошибки и возвращает ответы
    - Не содержит бизнес-логики
    """

    def setup_method(self):
        """Настройка тестовых данных для контроллера."""
        self.mock_menu_use_case = Mock(spec=MenuNavigationUseCase)
        self.controller = MainMenuController(self.mock_menu_use_case)

        # Создаем тестовое состояние меню (бизнес-объекты)
        self.test_menu_state = MenuState(
            title="Test Menu",
            items=[
                MenuItem(
                    id="item1",
                    title="Item 1",
                    action_type=MenuActionType.ACTION,
                    action=lambda: {"action": "item1"},
                ),
                MenuItem(
                    id="item2",
                    title="Item 2",
                    action_type=MenuActionType.NAVIGATION,
                    target_menu="submenu",
                ),
            ],
            selected_index=0,
        )

    def test_controller_initialization(self):
        """Тест инициализации контроллера."""
        assert self.controller._menu_use_case == self.mock_menu_use_case
        assert self.controller._current_menu_state is None

    def test_create_main_menu_success(self):
        """Тест успешного создания меню через контроллер.

        Controller должен:
        - Вызвать Use Case для создания меню
        - Преобразовать результат в DTO
        - Вернуть успешный ответ
        """
        # Arrange: настройка мока Use Case
        self.mock_menu_use_case.create_menu.return_value = self.test_menu_state

        # Act: вызов контроллера
        result = self.controller.create_main_menu("ru")

        # Assert: проверка ответа контроллера
        assert isinstance(result, MenuControllerResponse)
        assert result.success is True
        assert result.message == "Главное меню создано"
        assert result.menu_state is not None
        assert result.data["menu_type"] == "main"

        # Проверяем, что Use Case был вызван правильно
        self.mock_menu_use_case.create_menu.assert_called_once()
        call_args = self.mock_menu_use_case.create_menu.call_args
        assert call_args.kwargs["title"] == "Главное меню"  # Заголовок меню
        assert len(call_args.kwargs["items"]) == 6  # 6 пунктов главного меню

    def test_create_main_menu_english(self):
        """Тест создания главного меню на английском."""
        # Настройка мока
        self.mock_menu_use_case.create_menu.return_value = self.test_menu_state

        # Вызов контроллера
        result = self.controller.create_main_menu("en")

        # Проверки
        assert result.success is True
        assert result.message == "Главное меню создано"

        # Проверяем вызов Use Case с английским заголовком
        self.mock_menu_use_case.create_menu.assert_called_once()
        call_args = self.mock_menu_use_case.create_menu.call_args
        assert call_args.kwargs["title"] == "Main Menu"

    def test_create_main_menu_use_case_error(self):
        """Тест создания меню с ошибкой Use Case."""
        # Настройка мока
        self.mock_menu_use_case.create_menu.side_effect = ValueError(
            "Menu creation failed"
        )

        # Вызов контроллера
        result = self.controller.create_main_menu("ru")

        # Проверки
        assert isinstance(result, MenuControllerResponse)
        assert result.success is False
        assert "Ошибка создания главного меню" in result.message
        assert result.menu_state is None
        assert self.controller._current_menu_state is None

    def test_create_main_menu_unexpected_error(self):
        """Тест создания меню с неожиданной ошибкой."""
        # Настройка мока
        self.mock_menu_use_case.create_menu.side_effect = RuntimeError(
            "Unexpected error"
        )

        # Вызов контроллера
        result = self.controller.create_main_menu("ru")

        # Проверки
        assert result.success is False
        assert "Ошибка создания главного меню" in result.message
        assert "Unexpected error" in result.message

    def test_get_current_menu_state_exists(self):
        """Тест получения текущего состояния меню когда оно существует."""
        # Устанавливаем состояние
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Вызов контроллера
        result = self.controller.get_current_menu_state()

        # Проверки
        assert result == menu_state_dto

    def test_get_current_menu_state_none(self):
        """Тест получения текущего состояния меню когда его нет."""
        # Вызов контроллера без установки состояния
        result = self.controller.get_current_menu_state()

        # Проверки
        assert result is None

    def test_handle_navigation_menu_not_initialized(self):
        """Тест обработки навигации когда меню не инициализировано."""
        # Создаем запрос
        request = MenuControllerRequest(
            action="navigate", direction=MenuNavigationDirection.DOWN
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is False
        assert result.message == "Меню не инициализировано"
        assert result.menu_state is None

    def test_handle_navigation_success(self):
        """Тест успешной обработки навигации."""
        # Устанавливаем состояние
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос
        request = MenuControllerRequest(
            action="navigate", direction=MenuNavigationDirection.DOWN
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is True
        assert result.message == "Навигация выполнена"
        assert result.menu_state is not None
        assert (
            result.menu_state.selected_index == 1
        )  # Индекс должен измениться

    def test_handle_navigation_up(self):
        """Тест навигации вверх."""
        # Устанавливаем состояние с выбранным вторым пунктом
        self.test_menu_state.selected_index = 1
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос
        request = MenuControllerRequest(
            action="navigate", direction=MenuNavigationDirection.UP
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is True
        assert result.menu_state.selected_index == 0

    def test_handle_navigation_home(self):
        """Тест навигации в начало."""
        # Устанавливаем состояние с выбранным вторым пунктом
        self.test_menu_state.selected_index = 1
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос
        request = MenuControllerRequest(
            action="navigate", direction=MenuNavigationDirection.HOME
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is True
        assert result.menu_state.selected_index == 0

    def test_handle_navigation_end(self):
        """Тест навигации в конец."""
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос
        request = MenuControllerRequest(
            action="navigate", direction=MenuNavigationDirection.END
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is True
        assert result.menu_state.selected_index == 1  # Последний индекс

    def test_handle_navigation_no_direction(self):
        """Тест навигации без указания направления."""
        # Устанавливаем состояние
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос без направления
        request = MenuControllerRequest(action="navigate")

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is False
        assert "Не указано направление навигации" in result.message

    def test_handle_navigation_single_item(self):
        """Тест навигации когда только один пункт."""
        # Создаем меню с одним пунктом
        single_item_menu = MenuState(
            title="Single", items=[self.test_menu_state.items[0]]
        )
        menu_state_dto = MenuStateDTO.from_entity(single_item_menu)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос
        request = MenuControllerRequest(
            action="navigate", direction=MenuNavigationDirection.DOWN
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is True
        assert "Навигация недоступна" in result.message

    def test_handle_selection_success_by_number(self):
        """Тест успешного выбора пункта по номеру."""
        # Устанавливаем состояние
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос
        request = MenuControllerRequest(
            action="select", selection="2"  # Второй пункт
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is True
        assert "Выбран пункт" in result.message
        assert result.action_result == {"navigation": "submenu"}
        assert result.menu_state.selected_index == 1

    def test_handle_selection_success_by_hotkey(self):
        """Тест успешного выбора пункта по горячей клавише."""
        # Добавляем горячую клавишу к пункту
        self.test_menu_state.items[0].hotkey = "N"
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос
        request = MenuControllerRequest(
            action="select",
            selection="n",  # Горячая клавиша (нечувствительна к регистру)
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is True
        assert "Выбран пункт" in result.message
        assert result.action_result == {"action": "item1"}

    def test_handle_selection_special_zero(self):
        """Тест выбора специального пункта 0 (настройки)."""
        # Добавляем пункт настроек
        settings_item = MenuItem(
            id="settings",
            title="Settings",
            action_type=MenuActionType.NAVIGATION,
            target_menu="settings",
        )
        self.test_menu_state.items.append(settings_item)

        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос
        request = MenuControllerRequest(
            action="select", selection="0"  # Специальный выбор настроек
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is True
        assert result.action_result == {"navigation": "settings"}

    def test_handle_selection_invalid_number(self):
        """Тест выбора по неверному номеру."""
        # Устанавливаем состояние
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос с неверным номером
        request = MenuControllerRequest(
            action="select", selection="9"  # Слишком большой номер
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is False
        assert "Неверный выбор" in result.message

    def test_handle_selection_invalid_hotkey(self):
        """Тест выбора по неверной горячей клавише."""
        # Устанавливаем состояние
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос с неверной горячей клавишей
        request = MenuControllerRequest(
            action="select", selection="x"  # Несуществующая горячая клавиша
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is False
        assert "Неверный выбор" in result.message

    def test_handle_selection_no_selection(self):
        """Тест выбора без указания выбора."""
        # Устанавливаем состояние
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос без выбора
        request = MenuControllerRequest(action="select")

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is False
        assert "Не указан выбор" in result.message

    def test_handle_selection_exit_action(self):
        """Тест выбора пункта с действием выхода."""
        # Добавляем пункт выхода
        exit_item = MenuItem(
            id="exit", title="Exit", action_type=MenuActionType.EXIT
        )
        self.test_menu_state.items.append(exit_item)

        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос
        request = MenuControllerRequest(
            action="select", selection="3"  # Третий пункт (выход)
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is True
        assert result.action_result == {"navigation": "exit"}

    def test_handle_navigation_unknown_action(self):
        """Тест обработки неизвестного действия."""
        # Устанавливаем состояние
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос с неизвестным действием
        request = MenuControllerRequest(action="unknown")

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is False
        assert "Неизвестное действие" in result.message
        assert result.menu_state is not None  # Состояние должно вернуться

    def test_handle_navigation_with_disabled_items(self):
        """Тест навигации с отключенными пунктами."""
        # Отключаем второй пункт
        self.test_menu_state.items[1].is_enabled = False
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос навигации
        request = MenuControllerRequest(
            action="navigate", direction=MenuNavigationDirection.DOWN
        )

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is True
        assert (
            "Навигация недоступна" in result.message
        )  # Только один доступный пункт

    def test_create_main_menu_items_structure(self):
        """Тест структуры создаваемых пунктов меню."""
        # Настройка мока
        self.mock_menu_use_case.create_menu.return_value = self.test_menu_state

        # Вызов контроллера
        self.controller.create_main_menu("ru")

        # Проверяем структуру созданных пунктов
        call_args = self.mock_menu_use_case.create_menu.call_args
        items = call_args.kwargs["items"]

        # Проверяем количество пунктов
        assert len(items) == 6

        # Проверяем ID пунктов
        item_ids = [item.id for item in items]
        expected_ids = [
            "new_game",
            "create_character",
            "load_game",
            "settings",
            "languages",
            "exit",
        ]
        assert item_ids == expected_ids

        # Проверяем типы действий
        assert items[0].action_type == MenuActionType.ACTION  # new_game
        assert (
            items[1].action_type == MenuActionType.ACTION
        )  # create_character
        assert items[2].action_type == MenuActionType.ACTION  # load_game
        assert items[3].action_type == MenuActionType.NAVIGATION  # settings
        assert items[4].action_type == MenuActionType.NAVIGATION  # languages
        assert items[5].action_type == MenuActionType.EXIT  # exit

    def test_error_handling_in_navigation_methods(self):
        """Тест обработки ошибок в методах навигации."""
        # Устанавливаем состояние
        menu_state_dto = MenuStateDTO.from_entity(self.test_menu_state)
        self.controller._current_menu_state = menu_state_dto

        # Создаем запрос, который может вызвать ошибку
        request = MenuControllerRequest(
            action="navigate", direction=MenuNavigationDirection.DOWN
        )

        # Имитируем ошибку при доступе к атрибутам
        self.controller._current_menu_state.items = None

        # Вызов контроллера
        result = self.controller.handle_navigation(request)

        # Проверки
        assert result.success is False
        assert "Ошибка навигации" in result.message
