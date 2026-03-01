"""Точка входа в D&D Text MUD."""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.exceptions import DnDMudError
from core.game import Game
from ui.console import Console


def main() -> None:
    """Главная функция приложения."""
    try:
        console = Console()
        game = Game(console)
        game.run()
    except DnDMudError as e:
        print(f"Ошибка игры: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nДо свидания!")
        sys.exit(0)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
