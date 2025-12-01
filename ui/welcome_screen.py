"""
Welcome Screen - приветственный экран игры
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from pathlib import Path
import logging


class WelcomeScreen:
    """Приветственный экран игры"""

    def __init__(self, config_manager, window_manager):
        self.config_manager = config_manager
        self.window_manager = window_manager
        self.console = Console()
        self.logger = logging.getLogger(__name__)

        # Проверяем наличие сохранений
        self.saves_path = Path(config_manager.get('paths.saves', 'game/saves'))
        self.has_saves = self._check_saves()

    def _check_saves(self) -> bool:
        """Проверка наличия сохраненных игр"""
        if not self.saves_path.exists():
            return False

        save_files = list(self.saves_path.glob('*.json'))
        return len(save_files) > 0

    def show(self) -> str:
        """
        Отображение приветственного экрана

        Returns:
            Выбор пользователя
        """
        while True:
            self.window_manager.clear_screen()
            self._render_screen()

            choice = self._get_user_input()

            if choice == 'continue' and not self.has_saves:
                self.console.print("\n[red]Нет сохраненных игр![/red]")
                input("Нажмите Enter для продолжения...")
                continue

            return choice

    def _render_screen(self):
        """Рендеринг экрана"""
        # Заголовок
        title = self._create_title()
        self.console.print(title)
        self.console.print()

        # Меню
        menu = self._create_menu()
        self.console.print(menu)

    def _create_title(self) -> Panel:
        """Создание заголовка"""
        use_colors = self.config_manager.get('display.colored_text', True)

        title_text = Text()
        title_text.append("╔═══════════════════════════════════════════════════╗\n",
                          style="bold cyan" if use_colors else "bold")
        title_text.append("║                                                   ║\n",
                          style="bold cyan" if use_colors else "bold")
        title_text.append("║        DUNGEONS & DRAGONS 5E (2023)              ║\n",
                          style="bold yellow" if use_colors else "bold")
        title_text.append("║              MUD Text Adventure                   ║\n",
                          style="bold yellow" if use_colors else "bold")
        title_text.append("║                                                   ║\n",
                          style="bold cyan" if use_colors else "bold")
        title_text.append("╚═══════════════════════════════════════════════════╝",
                          style="bold cyan" if use_colors else "bold")

        return Align.center(title_text)

    def _create_menu(self) -> Panel:
        """Создание меню"""
        use_colors = self.config_manager.get('display.colored_text', True)

        menu_items = []

        # 1. Продолжить (если есть сохранения)
        if self.has_saves:
            menu_items.append(("1", "Продолжить", "green" if use_colors else None))
        else:
            menu_items.append(("1", "Продолжить (нет сохранений)", "dim" if use_colors else None))

        # 2. Новая игра
        menu_items.append(("2", "Новая игра", "bright_cyan" if use_colors else None))

        # 3. Настройки
        menu_items.append(("3", "Настройки", "yellow" if use_colors else None))

        # 4. Выход
        menu_items.append(("4", "Выход", "red" if use_colors else None))

        # Формируем текст меню
        menu_text = Text()
        menu_text.append("═" * 50 + "\n", style="cyan" if use_colors else None)
        menu_text.append("  ГЛАВНОЕ МЕНЮ\n\n", style="bold white" if use_colors else "bold")

        for number, item, color in menu_items:
            menu_text.append(f"  [{number}] ", style="bold white" if use_colors else "bold")
            menu_text.append(f"{item}\n", style=color)

        menu_text.append("\n" + "═" * 50, style="cyan" if use_colors else None)

        return Panel(
            Align.center(menu_text),
            border_style="cyan" if use_colors else "white",
            padding=(1, 2)
        )

    def _get_user_input(self) -> str:
        """Получение ввода пользователя"""
        self.console.print()
        choice = input("Выберите пункт меню (1-4): ").strip()

        if choice == '1':
            return 'continue' if self.has_saves else None
        elif choice == '2':
            return 'new_game'
        elif choice == '3':
            return 'settings'
        elif choice == '4':
            return 'exit'
        else:
            self.console.print("[red]Неверный выбор! Попробуйте снова.[/red]")
            input("Нажмите Enter...")
            return None

    def show_loading(self, message: str = "Загрузка..."):
        """Показать сообщение загрузки"""
        self.window_manager.clear_screen()

        loading_text = Text()
        loading_text.append("╔════════════════════════════════════╗\n", style="bold cyan")
        loading_text.append("║                                    ║\n", style="bold cyan")
        loading_text.append(f"║  {message:^32}  ║\n", style="bold yellow")
        loading_text.append("║                                    ║\n", style="bold cyan")
        loading_text.append("╚════════════════════════════════════╝", style="bold cyan")

        self.console.print(Align.center(loading_text))