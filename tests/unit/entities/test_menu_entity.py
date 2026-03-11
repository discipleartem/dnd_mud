"""Юнит-тесты для сущности меню.

Следует Clean Architecture - тестируем бизнес-логику сущностей
без внешних зависимостей.
"""

from unittest.mock import Mock

import pytest

from src.entities.menu_entity import MenuActionType, MenuItem, MenuState


class TestMenuItem:
    """Тесты для сущности MenuItem."""

    def test_menu_item_creation_valid(self):
        """Тест создания валидного пункта меню."""
        item = MenuItem(
            id="test_item",
            title="Test Item",
            description="Test description",
            action_type=MenuActionType.ACTION,
            action=lambda: {"result": "test"},
        )

        assert item.id == "test_item"
        assert item.title == "Test Item"
        assert item.description == "Test description"
        assert item.action_type == MenuActionType.ACTION
        assert item.is_enabled is True
        assert item.is_visible is True

    def test_menu_item_validation_empty_id(self):
        """Тест валидации: пустой ID."""
        with pytest.raises(
            ValueError, match="ID пункта меню не может быть пустым"
        ):
            MenuItem(id="", title="Test")

        with pytest.raises(
            ValueError, match="ID пункта меню не может быть пустым"
        ):
            MenuItem(id="   ", title="Test")

    def test_menu_item_validation_empty_title(self):
        """Тест валидации: пустой заголовок."""
        with pytest.raises(
            ValueError, match="Заголовок пункта меню не может быть пустым"
        ):
            MenuItem(id="test", title="")

        with pytest.raises(
            ValueError, match="Заголовок пункта меню не может быть пустым"
        ):
            MenuItem(id="test", title="   ")

    def test_menu_item_validation_title_too_long(self):
        """Тест валидации: слишком длинный заголовок."""
        long_title = "x" * 51
        with pytest.raises(
            ValueError, match="Заголовок пункта меню слишком длинный"
        ):
            MenuItem(id="test", title=long_title)

    def test_menu_item_validation_navigation_without_target(self):
        """Тест валидации: навигация без указания цели."""
        with pytest.raises(
            ValueError,
            match="Для пункта навигации необходимо указать target_menu",
        ):
            MenuItem(
                id="test", title="Test", action_type=MenuActionType.NAVIGATION
            )

    def test_menu_item_validation_action_without_callable(self):
        """Тест валидации: действие без callable."""
        with pytest.raises(
            ValueError, match="Для пункта действия необходимо указать action"
        ):
            MenuItem(
                id="test",
                title="Test",
                action_type=MenuActionType.ACTION,
                action=None,
            )

    def test_menu_item_is_selectable(self):
        """Тест проверки доступности выбора."""
        # Включенный и видимый
        item = MenuItem(id="test", title="Test", action=lambda: None)
        assert item.is_selectable() is True

        # Отключенный
        item.is_enabled = False
        assert item.is_selectable() is False

        # Невидимый
        item.is_enabled = True
        item.is_visible = False
        assert item.is_selectable() is False

    def test_menu_item_get_display_text_without_hotkey(self):
        """Тест получения текста отображения без горячей клавиши."""
        item = MenuItem(id="test", title="Test Item", action=lambda: None)
        assert item.get_display_text() == "Test Item"

    def test_menu_item_get_display_text_with_hotkey(self):
        """Тест получения текста отображения с горячей клавишей."""
        item = MenuItem(
            id="test", title="Test Item", hotkey="N", action=lambda: None
        )
        assert item.get_display_text() == "[N] Test Item"

    def test_menu_item_action_execution(self):
        """Тест выполнения действия."""
        mock_action = Mock(return_value={"result": "success"})
        item = MenuItem(
            id="test",
            title="Test",
            action_type=MenuActionType.ACTION,
            action=mock_action,
        )

        result = item.action()
        mock_action.assert_called_once()
        assert result == {"result": "success"}


class TestMenuState:
    """Тесты для сущности MenuState."""

    def create_test_items(self):
        """Создать тестовые пункты меню."""
        return [
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
            MenuItem(
                id="item3", title="Item 3", action_type=MenuActionType.EXIT
            ),
        ]

    def test_menu_state_creation_valid(self):
        """Тест создания валидного состояния меню."""
        items = self.create_test_items()
        state = MenuState(title="Test Menu", items=items, selected_index=1)

        assert state.title == "Test Menu"
        assert len(state.items) == 3
        assert state.selected_index == 1
        assert state.allow_back is True
        assert state.allow_exit is True

    def test_menu_state_validation_empty_title(self):
        """Тест валидации: пустой заголовок."""
        items = self.create_test_items()

        with pytest.raises(
            ValueError, match="Заголовок меню не может быть пустым"
        ):
            MenuState(title="", items=items)

        with pytest.raises(
            ValueError, match="Заголовок меню не может быть пустым"
        ):
            MenuState(title="   ", items=items)

    def test_menu_state_validation_no_items(self):
        """Тест валидации: нет пунктов меню."""
        with pytest.raises(
            ValueError, match="Меню должно содержать хотя бы один пункт"
        ):
            MenuState(title="Test", items=[])

    def test_menu_state_validation_invalid_selected_index(self):
        """Тест валидации: неверный индекс выбора."""
        items = self.create_test_items()

        with pytest.raises(
            ValueError, match="Индекс выбранного пункта вне диапазона"
        ):
            MenuState(title="Test", items=items, selected_index=-1)

        with pytest.raises(
            ValueError, match="Индекс выбранного пункта вне диапазона"
        ):
            MenuState(title="Test", items=items, selected_index=3)

    def test_menu_state_validation_no_visible_items(self):
        """Тест валидации: нет видимых пунктов."""
        items = self.create_test_items()
        for item in items:
            item.is_visible = False

        with pytest.raises(
            ValueError,
            match="Меню должно содержать хотя бы один видимый пункт",
        ):
            MenuState(title="Test", items=items)

    def test_menu_state_get_selectable_items(self):
        """Тест получения выбираемых пунктов."""
        items = self.create_test_items()
        items[1].is_enabled = False  # Отключаем второй пункт
        items[2].is_visible = False  # Скрываем третий пункт

        state = MenuState(title="Test", items=items)
        selectable = state.get_selectable_items()

        assert len(selectable) == 1
        assert selectable[0].id == "item1"

    def test_menu_state_get_current_item(self):
        """Тест получения текущего пункта."""
        items = self.create_test_items()
        state = MenuState(title="Test", items=items, selected_index=1)

        current = state.get_current_item()
        assert current is not None
        assert current.id == "item2"

    def test_menu_state_get_current_item_no_selectable(self):
        """Тест получения текущего пункта когда нет выбираемых."""
        items = self.create_test_items()
        for item in items:
            item.is_enabled = False

        state = MenuState(title="Test", items=items)
        current = state.get_current_item()

        assert current is None

    def test_menu_state_get_current_item_adjust_index(self):
        """Тест корректировки индекса при выходе за пределы."""
        items = self.create_test_items()
        items[2].is_visible = False  # Скрываем третий пункт

        state = MenuState(title="Test", items=items, selected_index=2)
        current = state.get_current_item()

        # Индекс должен быть скорректирован
        assert state.selected_index == 1
        assert current.id == "item2"

    def test_menu_state_move_selection_up(self):
        """Тест перемещения выбора вверх."""
        items = self.create_test_items()
        state = MenuState(title="Test", items=items, selected_index=1)

        old_index = state.selected_index
        moved = state.move_selection(-1)

        assert moved is True
        assert state.selected_index != old_index
        assert state.selected_index == 0

    def test_menu_state_move_selection_down(self):
        """Тест перемещения выбора вниз."""
        items = self.create_test_items()
        state = MenuState(title="Test", items=items, selected_index=0)

        old_index = state.selected_index
        moved = state.move_selection(1)

        assert moved is True
        assert state.selected_index != old_index
        assert state.selected_index == 1

    def test_menu_state_move_selection_wrap_around(self):
        """Тест зацикливания перемещения."""
        items = self.create_test_items()
        state = MenuState(title="Test", items=items, selected_index=2)

        # Движение вниз должно перейти к началу
        moved = state.move_selection(1)
        assert moved is True
        assert state.selected_index == 0

        # Движение вверх должно перейти к концу
        moved = state.move_selection(-1)
        assert moved is True
        assert state.selected_index == 2

    def test_menu_state_move_selection_single_item(self):
        """Тест перемещения при одном пункте."""
        items = [MenuItem(id="single", title="Single", action=lambda: None)]
        state = MenuState(title="Test", items=items)

        moved = state.move_selection(1)
        assert moved is False
        assert state.selected_index == 0

    def test_menu_state_select_by_hotkey(self):
        """Тест выбора по горячей клавише."""
        items = self.create_test_items()
        items[0].hotkey = "N"
        items[1].hotkey = "L"

        state = MenuState(title="Test", items=items)

        # Точный матч
        found = state.select_by_hotkey("N")
        assert found is not None
        assert found.id == "item1"

        # Нечувствительность к регистру
        found = state.select_by_hotkey("l")
        assert found is not None
        assert found.id == "item2"

        # Нет такой горячей клавиши
        found = state.select_by_hotkey("X")
        assert found is None

    def test_menu_state_select_by_hotkey_disabled_item(self):
        """Тест выбора по горячей клавише для отключенного пункта."""
        items = self.create_test_items()
        items[0].hotkey = "N"
        items[0].is_enabled = False

        state = MenuState(title="Test", items=items)
        found = state.select_by_hotkey("N")

        assert found is None


class TestMenuActionType:
    """Тесты для enum MenuActionType."""

    def test_menu_action_type_values(self):
        """Тест значений enum."""
        assert MenuActionType.NAVIGATION.value == "navigation"
        assert MenuActionType.ACTION.value == "action"
        assert MenuActionType.BACK.value == "back"
        assert MenuActionType.EXIT.value == "exit"

    def test_menu_action_type_uniqueness(self):
        """Тест уникальности значений."""
        values = [action_type.value for action_type in MenuActionType]
        assert len(values) == len(set(values))
