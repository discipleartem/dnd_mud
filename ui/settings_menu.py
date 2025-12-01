"""
Settings Menu - меню настроек игры
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
import logging


class SettingsMenu:
    """Меню настроек игры"""

    def __init__(self, config_manager, window_manager):
        self.config_manager = config_manager
        self.window_manager = window_manager
        self.console = Console()
        self.logger = logging.getLogger(__name__)

    def show(self) -> bool:
        """
        Показать меню настроек

        Returns:
            True если настройки изменились, иначе False
        """
        settings_changed = False

        while True:
            self.window_manager.clear_screen()
            self._render_settings()

            choice = self._get_user_input()

            if choice == 'back':
                break
            elif choice == 'resolution':
                self._show_resolution_info()
            elif choice == 'colored':
                settings_changed = True
                self._toggle_colored_text()
            elif choice == 'language':
                settings_changed = True
                self._change_language()
            elif choice == 'difficulty':
                settings_changed = True
                self._change_difficulty()
            elif choice == 'autosave':
                settings_changed = True
                self._toggle_autosave()
            elif choice == 'autosave_interval':
                settings_changed = True
                self._change_autosave_interval()
            elif choice == 'mods':
                settings_changed = True
                self._toggle_mods()

        if settings_changed:
            self.config_manager.save_config()
            self.logger.info("Настройки сохранены")

        return settings_changed

    def _render_settings(self):
        """Рендеринг меню настроек"""
        use_colors = self.config_manager.get('display.colored_text', True)

        # Заголовок
        title = Text("⚙️  НАСТРОЙКИ  ⚙️", style="bold yellow" if use_colors else "bold")
        self.console.print(Panel(title, border_style="yellow" if use_colors else "white"))
        self.console.print()

        # Таблица настроек
        table = Table(show_header=True, header_style="bold cyan" if use_colors else "bold")
        table.add_column("№", style="dim", width=4)
        table.add_column("Настройка", style="bold")
        table.add_column("Значение", style="green" if use_colors else None)

        # Разрешение окна
        width, height = self.window_manager.get_size()
        table.add_row("1", "Разрешение окна", f"{width}x{height}")

        # Цветной текст
        colored = self.config_manager.get('display.colored_text', True)
        table.add_row("2", "Цветной текст", "Вкл" if colored else "Выкл")

        # Язык
        language = self.config_manager.get('game.language', 'ru')
        table.add_row("3", "Язык", language.upper())

        # Сложность
        difficulty = self.config_manager.get('game.difficulty', 'easy')
        diff_text = "Легко" if difficulty == 'easy' else "Хардкор"
        table.add_row("4", "Сложность", diff_text)

        # Автосохранение
        autosave = self.config_manager.get('game.autosave', True)
        table.add_row("5", "Автосохранение", "Вкл" if autosave else "Выкл")

        # Интервал автосохранения
        interval = self.config_manager.get('game.autosave_interval', 300)
        table.add_row("6", "Интервал автосохранения", f"{interval} сек")

        # Модификации
        mods = self.config_manager.get('mods.enabled', True)
        table.add_row("7", "Модификации", "Вкл" if mods else "Выкл")

        self.console.print(table)
        self.console.print()

        # Кнопка назад
        back_text = Text("\n[0] Назад", style="bold red" if use_colors else "bold")
        self.console.print(back_text)

    def _get_user_input(self) -> str:
        """Получение ввода пользователя"""
        choice = input("\nВыберите настройку (0-7): ").strip()

        mapping = {
            '0': 'back',
            '1': 'resolution',
            '2': 'colored',
            '3': 'language',
            '4': 'difficulty',
            '5': 'autosave',
            '6': 'autosave_interval',
            '7': 'mods'
        }

        return mapping.get(choice, None)

    def _show_resolution_info(self):
        """Показать информацию о разрешении"""
        width, height = self.window_manager.get_size()
        info = f"\nТекущее разрешение: {width}x{height}"
        info += "\nРазмер окна обновляется автоматически."
        info += "\nИзмените размер окна терминала для применения изменений."

        self.console.print(info, style="cyan")
        input("\nНажмите Enter...")

    def _toggle_colored_text(self):
        """Переключение цветного текста"""
        current = self.config_manager.get('display.colored_text', True)
        self.config_manager.set('display.colored_text', not current)
        status = "включен" if not current else "выключен"
        self.console.print(f"\n[green]Цветной текст {status}[/green]")
        input("Нажмите Enter...")

    def _change_language(self):
        """Смена языка"""
        self.console.print("\nДоступные языки:")
        self.console.print("1. Русский (ru)")
        self.console.print("2. English (en)")

        choice = input("\nВыберите язык (1-2): ").strip()

        if choice == '1':
            self.config_manager.set('game.language', 'ru')
            self.console.print("[green]Язык изменен на Русский[/green]")
        elif choice == '2':
            self.config_manager.set('game.language', 'en')
            self.console.print("[green]Language changed to English[/green]")

        input("Нажмите Enter...")

    def _change_difficulty(self):
        """Смена сложности"""
        self.console.print("\nСложность:")
        self.console.print("1. Легко (easy)")
        self.console.print("2. Хардкор (hard_core)")

        choice = input("\nВыберите сложность (1-2): ").strip()

        if choice == '1':
            self.config_manager.set('game.difficulty', 'easy')
            self.console.print("[green]Сложность: Легко[/green]")
        elif choice == '2':
            self.config_manager.set('game.difficulty', 'hard_core')
            self.console.print("[green]Сложность: Хардкор[/green]")

        input("Нажмите Enter...")

    def _toggle_autosave(self):
        """Переключение автосохранения"""
        current = self.config_manager.get('game.autosave', True)
        self.config_manager.set('game.autosave', not current)
        status = "включено" if not current else "выключено"
        self.console.print(f"\n[green]Автосохранение {status}[/green]")
        input("Нажмите Enter...")

    def _change_autosave_interval(self):
        """Изменение интервала автосохранения"""
        self.console.print("\nИнтервал автосохранения (в секундах):")
        self.console.print("Текущий:", self.config_manager.get('game.autosave_interval', 300))

        try:
            interval = int(input("Введите новый интервал (60-3600): ").strip())
            if 60 <= interval <= 3600:
                self.config_manager.set('game.autosave_interval', interval)
                self.console.print(f"[green]Интервал изменен на {interval} сек[/green]")
            else:
                self.console.print("[red]Значение должно быть от 60 до 3600[/red]")
        except ValueError:
            self.console.print("[red]Неверный формат числа[/red]")

        input("Нажмите Enter...")

    def _toggle_mods(self):
        """Переключение модификаций"""
        current = self.config_manager.get('mods.enabled', True)
        self.config_manager.set('mods.enabled', not current)
        status = "включены" if not current else "выключены"
        self.console.print(f"\n[green]Модификации {status}[/green]")

        if not current:
            mods_path = self.config_manager.get('paths.mods', 'game/data/mods')
            self.console.print(f"Папка модов: {mods_path}")

        input("Нажмите Enter...")