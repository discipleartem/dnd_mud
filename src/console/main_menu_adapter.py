"""Адаптер для главного меню в консоли."""

from src.console.name_input_adapter import NameInputAdapter
from src.repositories.json_character_repository import JsonCharacterRepository
from src.services.name_input_service import NameInputService
from src.use_cases.main_menu import MainMenuUseCase, MenuItem


class MainMenuAdapter:
    """Адаптер главного меню для консольного интерфейса."""

    def __init__(self, main_menu: MainMenuUseCase):
        """Инициализировать адаптер главного меню.

        Args:
            main_menu: Use case главного меню
        """
        self.main_menu = main_menu
        # Инициализация зависимостей для создания персонажа
        character_repo = JsonCharacterRepository()
        self.name_input_service = NameInputService(character_repo)
        self.name_input_adapter = NameInputAdapter(self.name_input_service)
        self._setup_menu_items()

    def _setup_menu_items(self) -> None:
        """Настроить пункты меню."""
        # Новая игра
        self.main_menu.add_menu_item(
            MenuItem(title="Новая игра", action=self._new_game)
        )

        # Загрузить игру
        self.main_menu.add_menu_item(
            MenuItem(title="Загрузить игру", action=self._load_game)
        )

        # Создать персонажа
        self.main_menu.add_menu_item(
            MenuItem(title="Создать персонажа", action=self._create_character)
        )

        # Настройки
        self.main_menu.add_menu_item(
            MenuItem(title="Настройки", action=self._settings)
        )

    def _new_game(self) -> None:
        """Начать новую игру."""
        print("\nЗапуск новой игры...")
        print("В разработке...")
        input("Нажмите Enter для возврата в меню...")

    def _load_game(self) -> None:
        """Загрузить сохранённую игру."""
        print("\nЗагрузка игры...")
        print("В разработке...")
        input("Нажмите Enter для возврата в меню...")

    def _create_character(self) -> None:
        """Создать нового персонажа."""
        character = self.name_input_adapter.prompt_for_name()

        if character:
            self.name_input_adapter.show_success_message(character)
        else:
            self.name_input_adapter.show_cancellation_message()

        input("Нажмите Enter для возврата в меню...")

    def _settings(self) -> None:
        """Открыть настройки."""
        print("\nНастройки...")
        print("В разработке...")
        input("Нажмите Enter для возврата в меню...")

    def run(self) -> None:
        """Запустить главное меню."""
        self.main_menu.execute()
