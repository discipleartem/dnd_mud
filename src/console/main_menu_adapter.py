"""Адаптер для главного меню в консоли."""

from src.use_cases.main_menu import MainMenuUseCase, MenuItem


class MainMenuAdapter:
    """Адаптер главного меню для консольного интерфейса."""
    
    def __init__(self, main_menu: MainMenuUseCase):
        self.main_menu = main_menu
        self._setup_menu_items()
    
    def _setup_menu_items(self) -> None:
        """Настроить пункты меню."""
        # Новая игра
        self.main_menu.add_menu_item(MenuItem(
            title="Новая игра",
            action=self._new_game
        ))
        
        # Загрузить игру
        self.main_menu.add_menu_item(MenuItem(
            title="Загрузить игру",
            action=self._load_game
        ))
        
        
        # Настройки
        self.main_menu.add_menu_item(MenuItem(
            title="Настройки",
            action=self._settings
        ))
    
    def _new_game(self) -> None:
        """Начать новую игру."""
        print("\n🎮 Запуск новой игры...")
        print("🚧 В разработке...")
        input("Нажмите Enter для возврата в меню...")
    
    def _load_game(self) -> None:
        """Загрузить сохранённую игру."""
        print("\n📂 Загрузка игры...")
        print("🚧 В разработке...")
        input("Нажмите Enter для возврата в меню...")
    
    
    def _settings(self) -> None:
        """Открыть настройки."""
        print("\n⚙️ Настройки...")
        print("🚧 В разработке...")
        input("Нажмите Enter для возврата в меню...")
    
    def run(self) -> None:
        """Запустить главное меню."""
        self.main_menu.execute()