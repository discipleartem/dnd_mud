"""D&D MUD - Создание персонажей.

Простая программа для создания персонажей Dungeons & Dragons.
Следует принципам KISS и YAGNI.
"""

import sys
from typing import NoReturn

from i18n import t
from src.ui.main_menu.main import show_main_menu


def _print_welcome_banner() -> None:
    """Вывести приветственный баннер."""
    title = t('main.welcome.title')
    version = t('main.welcome.version')

    banner_lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║                                                              ║",
        "║                 DUNGEONS & DRAGONS MUD                       ║",
        "║                                                              ║",
        "║    🎲──────────────────────────────────────────────────🎲    ║",
        "║                                                              ║",
        f"║                  📜 {title:<41}║",
        f"║                  🔢 {version:<41}║",
        "║                                                              ║",
        "║         🗡️ Создайте своего героя и начните приключение! 🏰    ║",
        "║                                                              ║",
        "╚══════════════════════════════════════════════════════════════╝",
    ]

    print("\n".join(banner_lines))


def welcome_screen() -> None:
    """Приветственный экран."""
    _print_welcome_banner()
    input(t("main.welcome.press_enter"))


def main() -> int:
    """Основная функция.

    Returns:
        Код завершения программы (0 при успехе).
    """
    try:
        welcome_screen()
        show_main_menu()
    except KeyboardInterrupt:
        print(
            f"\n{t('main.welcome.interrupted')}"
        )
    except Exception as e:
        print(
            f"\n{t('main.welcome.error', error=str(e))}"
        )
        return 1

    return 0


def _run_application() -> NoReturn:
    """Запустить приложение с корректным выходом."""
    sys.exit(main())


if __name__ == "__main__":
    _run_application()
