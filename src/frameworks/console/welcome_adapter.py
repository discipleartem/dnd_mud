"""Консольный адаптер для приветственного экрана.

Следует Clean Architecture - оркестрация UI компонента.
Содержит только координацию, без бизнес-логики.
"""

from typing import Optional, Dict, Any

from src.frameworks.drivers.ui.console_welcome_ui import ConsoleWelcomeUI
from src.frameworks.console.main_menu_adapter import MainMenuAdapter
from src.dto.menu_dto import MenuControllerResponse


class ConsoleWelcomeScreenAdapter:
    """Консольный адаптер приветственного экрана.

    Следует Clean Architecture - координирует работу
    UI компонента для отображения данных.
    """

    def __init__(self, use_colors: bool = True) -> None:
        """Инициализация адаптера."""
        self._ui = ConsoleWelcomeUI()
        self._main_menu_adapter = MainMenuAdapter(use_colors=use_colors)
        self._use_main_menu = False

    def display(self, response_data: dict) -> None:
        """Отобразить приветственный экран.

        Args:
            response_data: Данные для отображения от контроллера
        """
        # Проверяем, нужно ли показывать главное меню
        if self._use_main_menu and "menu_state" in response_data:
            # Преобразуем данные в формат для меню
            menu_response = MenuControllerResponse(
                success=True,
                message="Главное меню",
                menu_state=response_data["menu_state"],
                data=response_data
            )
            self._main_menu_adapter.display_main_menu(menu_response)
        else:
            # Отображение через UI (старое поведение)
            self._ui.display_welcome_screen(response_data)

    def enable_main_menu(self) -> None:
        """Включить режим главного меню."""
        self._use_main_menu = True

    def disable_main_menu(self) -> None:
        """Выключить режим главного меню."""
        self._use_main_menu = False

    def is_main_menu_enabled(self) -> bool:
        """Проверить, включен ли режим главного меню.
        
        Returns:
            True если главное меню включено
        """
        return self._use_main_menu

    def display_main_menu(self, menu_response: MenuControllerResponse) -> None:
        """Отобразить главное меню.
        
        Args:
            menu_response: Ответ контроллера меню
        """
        self._main_menu_adapter.display_main_menu(menu_response)

    def get_user_input(self) -> str:
        """Получить ввод пользователя.
        
        Returns:
            Введенная строка
        """
        if self._use_main_menu:
            return self._main_menu_adapter.get_user_input()
        else:
            # Для старого приветственного экрана
            try:
                return input().strip()
            except KeyboardInterrupt:
                return "exit"
            except EOFError:
                return "exit"

    def clear_screen(self) -> None:
        """Очистить экран."""
        if self._use_main_menu:
            self._main_menu_adapter.clear_screen()
        else:
            # Простая очистка для старого режима
            print("\n" * 50)

    def display_message(self, message: str, message_type: str = "info") -> None:
        """Отобразить сообщение.
        
        Args:
            message: Текст сообщения
            message_type: Тип сообщения
        """
        if self._use_main_menu:
            self._main_menu_adapter.display_message(message, message_type)
        else:
            print(message)

    def refresh_display(self) -> None:
        """Обновить отображение меню."""
        if self._use_main_menu and self._main_menu_adapter._current_menu_state:
            context = self._main_menu_adapter._prepare_render_context(
                self._main_menu_adapter._current_menu_state
            )
            rendered_menu = self._main_menu_adapter.renderer.render_menu(context)
            self._main_menu_adapter.clear_screen()
            print(rendered_menu)
            self._main_menu_adapter._show_input_prompt()
