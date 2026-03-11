"""Контроллер главного меню.

Следует Clean Architecture - преобразует данные между слоями.
Управляет навигацией по главному меню игры.
"""

from src.dto.menu_dto import (
    MenuControllerRequest,
    MenuControllerResponse,
    MenuNavigationDirection,
    MenuStateDTO,
)
from src.entities.menu_entity import MenuActionType, MenuItem
from src.use_cases.menu_navigation_use_case import MenuNavigationUseCase


class MainMenuController:
    """Контроллер главного меню.

    Следует Clean Architecture - управляет главным меню игры,
    преобразуя пользовательский ввод в действия.
    """

    def __init__(self, menu_use_case: MenuNavigationUseCase) -> None:
        """Инициализация контроллера.

        Args:
            menu_use_case: Use Case навигации меню
        """
        self._menu_use_case = menu_use_case
        self._current_menu_state: MenuStateDTO | None = None

    def create_main_menu(self, language: str = "ru") -> MenuControllerResponse:
        """Создать главное меню.

        Args:
            language: Язык интерфейса

        Returns:
            Ответ контроллера с состоянием меню
        """
        try:
            # Создаем пункты главного меню
            menu_items = self._create_main_menu_items(language)

            # Создаем состояние меню через Use Case
            menu_state = self._menu_use_case.create_menu(
                title=self._get_menu_title(language), items=menu_items
            )

            # Преобразуем в DTO
            self._current_menu_state = MenuStateDTO.from_entity(menu_state)

            return MenuControllerResponse(
                success=True,
                message="Главное меню создано",
                menu_state=self._current_menu_state,
                data={"menu_type": "main"},
            )

        except Exception as e:
            return MenuControllerResponse(
                success=False,
                message=f"Ошибка создания главного меню: {str(e)}",
                menu_state=None,
            )

    def handle_navigation(
        self, request: MenuControllerRequest
    ) -> MenuControllerResponse:
        """Обработать навигацию по меню.

        Args:
            request: Запрос навигации

        Returns:
            Ответ контроллера с результатом навигации
        """
        try:
            if not self._current_menu_state:
                return MenuControllerResponse(
                    success=False,
                    message="Меню не инициализировано",
                    menu_state=None,
                )

            # Обрабатываем разные типы действий
            if request.action == "navigate":
                return self._handle_navigation_request(request)
            elif request.action == "select":
                return self._handle_selection_request(request)
            else:
                return MenuControllerResponse(
                    success=False,
                    message=f"Неизвестное действие: {request.action}",
                    menu_state=self._current_menu_state,
                )

        except Exception as e:
            return MenuControllerResponse(
                success=False,
                message=f"Ошибка навигации: {str(e)}",
                menu_state=self._current_menu_state,
            )

    def get_current_menu_state(self) -> MenuStateDTO | None:
        """Получить текущее состояние меню.

        Returns:
            Текущее состояние меню или None
        """
        return self._current_menu_state

    def _create_main_menu_items(self, language: str) -> list[MenuItem]:
        """Создать пункты главного меню.

        Args:
            language: Язык интерфейса

        Returns:
            Список пунктов меню
        """
        titles = self._get_menu_titles(language)

        return [
            MenuItem(
                id="new_game",
                title=titles["new_game"],
                description="Начать новую игру",
                action_type=MenuActionType.ACTION,
                action=lambda: {"action": "new_game"},
            ),
            MenuItem(
                id="create_character",
                title=titles["create_character"],
                description="Создать нового персонажа",
                action_type=MenuActionType.ACTION,
                action=lambda: {"action": "create_character"},
            ),
            MenuItem(
                id="load_game",
                title=titles["load_game"],
                description="Загрузить сохраненную игру",
                action_type=MenuActionType.ACTION,
                action=lambda: {"action": "load_game"},
            ),
            MenuItem(
                id="settings",
                title=titles["settings"],
                description="Настроить игру",
                action_type=MenuActionType.NAVIGATION,
                target_menu="settings",
            ),
            MenuItem(
                id="languages",
                title=titles["languages"],
                description="Изменить язык интерфейса",
                action_type=MenuActionType.NAVIGATION,
                target_menu="languages",
            ),
            MenuItem(
                id="exit",
                title=titles["exit"],
                description="Выйти из игры",
                action_type=MenuActionType.EXIT,
            ),
        ]

    def _get_menu_titles(self, language: str) -> dict[str, str]:
        """Получить заголовки меню для языка.

        Args:
            language: Код языка

        Returns:
            Словарь с заголовками
        """
        titles = {
            "ru": {
                "title": "Главное меню",
                "new_game": "Новая игра",
                "create_character": "Создать персонажа",
                "load_game": "Загрузить игру",
                "settings": "Настройки",
                "languages": "Languages",
                "exit": "Выход",
            },
            "en": {
                "title": "Main Menu",
                "new_game": "New Game",
                "create_character": "Create Character",
                "load_game": "Load Game",
                "settings": "Settings",
                "languages": "Language",
                "exit": "Exit",
            },
        }

        return titles.get(language, titles["ru"])

    def _get_menu_title(self, language: str) -> str:
        """Получить заголовок меню.

        Args:
            language: Код языка

        Returns:
            Заголовок меню
        """
        titles = self._get_menu_titles(language)
        return titles.get("title", "Главное меню")

    def _handle_navigation_request(
        self, request: MenuControllerRequest
    ) -> MenuControllerResponse:
        """Обработать запрос навигации.

        Args:
            request: Запрос навигации

        Returns:
            Ответ контроллера
        """
        if not request.direction:
            return MenuControllerResponse(
                success=False,
                message="Не указано направление навигации",
                menu_state=self._current_menu_state,
            )

        # Проверяем наличие состояния меню
        if not self._current_menu_state:
            return MenuControllerResponse(
                success=False,
                message="Меню не инициализировано",
                menu_state=None,
            )

        # Получаем выбираемые пункты
        selectable_items = [
            item
            for item in self._current_menu_state.items
            if item.is_visible and item.is_enabled
        ]

        if len(selectable_items) <= 1:
            return MenuControllerResponse(
                success=True,
                message="Навигация недоступна (только один пункт)",
                menu_state=self._current_menu_state,
            )

        # Обрабатываем навигацию
        current_index = self._current_menu_state.selected_index

        if request.direction == MenuNavigationDirection.UP:
            new_index = (current_index - 1) % len(selectable_items)
            self._current_menu_state.selected_index = new_index
        elif request.direction == MenuNavigationDirection.DOWN:
            new_index = (current_index + 1) % len(selectable_items)
            self._current_menu_state.selected_index = new_index
        elif request.direction == MenuNavigationDirection.HOME:
            self._current_menu_state.selected_index = 0
        elif request.direction == MenuNavigationDirection.END:
            self._current_menu_state.selected_index = len(selectable_items) - 1

        return MenuControllerResponse(
            success=True,
            message="Навигация выполнена",
            menu_state=self._current_menu_state,
        )

    def _handle_selection_request(
        self, request: MenuControllerRequest
    ) -> MenuControllerResponse:
        """Обработать запрос выбора пункта.

        Args:
            request: Запрос выбора

        Returns:
            Ответ контроллера с результатом действия
        """
        if not request.selection:
            return MenuControllerResponse(
                success=False,
                message="Не указан выбор",
                menu_state=self._current_menu_state,
            )

        # Проверяем наличие состояния меню
        if not self._current_menu_state:
            return MenuControllerResponse(
                success=False,
                message="Меню не инициализировано",
                menu_state=None,
            )

        # Получаем выбираемые пункты
        selectable_items = [
            item
            for item in self._current_menu_state.items
            if item.is_visible and item.is_enabled
        ]

        selected_item = None
        action_result = None

        # Проверяем выбор по цифре
        if request.selection.isdigit():
            selection_index = int(request.selection)
            if 1 <= selection_index <= len(selectable_items):
                selected_item = selectable_items[selection_index - 1]
                self._current_menu_state.selected_index = selection_index - 1
            elif selection_index == 0:  # 0 для настроек
                # Ищем пункт с действием NAVIGATION к settings
                for item in self._current_menu_state.items:
                    if (
                        item.action_type == MenuActionType.NAVIGATION
                        and item.target_menu == "settings"
                    ):
                        selected_item = item
                        break
        else:
            # Проверяем выбор по горячей клавише
            for item in selectable_items:
                if (
                    item.hotkey
                    and item.hotkey.lower() == request.selection.lower()
                ):
                    selected_item = item
                    break

        # Если пункт выбран, выполняем действие
        if selected_item:
            if (
                selected_item.action_type == MenuActionType.ACTION
                and selected_item.action
            ):
                action_result = selected_item.action()
            elif selected_item.action_type == MenuActionType.NAVIGATION:
                action_result = {"navigation": selected_item.target_menu}
            elif selected_item.action_type == MenuActionType.EXIT:
                action_result = {"navigation": "exit"}
            elif selected_item.action_type == MenuActionType.BACK:
                action_result = {"navigation": "back"}

            return MenuControllerResponse(
                success=True,
                message=f"Выбран пункт: {selected_item.title}",
                menu_state=self._current_menu_state,
                action_result=action_result,
            )
        else:
            return MenuControllerResponse(
                success=False,
                message=f"Неверный выбор: {request.selection}",
                menu_state=self._current_menu_state,
            )
