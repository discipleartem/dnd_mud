"""
Game Engine - главный игровой движок
"""
import logging
from ui.welcome_screen import WelcomeScreen
from ui.settings_menu import SettingsMenu
from ui.window_manager import WindowManager
from game.core.data.data_loader import DataLoader
from game.core.character.character_creator import CharacterCreator
from utils.mods_loader import ModsLoader
from utils.watchdog_handler import WatchdogManager


class GameEngine:
    """Главный игровой движок"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)

        # Инициализация компонентов
        self.window_manager = WindowManager(config_manager)
        self.data_loader = DataLoader(config_manager)
        self.mods_loader = ModsLoader(config_manager)
        self.watchdog = WatchdogManager(config_manager)

        # UI компоненты
        self.welcome_screen = WelcomeScreen(config_manager, self.window_manager)
        self.settings_menu = SettingsMenu(config_manager, self.window_manager)
        self.character_creator = CharacterCreator(
            config_manager,
            self.window_manager,
            self.data_loader
        )

        # Игровое состояние
        self.running = False
        self.current_character = None

        # Инициализация
        self._initialize()

    def _initialize(self):
        """Инициализация игрового движка"""
        self.logger.info("Инициализация игрового движка")

        # Инициализация загрузчиков данных
        self.data_loader.initialize()
        self.mods_loader.initialize()

        # Настройка watchdog callbacks
        self.watchdog.initialize()
        self.watchdog.add_callback('config', self._on_config_changed)
        self.watchdog.add_callback('data', self._on_data_changed)
        self.watchdog.add_callback('mods', self._on_mods_changed)

        # Запуск мониторинга
        self.watchdog.start_watching()

        self.logger.info("Игровой движок инициализирован")

    def run(self):
        """Главный цикл игры"""
        self.running = True
        self.logger.info("Запуск игрового цикла")

        try:
            while self.running:
                # Показываем welcome screen
                choice = self.welcome_screen.show()

                if choice == 'exit':
                    self._exit_game()
                    break
                elif choice == 'new_game':
                    self._start_new_game()
                elif choice == 'continue':
                    self._continue_game()
                elif choice == 'settings':
                    self._show_settings()

        except KeyboardInterrupt:
            self.logger.info("Игра прервана пользователем")
            self._exit_game()
        except Exception as e:
            self.logger.error(f"Критическая ошибка в игровом цикле: {e}", exc_info=True)
            raise
        finally:
            self._cleanup()

    def _start_new_game(self):
        """Начать новую игру"""
        self.logger.info("Начало новой игры")

        # Создание персонажа
        character = self.character_creator.create_character()

        if character:
            self.current_character = character
            self.logger.info(f"Персонаж создан: {character['name']}")

            # Здесь будет переход к основной игре
            self._start_adventure()
        else:
            self.logger.info("Создание персонажа отменено")

    def _continue_game(self):
        """Продолжить сохраненную игру"""
        self.logger.info("Продолжение сохраненной игры")
        # TODO: Реализовать загрузку сохранения
        self.welcome_screen.show_loading("Загрузка сохранения...")
        import time
        time.sleep(2)

    def _show_settings(self):
        """Показать меню настроек"""
        self.logger.info("Открытие меню настроек")
        settings_changed = self.settings_menu.show()

        if settings_changed:
            self.logger.info("Настройки изменены, применение изменений")
            # Перезагрузка данных если нужно
            if self.config_manager.get('mods.enabled'):
                self.mods_loader.reload_mods()

    def _start_adventure(self):
        """Начало приключения (основная игра)"""
        self.logger.info(f"Начало приключения для {self.current_character['name']}")

        # TODO: Реализовать основной игровой цикл
        from rich.console import Console
        console = Console()

        console.print("\n[bold green]Приключение начинается![/bold green]\n")
        console.print(f"Добро пожаловать, {self.current_character['name']}!")
        console.print("\n[dim]Основная игровая механика будет реализована позже...[/dim]\n")

        input("Нажмите Enter для возврата в главное меню...")

    def _exit_game(self):
        """Выход из игры"""
        self.logger.info("Выход из игры")
        self.running = False

        from rich.console import Console
        console = Console()
        console.print("\n[bold yellow]Спасибо за игру![/bold yellow]")
        console.print("[cyan]До новых встреч в мире Dungeons & Dragons![/cyan]\n")

    def _cleanup(self):
        """Очистка ресурсов"""
        self.logger.info("Очистка ресурсов")

        # Остановка watchdog
        if self.watchdog:
            self.watchdog.stop_watching()

        # Остановка мониторинга окна
        if self.window_manager:
            self.window_manager.stop_monitoring()

        self.logger.info("Очистка завершена")

    # Watchdog callbacks
    def _on_config_changed(self, file_path: str, event_type: str):
        """Callback при изменении конфига"""
        self.logger.info(f"Конфиг изменен: {file_path} ({event_type})")
        self.config_manager.reload_config()

    def _on_data_changed(self, file_path: str, event_type: str):
        """Callback при изменении игровых данных"""
        self.logger.info(f"Игровые данные изменены: {file_path} ({event_type})")
        self.data_loader.reload_all()

    def _on_mods_changed(self, file_path: str, event_type: str):
        """Callback при изменении модов"""
        self.logger.info(f"Моды изменены: {file_path} ({event_type})")
        if self.config_manager.get('mods.enabled'):
            self.mods_loader.reload_mods()