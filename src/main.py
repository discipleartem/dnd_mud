"""
Главный файл запуска игры DnD MUD Game.
Точка входа в приложение.
"""

import sys
from pathlib import Path

# Добавление корневой директории в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

from src.core.window_manager import window_manager
from src.core.state_manager import state_manager, GameState
from src.ui.main_menu import MainMenu


def check_environment() -> bool:
    """
    Проверка окружения перед запуском игры.

    Returns:
        bool: True если всё готово к запуску
    """
    console = Console()

    # Проверка размера терминала
    is_valid, message = window_manager.check_minimum_size()
    if not is_valid:
        console.print(Panel(
            message,
            title="Ошибка размера терминала",
            border_style="red"
        ))
        return False

    # Проверка необходимых директорий
    required_dirs = [
        "data/yaml",
        "data/saves",
        "data/mods"
    ]

    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    return True


def show_welcome_message() -> None:
    """Показ приветственного сообщения."""
    console = Console()

    welcome = """
[bold cyan]Добро пожаловать в DnD MUD Game![/bold cyan]

Текстовая приключенческая игра на основе
Dungeons & Dragons 5 Edition (2023)

[dim]Версия: 0.1.0 (Alpha)[/dim]
    """

    console.print(Panel(
        welcome,
        border_style="bright_blue",
        padding=(1, 2)
    ))
    console.print()


def main() -> int:
    console = Console()

    try:
        # Проверка окружения
        if not check_environment():
            return 1

        # Приветственное сообщение
        show_welcome_message()

        # Запуск главного меню
        menu = MainMenu()
        menu.run()

        # Проверка состояния выхода
        final_state = state_manager.get_state()
        if final_state == GameState.EXIT:
            console.print("\n[green]Игра завершена корректно[/green]")
            return 0

        return 0

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Игра прервана пользователем[/yellow]")
        return 130  # Стандартный код для SIGINT

    except Exception as e:
        console.print(f"\n[red bold]Критическая ошибка: {e}[/red bold]")
        console.print("[dim]Пожалуйста, сообщите об этой ошибке разработчикам[/dim]")

        # В debug режиме показываем полный traceback
        if "--debug" in sys.argv:
            import traceback
            console.print("\n[red]Traceback:[/red]")
            traceback.print_exc()

        return 1


if __name__ == "__main__":
    sys.exit(main())