from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Any, Callable
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box


@dataclass
class MenuItem:
    """Пункт меню."""
    number: int
    label: str
    action: Callable[[], Any]
    enabled: bool = True
    description: Optional[str] = None


class MenuBase(ABC):
    """
    Базовый класс для всех меню.

    Паттерн: Template Method
    Принципы: SRP, OCP

    Определяет общую структуру меню и позволяет подклассам
    переопределять специфичные части.
    """

    def __init__(self, title: str = "Меню") -> None:
        """
        Инициализация меню.

        Args:
            title: заголовок меню
        """
        self.title = title
        self.console = Console()
        self.items: List[MenuItem] = []
        self._running = True

    @abstractmethod
    def build_menu(self) -> None:
        """
        Построение пунктов меню.

        Должен быть реализован в подклассах.
        """
        pass

    def add_item(self, label: str, action: Callable[[], Any],
                 enabled: bool = True, description: Optional[str] = None) -> None:
        """
        Добавление пункта меню.

        Args:
            label: текст пункта
            action: функция-обработчик
            enabled: активен ли пункт
            description: описание пункта
        """
        number = len(self.items) + 1
        item = MenuItem(
            number=number,
            label=label,
            action=action,
            enabled=enabled,
            description=description
        )
        self.items.append(item)

    def render(self) -> None:
        """Отрисовка меню."""
        # Получение размера терминала
        # size = window_manager.get_terminal_size()

        # Очистка экрана
        self.console.clear()

        # Отрисовка заголовка
        self._render_title()

        # Отрисовка пунктов меню
        self._render_items()

        # Отрисовка подсказки
        self._render_hint()

    def _render_title(self) -> None:
        """Отрисовка заголовка меню."""
        title_text = Text(self.title, style="bold cyan", justify="center")
        title_panel = Panel(
            title_text,
            box=box.DOUBLE,
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(title_panel)
        self.console.print()

    def _render_items(self) -> None:
        """Отрисовка пунктов меню."""
        items_text = Text()

        for item in self.items:
            if item.enabled:
                style = "bold white"
                prefix = "►"
            else:
                style = "dim"
                prefix = " "

            # Номер и текст пункта
            line = f"{prefix} {item.number}. {item.label}"
            items_text.append(line + "\n", style=style)

            # Описание (если есть)
            if item.description and item.enabled:
                items_text.append(f"   {item.description}\n", style="dim")

        # Панель с пунктами
        items_panel = Panel(
            items_text,
            box=box.ROUNDED,
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(items_panel)

    def _render_hint(self) -> None:
        """Отрисовка подсказки для пользователя."""
        hint = Text("Введите номер пункта меню или /help для справки",
                    style="italic yellow")
        self.console.print()
        self.console.print(hint)

    def handle_input(self, user_input: str) -> Optional[Any]:
        """
        Обработка пользовательского ввода.

        Args:
            user_input: введённая строка

        Returns:
            Optional[Any]: результат выполнения действия
        """
        user_input = user_input.strip()

        # Обработка служебных команд
        if user_input.startswith('/'):
            return self._handle_command(user_input)

        # Обработка выбора пункта меню
        try:
            choice = int(user_input)
            return self._execute_choice(choice)
        except ValueError:
            self.console.print("[red]Ошибка: введите число или команду[/red]")
            return None

    def _handle_command(self, command: str) -> Optional[Any]:
        """
        Обработка служебной команды.

        Args:
            command: команда (начинается с /)

        Returns:
            Optional[Any]: результат команды
        """
        command = command.lower()

        if command in ['/help', '/справка', '/h', '/?']:
            self._show_help()
        elif command in ['/exit', '/выход', '/quit', '/q']:
            self._running = False
        else:
            self.console.print(f"[red]Неизвестная команда: {command}[/red]")

        return None

    def _show_help(self) -> None:
        """Показ справки."""
        help_text = """
[bold cyan]Доступные команды:[/bold cyan]

[yellow]Навигация по меню:[/yellow]
  1-9         - Выбор пункта меню по номеру
  /help       - Показать эту справку
  /exit       - Выход из меню

[yellow]Глобальные команды:[/yellow]
  /save       - Быстрое сохранение (в игре)
  /load       - Быстрая загрузка (в игре)
  /settings   - Открыть настройки

[dim]Для выполнения действия введите номер пункта или команду[/dim]
        """
        panel = Panel(
            help_text,
            title="Справка",
            box=box.ROUNDED,
            border_style="yellow"
        )
        self.console.print()
        self.console.print(panel)
        input("\nНажмите Enter для продолжения...")

    def _execute_choice(self, choice: int) -> Optional[Any]:
        """
        Выполнение выбранного пункта меню.

        Args:
            choice: номер выбранного пункта

        Returns:
            Optional[Any]: результат выполнения действия
        """
        # Поиск пункта по номеру
        item = next((i for i in self.items if i.number == choice), None)

        if item is None:
            self.console.print(f"[red]Ошибка: пункт {choice} не существует[/red]")
            return None

        if not item.enabled:
            self.console.print(f"[red]Пункт '{item.label}' недоступен[/red]")
            return None

        # Выполнение действия
        try:
            return item.action()
        except Exception as e:
            self.console.print(f"[red]Ошибка при выполнении: {e}[/red]")
            return None

    def run(self) -> None:
        """
        Запуск меню (главный цикл).

        Template Method: определяет общий алгоритм работы меню.
        """
        self.build_menu()

        while self._running:
            self.render()

            try:
                user_input = input("\n> ").strip()
                if user_input:
                    self.handle_input(user_input)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Используйте /exit для выхода[/yellow]")
                continue
            except EOFError:
                break

    def stop(self) -> None:
        """Остановка меню."""
        self._running = False