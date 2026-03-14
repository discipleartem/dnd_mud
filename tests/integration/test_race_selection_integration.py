"""Интеграционные тесты для RaceSelectionAdapter.

Тестируют интеграцию RaceService с MenuService и UI логику.
"""

import pytest
from unittest.mock import Mock

from src.frameworks.adapters.race_selection_adapter import RaceSelectionAdapter
from src.services.race_service import RaceService
from src.services.menu_service import MenuService
from src.entities.menu_entity import MenuActionType


class TestRaceSelectionIntegration:
    """Интеграционные тесты выбора расы."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.race_service = RaceService()
        self.menu_service = MenuService()
        self.adapter = RaceSelectionAdapter(self.race_service, self.menu_service)

    def test_create_race_selection_menu(self):
        """Тест создания меню выбора расы."""
        menu_state = self.adapter.create_race_selection_menu()
        
        assert menu_state.title == "Выбор расы"
        assert len(menu_state.items) > 0
        
        # Проверяем наличие основных рас
        race_titles = [item.title for item in menu_state.items]
        assert "Человек" in race_titles
        assert "Эльф" in race_titles
        assert "Полуорк" in race_titles

    def test_create_race_selection_menu_with_subraces(self):
        """Тест меню для рас с подрасами."""
        menu_state = self.adapter.create_race_selection_menu()
        
        # Находим эльфа в меню
        elf_item = None
        for item in menu_state.items:
            if item.title == "Эльф":
                elf_item = item
                break
        
        assert elf_item is not None
        assert elf_item.action_type == MenuActionType.NAVIGATION
        assert elf_item.target_menu == "subrace_elf"

    def test_create_race_selection_menu_without_subraces(self):
        """Тест меню для рас без подрас."""
        menu_state = self.adapter.create_race_selection_menu()
        
        # Находим человека в меню (можно выбирать сразу)
        human_item = None
        for item in menu_state.items:
            if item.title == "Человек":
                human_item = item
                break
        
        assert human_item is not None
        assert human_item.action_type == MenuActionType.ACTION

    def test_create_subrace_selection_menu(self):
        """Тест создания меню подрас."""
        menu_state = self.adapter._create_subrace_selection_menu("elf")
        
        assert "Эльф" in menu_state.title
        assert len(menu_state.items) > 1  # Подрасы + кнопка "Назад"
        
        # Проверяем наличие подрас
        subrace_titles = [item.title for item in menu_state.items if item.title != "Назад"]
        assert "Высший эльф" in subrace_titles
        assert "Лесной эльф" in subrace_titles

    def test_get_race_details(self):
        """Тест получения детальной информации о расе."""
        details = self.adapter.get_race_details("Человек")
        
        assert "Человек" in details
        assert "+1" in details  # Бонусы к характеристикам
        assert "medium" in details  # Размер

    def test_get_race_details_with_subrace(self):
        """Тест получения детальной информации о подрасе."""
        details = self.adapter.get_race_details("Эльф", "high_elf")
        
        assert "Высший эльф" in details
        assert "+1" in details  # Бонус к интеллекту
        assert "Эльф" in details  # Родительская раса

    def test_validate_race_choice_valid(self):
        """Тест валидации корректного выбора."""
        assert self.adapter.validate_race_choice("Человек") is True
        assert self.adapter.validate_race_choice("Эльф", "high_elf") is True

    def test_validate_race_choice_invalid(self):
        """Тест валидации некорректного выбора."""
        assert self.adapter.validate_race_choice("НесуществующаяРаса") is False
        assert self.adapter.validate_race_choice("Эльф", "НесуществующаяПодраса") is False

    def test_get_available_races(self):
        """Тест получения списка доступных рас."""
        races = self.adapter.get_available_races()
        
        assert len(races) > 0
        assert "Человек" in races
        assert "Эльф" in races
        assert "Полуорк" in races

    def test_get_subraces_for_race(self):
        """Тест получения подрас для расы."""
        # Раса с подрасами
        elf_subraces = self.adapter.get_subraces_for_race("Эльф")
        assert len(elf_subraces) > 0
        assert "Высший эльф" in elf_subraces
        assert "Лесной эльф" in elf_subraces
        
        # Раса без подрас
        human_subraces = self.adapter.get_subraces_for_race("Человек")
        assert len(human_subraces) == 0

    def test_select_race_action(self):
        """Тест действия выбора расы."""
        action = self.adapter._create_select_race_action("Человек")
        result = action()
        
        assert result.race_name == "Человек"
        assert result.subrace_name is None
        assert result.final_abilities["strength"] == 11  # 10 + 1

    def test_select_subrace_action(self):
        """Тест действия выбора подрасы."""
        action = self.adapter._create_select_subrace_action("Эльф", "high_elf")
        result = action()
        
        assert result.race_name == "Эльф"
        assert result.subrace_name == "high_elf"
        assert result.final_abilities["intelligence"] == 11  # 10 + 1

    def test_subrace_menu_action(self):
        """Тест действия перехода к меню подрас."""
        action = self.adapter._create_subrace_menu_action("Эльф")
        menu_state = action()
        
        assert "Эльф" in menu_state.title
        assert len(menu_state.items) > 1


class TestRaceSelectionController:
    """Интеграционные тесты контроллера выбора расы."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        from src.dependency_injection import ApplicationServices
        self.controller = RaceSelectionController(ApplicationServices())

    def test_controller_initialization(self):
        """Тест инициализации контроллера."""
        assert self.controller._services is not None
        assert self.controller._adapter is not None

    def test_get_adapter(self):
        """Тест получения адаптера."""
        adapter = self.controller.get_adapter()
        assert adapter is not None
        assert hasattr(adapter, 'create_race_selection_menu')

    def test_show_race_selection_keyboard_interrupt(self):
        """Тест прерывания выбора расы."""
        from unittest.mock import patch
        
        with patch('builtins.input', side_effect=KeyboardInterrupt("Выход")):
            with pytest.raises(KeyboardInterrupt, match="Выбор расы отменён"):
                self.controller.show_race_selection()


if __name__ == "__main__":
    pytest.main([__file__])
