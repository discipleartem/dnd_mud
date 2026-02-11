from __future__ import annotations
from pathlib import Path
from rich.console import Console

from core.game import Game
from core.validator import ProjectStructureValidator


def main() -> bool:
    """Точка входа приложения."""
    try:
        ProjectStructureValidator.validate_data_directory(Path(__file__).parent.parent / "data")
        game = Game()
        game.run()
        return True
        
    except Exception as e:
        console = Console()
        console.print(f"[red]Ошибка запуска: {e}[/red]")
        return False


if __name__ == "__main__":
    main()

