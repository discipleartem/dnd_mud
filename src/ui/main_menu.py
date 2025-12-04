from src.core.window_manager import window_manager
from src.core.state_manager import state_manager, GameState

from src.ui.menu_base import MenuBase, Text
from rich.align import Align

class MainMenu(MenuBase):
    """
    Главное меню игры.

    Пункты:
    - Продолжить (если есть сохранение)
    - Новая игра
    - Загрузить
    - Настройки
    - Выход
    """

    def __init__(self) -> None:
        """Инициализация главного меню."""
        super().__init__(title="Главное меню")

    def build_menu(self) -> None:
        """Построение главного меню."""
        self.items.clear()

        # Проверка наличия сохранения для продолжения
        has_continue = state_manager.can_continue()

        # Пункт "Продолжить" (только если есть сохранение)
        if has_continue:
            self.add_item(
                label="Продолжить",
                action=self._continue_game,
                enabled=True,
                description="Продолжить последнюю игру"
            )

        # Новая игра
        self.add_item(
            label="Новая игра",
            action=self._new_game,
            enabled=True,
            description="Начать новое приключение"
        )

        # Загрузить
        self.add_item(
            label="Загрузить",
            action=self._load_game,
            enabled=True,
            description="Загрузить сохранённую игру"
        )

        # Настройки
        self.add_item(
            label="Настройки",
            action=self._settings,
            enabled=True,
            description="Настройки игры"
        )

        # Выход
        self.add_item(
            label="Выход",
            action=self._exit_game,
            enabled=True,
            description="Выход из игры"
        )

    def _render_title(self) -> None:
        """Красивая отрисовка заголовка игры."""
        # ASCII-арт заголовок
        title_art = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║    ██████╗ ███╗   ██╗██████╗     ███████╗███████╗         ║
║    ██╔══██╗████╗  ██║██╔══██╗    ██╔════╝██╔════╝         ║
║    ██║  ██║██╔██╗ ██║██║  ██║    ███████╗█████╗           ║
║    ██║  ██║██║╚██╗██║██║  ██║    ╚════██║██╔══╝           ║
║    ██████╔╝██║ ╚████║██████╔╝    ███████║███████╗         ║
║    ╚═════╝ ╚═╝  ╚═══╝╚═════╝     ╚══════╝╚══════╝         ║
║                                                           ║
║           Dungeons & Dragons 5 Edition (2023)             ║
╚═══════════════════════════════════════════════════════════╝
        """

        # Отрисовка через Rich с градиентом
        title_text = Text(title_art)
        title_text.stylize("bold bright_cyan")

        self.console.print(Align.center(title_text))
        self.console.print()

    def _continue_game(self) -> None:
        """Продолжить последнюю игру."""
        self.console.print("\n[green]Загрузка последней игры...[/green]")

        # Здесь будет загрузка состояния
        # data = state_manager.load_continue_state()
        # if data:
        #     state_manager.set_state(GameState.ADVENTURE, data)
        #     self.stop()
        # else:
        #     self.console.print("[red]Ошибка загрузки игры[/red]")

        input("\n[dim]Нажмите Enter...[/dim]")

    def _new_game(self) -> None:
        """Начать новую игру."""
        self.console.print("\n[green]Создание нового персонажа...[/green]")

        # Переход к созданию персонажа
        # state_manager.set_state(GameState.CHARACTER_CREATION)
        # self.stop()

        input("\n[dim]Нажмите Enter...[/dim]")

    def _load_game(self) -> None:
        """Загрузить сохранённую игру."""
        self.console.print("\n[cyan]Список сохранений:[/cyan]")
        self.console.print("[dim]Функция загрузки будет реализована позже[/dim]")

        # Здесь будет меню выбора сохранения
        # state_manager.set_state(GameState.LOAD_GAME)
        # self.stop()

        input("\n[dim]Нажмите Enter...[/dim]")

    def _settings(self) -> None:
        """Открыть настройки."""
        self.console.print("\n[cyan]Настройки игры:[/cyan]")
        self.console.print("[dim]Меню настроек будет реализовано позже[/dim]")

        # Здесь будет меню настроек
        # state_manager.set_state(GameState.SETTINGS)

        input("\n[dim]Нажмите Enter...[/dim]")

    def _exit_game(self) -> None:
        """Выход из игры."""
        self.console.print("\n[yellow]Спасибо за игру![/yellow]")
        self.console.print("[dim]До новых встреч в мире приключений![/dim]\n")

        # state_manager.set_state(GameState.EXIT)
        self.stop()


# Пример использования
if __name__ == "__main__":
    menu = MainMenu()
    menu.run()