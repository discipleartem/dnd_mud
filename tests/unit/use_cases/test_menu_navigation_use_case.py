"""Юнит-тесты для Use Case навигации по меню.

Следует Clean Architecture - тестируем бизнес-логику Use Case
с моками для интерфейсов.
"""

from unittest.mock import Mock

import pytest

from src.entities.menu_entity import MenuActionType, MenuItem, MenuState
from src.interfaces.services.menu_service_interface import MenuServiceInterface
from src.use_cases.menu_navigation_use_case import MenuNavigationUseCase


class TestMenuNavigationUseCase:
    """Тесты для MenuNavigationUseCase."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.mock_menu_service = Mock(spec=MenuServiceInterface)
        self.use_case = MenuNavigationUseCase(self.mock_menu_service)

        # Создаем тестовые пункты меню
        self.test_items = [
            MenuItem(
                id="item1",
                title="Item 1",
                action_type=MenuActionType.ACTION,
                action=lambda: {"result": "item1"},
            ),
            MenuItem(
                id="item2",
                title="Item 2",
                action_type=MenuActionType.NAVIGATION,
                target_menu="submenu",
            ),
            MenuItem(
                id="item3", title="Item 3", action_type=MenuActionType.EXIT
            ),
        ]

        self.test_menu_state = MenuState(
            title="Test Menu", items=self.test_items, selected_index=0
        )

    def test_use_case_initialization(self):
        """Тест инициализации Use Case."""
        assert self.use_case._menu_service == self.mock_menu_service

    def test_create_menu_success(self):
        """Тест успешного создания меню."""
        # Настройка мока
        self.mock_menu_service.create_menu_state.return_value = (
            self.test_menu_state
        )
        self.mock_menu_service.validate_menu_state.return_value = True

        # Вызов Use Case
        result = self.use_case.create_menu("Test Menu", self.test_items)

        # Проверки
        self.mock_menu_service.create_menu_state.assert_called_once_with(
            "Test Menu", self.test_items
        )
        self.mock_menu_service.validate_menu_state.assert_called_once_with(
            self.test_menu_state
        )
        assert result == self.test_menu_state

    def test_create_menu_validation_failure(self):
        """Тест создания меню с ошибкой валидации."""
        # Настройка мока
        mock_menu_state = Mock()
        self.mock_menu_service.create_menu_state.return_value = mock_menu_state
        self.mock_menu_service.validate_menu_state.return_value = False

        # Вызов и проверка исключения
        with pytest.raises(
            ValueError, match="Невозможно создать меню: Test Menu"
        ):
            self.use_case.create_menu("Test Menu", self.test_items)

        self.mock_menu_service.create_menu_state.assert_called_once_with(
            "Test Menu", self.test_items
        )
        self.mock_menu_service.validate_menu_state.assert_called_once_with(
            mock_menu_state
        )

    def test_navigate_up(self):
        """Тест навигации вверх."""
        # Настройка мока
        updated_state = Mock()
        self.mock_menu_service.navigate_menu.return_value = updated_state

        # Вызов Use Case
        result = self.use_case.navigate_up(self.test_menu_state)

        # Проверки
        self.mock_menu_service.navigate_menu.assert_called_once_with(
            self.test_menu_state, "up"
        )
        assert result == updated_state

    def test_navigate_down(self):
        """Тест навигации вниз."""
        # Настройка мока
        updated_state = Mock()
        self.mock_menu_service.navigate_menu.return_value = updated_state

        # Вызов Use Case
        result = self.use_case.navigate_down(self.test_menu_state)

        # Проверки
        self.mock_menu_service.navigate_menu.assert_called_once_with(
            self.test_menu_state, "down"
        )
        assert result == updated_state

    def test_select_by_index_valid(self):
        """Тест выбора пункта по валидному индексу."""
        # Выбор второго пункта (индекс 2 в пользовательском вводе)
        result = self.use_case.select_by_index(self.test_menu_state, 2)

        assert result is not None
        assert result.id == "item2"
        assert self.test_menu_state.selected_index == 1  # 0-based индекс

    def test_select_by_index_invalid_too_low(self):
        """Тест выбора пункта по индексу меньше 1."""
        result = self.use_case.select_by_index(self.test_menu_state, 0)

        assert result is None
        assert self.test_menu_state.selected_index == 0  # Не изменился

    def test_select_by_index_invalid_too_high(self):
        """Тест выбора пункта по индексу больше количества пунктов."""
        result = self.use_case.select_by_index(self.test_menu_state, 10)

        assert result is None
        assert self.test_menu_state.selected_index == 0  # Не изменился

    def test_select_by_index_with_disabled_items(self):
        """Тест выбора по индексу с отключенными пунктами."""
        # Отключаем второй пункт
        self.test_items[1].is_enabled = False

        # Выбираем второй пункт - должен выбраться третий
        result = self.use_case.select_by_index(self.test_menu_state, 2)

        assert result is not None
        assert result.id == "item3"
        assert (
            self.test_menu_state.selected_index == 1
        )  # Индекс в выбираемых пунктах

    def test_select_by_hotkey(self):
        """Тест выбора по горячей клавише."""
        # Настройка мока
        expected_item = self.test_items[0]
        self.mock_menu_service.select_item.return_value = expected_item

        # Вызов Use Case
        result = self.use_case.select_by_hotkey(self.test_menu_state, "1")

        # Проверки
        self.mock_menu_service.select_item.assert_called_once_with(
            self.test_menu_state, "1"
        )
        assert result == expected_item

    def test_select_by_hotkey_not_found(self):
        """Тест выбора по несуществующей горячей клавише."""
        # Настройка мока
        self.mock_menu_service.select_item.return_value = None

        # Вызов Use Case
        result = self.use_case.select_by_hotkey(self.test_menu_state, "x")

        # Проверки
        self.mock_menu_service.select_item.assert_called_once_with(
            self.test_menu_state, "x"
        )
        assert result is None

    def test_execute_current_item_success(self):
        """Тест успешного выполнения текущего пункта."""
        # Настройка мока
        expected_result = {"action": "executed"}
        self.mock_menu_service.execute_item_action.return_value = (
            expected_result
        )

        # Вызов Use Case
        result = self.use_case.execute_current_item(self.test_menu_state)

        # Проверки
        current_item = self.test_menu_state.get_current_item()
        self.mock_menu_service.execute_item_action.assert_called_once_with(
            current_item
        )
        assert result == expected_result

    def test_execute_current_item_no_current_item(self):
        """Тест выполнения когда нет текущего пункта."""
        # Создаем меню без выбираемых пунктов
        for item in self.test_items:
            item.is_enabled = False

        # Вызов и проверка исключения
        with pytest.raises(ValueError, match="Нет выбранного пункта меню"):
            self.use_case.execute_current_item(self.test_menu_state)

        # Проверяем, что execute_item_action не вызывался
        self.mock_menu_service.execute_item_action.assert_not_called()

    def test_handle_selection_by_hotkey(self):
        """Тест обработки выбора по горячей клавише."""
        # Настройка мока
        expected_item = self.test_items[0]
        expected_result = {"result": "hotkey_success"}
        self.mock_menu_service.select_item.return_value = expected_item
        self.mock_menu_service.execute_item_action.return_value = (
            expected_result
        )

        # Вызов Use Case
        selected_item, result = self.use_case.handle_selection(
            self.test_menu_state, "N"
        )

        # Проверки
        assert selected_item == expected_item
        assert result == expected_result
        self.mock_menu_service.select_item.assert_called_once_with(
            self.test_menu_state, "N"
        )
        self.mock_menu_service.execute_item_action.assert_called_once_with(
            expected_item
        )

    def test_handle_selection_by_digit(self):
        """Тест обработки выбора по цифре."""
        # Настройка мока - сначала select_item возвращает None (не hotkey)
        # потом execute_item_action вызывается напрямую
        self.mock_menu_service.select_item.return_value = None
        expected_result = {"result": "digit_success"}
        self.mock_menu_service.execute_item_action.return_value = (
            expected_result
        )

        # Вызов Use Case
        selected_item, result = self.use_case.handle_selection(
            self.test_menu_state, "2"
        )

        # Проверки
        assert selected_item is not None
        assert selected_item.id == "item2"
        assert result == expected_result
        self.mock_menu_service.select_item.assert_called_once_with(
            self.test_menu_state, "2"
        )
        self.mock_menu_service.execute_item_action.assert_called_once()

    def test_handle_selection_not_found(self):
        """Тест обработки выбора когда пункт не найден."""
        # Настройка мока
        self.mock_menu_service.select_item.return_value = None

        # Вызов Use Case с несуществующим выбором
        selected_item, result = self.use_case.handle_selection(
            self.test_menu_state, "x"
        )

        # Проверки
        assert selected_item is None
        assert result is None
        self.mock_menu_service.select_item.assert_called_once_with(
            self.test_menu_state, "x"
        )
        self.mock_menu_service.execute_item_action.assert_not_called()

    def test_handle_selection_non_digit_selection(self):
        """Тест обработки выбора не цифрой и не hotkey."""
        # Настройка мока
        self.mock_menu_service.select_item.return_value = None

        # Вызов Use Case с текстом который не цифра
        selected_item, result = self.use_case.handle_selection(
            self.test_menu_state, "abc"
        )

        # Проверки
        assert selected_item is None
        assert result is None
        self.mock_menu_service.select_item.assert_called_once_with(
            self.test_menu_state, "abc"
        )
        self.mock_menu_service.execute_item_action.assert_not_called()

    def test_get_render_context(self):
        """Тест получения контекста для рендеринга."""
        # Настройка мока
        base_context = {"title": "Test Menu", "items": self.test_items}
        self.mock_menu_service.get_menu_context.return_value = base_context

        # Вызов Use Case
        result = self.use_case.get_render_context(self.test_menu_state)

        # Проверки
        assert result["title"] == "Test Menu"
        assert result["items"] == self.test_items
        assert "selectable_items" in result
        assert "current_item" in result
        assert "total_selectable" in result
        assert "has_navigation" in result
        assert "allow_back" in result
        assert "allow_exit" in result

        # Проверяем значения
        assert result["total_selectable"] == 3
        assert result["has_navigation"] is True
        assert result["allow_back"] is True
        assert result["allow_exit"] is True

        self.mock_menu_service.get_menu_context.assert_called_once_with(
            self.test_menu_state
        )

    def test_get_render_context_single_item(self):
        """Тест контекста рендеринга для меню с одним пунктом."""
        # Создаем меню с одним пунктом
        single_item = [self.test_items[0]]
        single_menu = MenuState(title="Single", items=single_item)

        # Настройка мока
        base_context = {"title": "Single", "items": single_item}
        self.mock_menu_service.get_menu_context.return_value = base_context

        # Вызов Use Case
        result = self.use_case.get_render_context(single_menu)

        # Проверки
        assert result["total_selectable"] == 1
        assert result["has_navigation"] is False

    def test_add_item(self):
        """Тест добавления пункта в меню."""
        # Настройка мока
        new_item = MenuItem(id="new", title="New Item", action=lambda: None)
        updated_state = Mock()
        self.mock_menu_service.add_menu_item.return_value = updated_state

        # Вызов Use Case
        result = self.use_case.add_item(self.test_menu_state, new_item)

        # Проверки
        self.mock_menu_service.add_menu_item.assert_called_once_with(
            self.test_menu_state, new_item
        )
        assert result == updated_state

    def test_remove_item(self):
        """Тест удаления пункта из меню."""
        # Настройка мока
        updated_state = Mock()
        self.mock_menu_service.remove_menu_item.return_value = updated_state

        # Вызов Use Case
        result = self.use_case.remove_item(self.test_menu_state, "item1")

        # Проверки
        self.mock_menu_service.remove_menu_item.assert_called_once_with(
            self.test_menu_state, "item1"
        )
        assert result == updated_state

    def test_use_case_with_different_menu_states(self):
        """Тест работы Use Case с различными состояниями меню."""
        # Создаем меню с отключенными пунктами
        self.test_items[1].is_enabled = False
        self.test_items[2].is_visible = False

        # Настройка мока
        self.mock_menu_service.select_item.return_value = None
        expected_result = {"result": "test"}
        self.mock_menu_service.execute_item_action.return_value = (
            expected_result
        )

        # Выбираем по индексу - должен выбрать первый доступный пункт
        selected_item, result = self.use_case.handle_selection(
            self.test_menu_state, "1"
        )

        assert selected_item is not None
        assert selected_item.id == "item1"
        assert result == expected_result

    def test_boundary_conditions(self):
        """Тест граничных условий."""
        # Настраиваем моки для возврата None
        self.mock_menu_service.select_item.return_value = None
        self.mock_menu_service.execute_item_action.return_value = None

        # Тест с пустым выбором
        selected_item, result = self.use_case.handle_selection(
            self.test_menu_state, ""
        )
        assert selected_item is None
        assert result is None

        # Тест с очень большим индексом
        result = self.use_case.select_by_index(self.test_menu_state, 999999)
        assert result is None

        # Тест с отрицательным индексом
        result = self.use_case.select_by_index(self.test_menu_state, -5)
        assert result is None
