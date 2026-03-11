"""Адаптер главного меню для консоли.

Следует Clean Architecture - преобразует данные меню в консольный вывод.
Расширяет функциональность приветственного экрана.
"""

import sys
from typing import Any

from src.dto.menu_dto import MenuControllerResponse, MenuStateDTO
from src.frameworks.console.menu_renderer import MenuRenderer


class MainMenuAdapter:
    """Адаптер главного меню для консольного вывода.

    Следует Clean Architecture - преобразует данные меню
    в консольный интерфейс с навигацией.
    """

    def __init__(self, use_colors: bool = True) -> None:
        """Инициализация адаптера.

        Args:
            use_colors: Использовать цветовой вывод
        """
        self.renderer = MenuRenderer(use_colors=use_colors)
        self._current_menu_state: MenuStateDTO | None = None

    def display_main_menu(self, menu_response: MenuControllerResponse) -> None:
        """Отобразить главное меню.

        Args:
            menu_response: Ответ контроллера с состоянием меню
        """
        if not menu_response.success or not menu_response.menu_state:
            self._display_error(menu_response.message)
            return

        self._current_menu_state = menu_response.menu_state

        # Получаем контекст для рендеринга
        context = self._prepare_render_context(menu_response.menu_state)

        # Рендерим меню
        rendered_menu = self.renderer.render_menu(context)

        # Выводим меню
        print(rendered_menu)

        # Отображаем приглашение к вводу
        self._show_input_prompt()

    def display_message(
        self, message: str, message_type: str = "info"
    ) -> None:
        """Отобразить сообщение.

        Args:
            message: Текст сообщения
            message_type: Тип сообщения
        """
        rendered_message = self.renderer.render_message(message, message_type)
        print(rendered_message)

    def get_user_input(self) -> str:
        """Получить ввод пользователя.

        Returns:
            Введенная строка
        """
        try:
            user_input = input().strip()
            return user_input
        except KeyboardInterrupt:
            return "exit"
        except EOFError:
            return "exit"

    def clear_screen(self) -> None:
        """Очистить экран."""
        if sys.platform == "win32":
            print("\n" * 50)
        else:
            print("\033[2J\033[H")

    def update_menu_state(self, menu_state: MenuStateDTO) -> None:
        """Обновить состояние меню.

        Args:
            menu_state: Новое состояние меню
        """
        self._current_menu_state = menu_state

    def refresh_display(self) -> None:
        """Обновить отображение меню."""
        if self._current_menu_state:
            context = self._prepare_render_context(self._current_menu_state)
            rendered_menu = self.renderer.render_menu(context)
            print(rendered_menu)
            self._show_input_prompt()

    def _prepare_render_context(
        self, menu_state: MenuStateDTO
    ) -> dict[str, Any]:
        """Подготовить контекст для рендеринга.

        Args:
            menu_state: Состояние меню

        Returns:
            Контекст для рендеринга
        """
        # Преобразуем DTO в формат для рендерера
        items = []
        for item_dto in menu_state.items:
            # Создаем временный объект для рендеринга
            class RenderItem:
                def __init__(self, dto):
                    self.id = dto.id
                    self.title = dto.title
                    self.description = dto.description
                    self.is_visible = dto.is_visible
                    self.is_enabled = dto.is_enabled
                    self.hotkey = dto.hotkey

                def get_display_text(self):
                    if self.hotkey:
                        return f"[{self.hotkey}] {self.title}"
                    return self.title

            items.append(RenderItem(item_dto))

        return {
            "title": menu_state.title,
            "items": items,
            "selected_index": menu_state.selected_index,
            "allow_back": menu_state.allow_back,
            "allow_exit": menu_state.allow_exit,
            "current_item": self._get_current_item(menu_state),
            "selectable_items": self._get_selectable_items(menu_state),
            "has_navigation": len(menu_state.selectable_items) > 1,
        }

    def _get_current_item(self, menu_state: MenuStateDTO):
        """Получить текущий пункт меню.

        Args:
            menu_state: Состояние меню

        Returns:
            Текущий пункт или None
        """
        selectable_items = self._get_selectable_items(menu_state)
        if 0 <= menu_state.selected_index < len(selectable_items):
            return selectable_items[menu_state.selected_index]
        return None

    def _get_selectable_items(self, menu_state: MenuStateDTO):
        """Получить выбираемые пункты меню.

        Args:
            menu_state: Состояние меню

        Returns:
            Список выбираемых пунктов
        """
        return [
            item
            for item in menu_state.items
            if item.is_visible and item.is_enabled
        ]

    def _display_error(self, error_message: str) -> None:
        """Отобразить ошибку.

        Args:
            error_message: Текст ошибки
        """
        rendered_error = self.renderer.render_message(
            f"ОШИБКА: {error_message}", "error"
        )
        print(rendered_error)

    def _show_input_prompt(self) -> None:
        """Показать приглашение к вводу."""
        prompt = self.renderer.render_input_prompt("Ваш выбор: ")
        print(prompt, end="", flush=True)
