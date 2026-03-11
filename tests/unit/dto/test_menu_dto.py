"""Юнит-тесты для DTO объектов меню.

Следует Clean Architecture - тестируем объекты передачи данных
без внешних зависимостей.
"""

from datetime import datetime

import pytest

from src.dto.menu_dto import (
    MenuControllerRequest,
    MenuControllerResponse,
    MenuItemDTO,
    MenuNavigationDirection,
    MenuStateDTO,
)
from src.entities.menu_entity import MenuActionType, MenuItem, MenuState


class TestMenuNavigationDirection:
    """Тесты для enum MenuNavigationDirection."""

    def test_navigation_direction_values(self):
        """Тест значений направлений."""
        assert MenuNavigationDirection.UP.value == "up"
        assert MenuNavigationDirection.DOWN.value == "down"
        assert MenuNavigationDirection.HOME.value == "home"
        assert MenuNavigationDirection.END.value == "end"

    def test_navigation_direction_uniqueness(self):
        """Тест уникальности значений."""
        values = [direction.value for direction in MenuNavigationDirection]
        assert len(values) == len(set(values))


class TestMenuControllerRequest:
    """Тесты для MenuControllerRequest."""

    def test_request_creation_minimal(self):
        """Тест создания запроса с минимальными данными."""
        request = MenuControllerRequest(action="navigate")

        assert request.action == "navigate"
        assert request.menu_id is None
        assert request.selection is None
        assert request.direction is None
        assert request.context is None

    def test_request_creation_full(self):
        """Тест создания запроса со всеми данными."""
        context = {"user_id": "123", "session": "abc"}
        request = MenuControllerRequest(
            action="select",
            menu_id="main_menu",
            selection="1",
            direction=MenuNavigationDirection.DOWN,
            context=context,
        )

        assert request.action == "select"
        assert request.menu_id == "main_menu"
        assert request.selection == "1"
        assert request.direction == MenuNavigationDirection.DOWN
        assert request.context == context

    def test_request_with_different_actions(self):
        """Тест запросов с разными действиями."""
        actions = ["navigate", "select", "create", "destroy", "update"]

        for action in actions:
            request = MenuControllerRequest(action=action)
            assert request.action == action

    def test_request_context_mutation(self):
        """Тест изменения контекста запроса."""
        original_context = {"key": "value"}
        request = MenuControllerRequest(
            action="test", context=original_context
        )

        # Изменяем оригинальный словарь
        original_context["new_key"] = "new_value"

        # Контекст запроса должен измениться (так как это ссылка)
        assert request.context["new_key"] == "new_value"


class TestMenuItemDTO:
    """Тесты для MenuItemDTO."""

    def test_menu_item_dto_creation_minimal(self):
        """Тест создания DTO с минимальными данными."""
        dto = MenuItemDTO(id="test", title="Test Item")

        assert dto.id == "test"
        assert dto.title == "Test Item"
        assert dto.description is None
        assert dto.action_type == MenuActionType.ACTION
        assert dto.target_menu is None
        assert dto.is_enabled is True
        assert dto.is_visible is True
        assert dto.hotkey is None
        assert dto.index is None
        assert dto.action is None

    def test_menu_item_dto_creation_full(self):
        """Тест создания DTO со всеми данными."""

        def action_func():
            return {"result": "test"}

        dto = MenuItemDTO(
            id="full_item",
            title="Full Item",
            description="Full description",
            action_type=MenuActionType.NAVIGATION,
            target_menu="submenu",
            is_enabled=False,
            is_visible=False,
            hotkey="F",
            index=5,
            action=action_func,
        )

        assert dto.id == "full_item"
        assert dto.title == "Full Item"
        assert dto.description == "Full description"
        assert dto.action_type == MenuActionType.NAVIGATION
        assert dto.target_menu == "submenu"
        assert dto.is_enabled is False
        assert dto.is_visible is False
        assert dto.hotkey == "F"
        assert dto.index == 5
        assert dto.action == action_func

    def test_get_display_text_without_hotkey(self):
        """Тест получения текста отображения без горячей клавиши."""
        dto = MenuItemDTO(id="test", title="Test Item")
        assert dto.get_display_text() == "Test Item"

    def test_get_display_text_with_hotkey(self):
        """Тест получения текста отображения с горячей клавишей."""
        dto = MenuItemDTO(id="test", title="Test Item", hotkey="N")
        assert dto.get_display_text() == "[N] Test Item"

    def test_from_entity_minimal(self):
        """Тест создания DTO из сущности с минимальными данными."""
        entity = MenuItem(
            id="entity_test",
            title="Entity Item",
            action_type=MenuActionType.ACTION,
            action=lambda: {"test": "result"},
        )

        dto = MenuItemDTO.from_entity(entity)

        assert dto.id == "entity_test"
        assert dto.title == "Entity Item"
        assert dto.action_type == MenuActionType.ACTION
        assert dto.is_enabled is True
        assert dto.is_visible is True
        assert dto.hotkey is None
        assert dto.action is not None

    def test_from_entity_full(self):
        """Тест создания DTO из полной сущности."""
        entity = MenuItem(
            id="full_entity",
            title="Full Entity Item",
            description="Entity description",
            action_type=MenuActionType.NAVIGATION,
            target_menu="target_menu",
            is_enabled=False,
            is_visible=False,
            hotkey="E",
            action=lambda: {"nav": "target"},
        )

        dto = MenuItemDTO.from_entity(entity)

        assert dto.id == "full_entity"
        assert dto.title == "Full Entity Item"
        assert dto.description == "Entity description"
        assert dto.action_type == MenuActionType.NAVIGATION
        assert dto.target_menu == "target_menu"
        assert dto.is_enabled is False
        assert dto.is_visible is False
        assert dto.hotkey == "E"
        assert dto.action is not None

    def test_to_entity_minimal(self):
        """Тест создания сущности из DTO с минимальными данными."""
        dto = MenuItemDTO(
            id="dto_test",
            title="DTO Item",
            action_type=MenuActionType.ACTION,
            action=lambda: {"dto": "result"},
        )

        entity = dto.to_entity()

        assert entity.id == "dto_test"
        assert entity.title == "DTO Item"
        assert entity.action_type == MenuActionType.ACTION
        assert entity.is_enabled is True
        assert entity.is_visible is True
        assert entity.hotkey is None
        assert entity.action is not None

    def test_to_entity_full(self):
        """Тест создания сущности из полного DTO."""

        def action_func():
            return {"converted": True}

        dto = MenuItemDTO(
            id="full_dto",
            title="Full DTO Item",
            description="DTO description",
            action_type=MenuActionType.NAVIGATION,
            target_menu="dto_target",
            is_enabled=False,
            is_visible=False,
            hotkey="D",
            action=action_func,
        )

        entity = dto.to_entity()

        assert entity.id == "full_dto"
        assert entity.title == "Full DTO Item"
        assert entity.description == "DTO description"
        assert entity.action_type == MenuActionType.NAVIGATION
        assert entity.target_menu == "dto_target"
        assert entity.is_enabled is False
        assert entity.is_visible is False
        assert entity.hotkey == "D"
        assert entity.action == action_func

    def test_round_trip_conversion(self):
        """Тест двустороннего преобразования DTO -> Entity -> DTO."""
        original_dto = MenuItemDTO(
            id="round_trip",
            title="Round Trip Item",
            description="Testing round trip",
            action_type=MenuActionType.ACTION,
            is_enabled=True,
            is_visible=True,
            hotkey="R",
            action=lambda: {"round": "trip"},
        )

        # DTO -> Entity -> DTO
        entity = original_dto.to_entity()
        converted_dto = MenuItemDTO.from_entity(entity)

        # Проверяем, что данные сохранились
        assert converted_dto.id == original_dto.id
        assert converted_dto.title == original_dto.title
        assert converted_dto.description == original_dto.description
        assert converted_dto.action_type == original_dto.action_type
        assert converted_dto.is_enabled == original_dto.is_enabled
        assert converted_dto.is_visible == original_dto.is_visible
        assert converted_dto.hotkey == original_dto.hotkey


class TestMenuStateDTO:
    """Тесты для MenuStateDTO."""

    def create_test_item_dtos(self):
        """Создать тестовые DTO пунктов меню."""
        return [
            MenuItemDTO(
                id="item1",
                title="Item 1",
                action_type=MenuActionType.ACTION,
                action=lambda: {"action": "item1"},
            ),
            MenuItemDTO(
                id="item2",
                title="Item 2",
                action_type=MenuActionType.NAVIGATION,
                target_menu="submenu",
            ),
            MenuItemDTO(
                id="item3", title="Item 3", action_type=MenuActionType.EXIT
            ),
        ]

    def test_menu_state_dto_creation_minimal(self):
        """Тест создания DTO состояния с минимальными данными."""
        items = self.create_test_item_dtos()
        dto = MenuStateDTO(title="Test Menu", items=items)

        assert dto.title == "Test Menu"
        assert dto.items == items
        assert dto.selected_index == 0  # По умолчанию
        assert dto.allow_back is True  # По умолчанию
        assert dto.allow_exit is True  # По умолчанию

    def test_menu_state_dto_creation_full(self):
        """Тест создания DTO состояния со всеми данными."""
        items = self.create_test_item_dtos()
        dto = MenuStateDTO(
            title="Full Menu",
            items=items,
            selected_index=2,
            allow_back=False,
            allow_exit=False,
        )

        assert dto.title == "Full Menu"
        assert dto.items == items
        assert dto.selected_index == 2
        assert dto.allow_back is False
        assert dto.allow_exit is False

    def test_from_entity(self):
        """Тест создания DTO из сущности состояния."""
        # Создаем сущность
        entity_items = [
            MenuItem(
                id="entity_item1",
                title="Entity Item 1",
                action_type=MenuActionType.ACTION,
                action=lambda: {"test": "1"},
            ),
            MenuItem(
                id="entity_item2",
                title="Entity Item 2",
                action_type=MenuActionType.NAVIGATION,
                target_menu="entity_submenu",
            ),
        ]

        entity = MenuState(
            title="Entity Menu",
            items=entity_items,
            selected_index=1,
            allow_back=False,
            allow_exit=True,
        )

        # Конвертируем в DTO
        dto = MenuStateDTO.from_entity(entity)

        # Проверяем
        assert dto.title == "Entity Menu"
        assert len(dto.items) == 2
        assert dto.selected_index == 1
        assert dto.allow_back is False
        assert dto.allow_exit is True

        # Проверяем конвертацию пунктов
        assert dto.items[0].id == "entity_item1"
        assert dto.items[0].title == "Entity Item 1"
        assert dto.items[1].id == "entity_item2"
        assert dto.items[1].target_menu == "entity_submenu"

    def test_to_entity(self):
        """Тест создания сущности из DTO состояния."""
        items = self.create_test_item_dtos()
        dto = MenuStateDTO(
            title="DTO Menu",
            items=items,
            selected_index=1,
            allow_back=False,
            allow_exit=True,
        )

        entity = dto.to_entity()

        # Проверяем
        assert entity.title == "DTO Menu"
        assert len(entity.items) == 3
        assert entity.selected_index == 1
        assert entity.allow_back is False
        assert entity.allow_exit is True

        # Проверяем конвертацию пунктов
        assert entity.items[0].id == "item1"
        assert entity.items[0].title == "Item 1"
        assert entity.items[1].id == "item2"
        assert entity.items[1].target_menu == "submenu"

    def test_round_trip_conversion(self):
        """Тест двустороннего преобразования."""
        items = self.create_test_item_dtos()
        original_dto = MenuStateDTO(
            title="Round Trip Menu",
            items=items,
            selected_index=2,
            allow_back=True,
            allow_exit=False,
        )

        # DTO -> Entity -> DTO
        entity = original_dto.to_entity()
        converted_dto = MenuStateDTO.from_entity(entity)

        # Проверяем, что данные сохранились
        assert converted_dto.title == original_dto.title
        assert len(converted_dto.items) == len(original_dto.items)
        assert converted_dto.selected_index == original_dto.selected_index
        assert converted_dto.allow_back == original_dto.allow_back
        assert converted_dto.allow_exit == original_dto.allow_exit

    def test_get_selectable_items(self):
        """Тест получения выбираемых пунктов."""
        items = self.create_test_item_dtos()
        items[1].is_enabled = False  # Отключаем второй пункт
        items[2].is_visible = False  # Скрываем третий пункт

        dto = MenuStateDTO(title="Test", items=items)
        selectable = dto.selectable_items

        assert len(selectable) == 1
        assert selectable[0].id == "item1"

    def test_get_current_item(self):
        """Тест получения текущего пункта."""
        items = self.create_test_item_dtos()
        dto = MenuStateDTO(title="Test", items=items, selected_index=1)

        current = dto.get_current_item()
        assert current is not None
        assert current.id == "item2"

    def test_get_current_item_no_selectable(self):
        """Тест получения текущего пункта когда нет выбираемых."""
        items = self.create_test_item_dtos()
        for item in items:
            item.is_enabled = False

        dto = MenuStateDTO(title="Test", items=items)
        current = dto.get_current_item()

        assert current is None

    def test_menu_state_dto_validation_edge_cases(self):
        """Тест граничных случаев валидации."""
        items = self.create_test_item_dtos()

        # Пустой заголовок
        with pytest.raises(ValueError):
            MenuStateDTO(title="", items=items)

        # Пустой список пунктов
        with pytest.raises(ValueError):
            MenuStateDTO(title="Test", items=[])

        # Индекс вне диапазона
        with pytest.raises(ValueError):
            MenuStateDTO(title="Test", items=items, selected_index=-1)

        with pytest.raises(ValueError):
            MenuStateDTO(title="Test", items=items, selected_index=5)


class TestMenuControllerResponse:
    """Тесты для MenuControllerResponse."""

    def test_response_creation_success(self):
        """Тест создания успешного ответа."""
        items = [MenuItemDTO(id="test", title="Test")]
        menu_state = MenuStateDTO(title="Test", items=items)
        data = {"result": "success"}

        response = MenuControllerResponse(
            success=True,
            message="Operation successful",
            menu_state=menu_state,
            action_result=data,
        )

        assert response.success is True
        assert response.message == "Operation successful"
        assert response.menu_state == menu_state
        assert response.action_result == data

    def test_response_creation_error(self):
        """Тест создания ответа с ошибкой."""
        response = MenuControllerResponse(
            success=False,
            message="Operation failed",
            menu_state=None,
            action_result=None,
        )

        assert response.success is False
        assert response.message == "Operation failed"
        assert response.menu_state is None
        assert response.action_result is None

    def test_response_creation_minimal(self):
        """Тест создания ответа с минимальными данными."""
        response = MenuControllerResponse(
            success=True, message="Minimal response"
        )

        assert response.success is True
        assert response.message == "Minimal response"
        assert response.menu_state is None
        assert response.action_result is None

    def test_response_with_complex_data(self):
        """Тест ответа со сложными данными."""
        items = [MenuItemDTO(id="complex", title="Complex")]
        menu_state = MenuStateDTO(title="Complex", items=items)

        complex_data = {
            "nested": {"value": 42, "list": [1, 2, 3]},
            "timestamp": datetime.now().isoformat(),
        }

        response = MenuControllerResponse(
            success=True,
            message="Complex operation",
            menu_state=menu_state,
            action_result=complex_data,
        )

        assert response.action_result == complex_data
        assert isinstance(response.action_result, dict)
        assert "nested" in response.action_result
