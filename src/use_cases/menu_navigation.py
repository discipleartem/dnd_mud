"""Use Cases для навигации по меню."""

from typing import Final

from core.constants import GameConstants, MenuChoices
from interfaces.user_interface import UserInterface


class ShowMenuUseCase:
    """Use Case для отображения главного меню.
    
    Следует принципу единственной ответственности (SRP) -
    только отображение меню, без обработки выбора.
    """

    def __init__(self, ui: UserInterface, menu_factory) -> None:
        """Инициализация Use Case.
        
        Args:
            ui: Реализация пользовательского интерфейса
            menu_factory: Фабрика для создания меню
        """
        self.ui = ui
        self.menu_factory = menu_factory

    def execute(self) -> int:
        """Показать меню и вернуть выбор.
        
        Returns:
            Выбранный пункт меню
        """
        menu = self.menu_factory.create_main_menu(self.ui)
        return menu.show()


class HandleMenuChoiceUseCase:
    """Use Case для обработки выбора меню.
    
    Следует принципу единственной ответственности (SRP) -
    только обработка выбора, без отображения меню.
    """

    def __init__(self, ui: UserInterface) -> None:
        """Инициализация Use Case.
        
        Args:
            ui: Реализация пользовательского интерфейса
        """
        self.ui = ui
        
        # Сообщения для каждого выбора (DRY - нет дублирования)
        self._messages: Final[dict[int, str]] = {
            MenuChoices.NEW_GAME: "Выберите опцию:",
            MenuChoices.LOAD_GAME: "Функция загрузки пока недоступна.",
            MenuChoices.SETTINGS: "Функция настроек пока недоступна.",
            MenuChoices.MODS: "Функция модов пока недоступна.",
        }
        
        # Допустимые выборы
        self._valid_choices: Final[list[int]] = [
            MenuChoices.NEW_GAME,
            MenuChoices.LOAD_GAME,
            MenuChoices.SETTINGS,
            MenuChoices.MODS,
        ]

    def execute(self, choice: int) -> bool:
        """Обработать выбор меню.
        
        Args:
            choice: Выбранный пункт меню
            
        Returns:
            True для продолжения, False для выхода
        """
        if choice == MenuChoices.EXIT:
            self.ui.print_success("Спасибо за игру!")
            return False

        message = self._get_choice_message(choice)
        self.ui.print_info(message)

        if choice not in self._valid_choices:
            self.ui.get_input(GameConstants.PRESS_ENTER_MESSAGE)
        return True

    def _get_choice_message(self, choice: int) -> str:
        """Получить сообщение для выбора.
        
        Args:
            choice: Выбранный пункт меню
            
        Returns:
            Сообщение для вывода
        """
        return self._messages.get(choice, "Неверный выбор. Попробуйте снова.")
