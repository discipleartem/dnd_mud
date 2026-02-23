"""
D&D MUD - Создание персонажей.

Простая программа для создания персонажей Dungeons & Dragons.
Следует принципам KISS и YAGNI.
"""

import sys
from src.ui.main_menu.main import show_main_menu
from i18n import t


def welcome_screen() -> None:
    """Приветственный экран."""
    welcome = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗      ║
║    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║      ║
║       ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║      ║
║       ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║      ║
║       ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████  ║
║       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝ ╚═══╝╚═╝  ╚═╝╚══════╝  ║
║                                                                      ║
║                          {t('main.welcome.title')}                                ║
║                                                                      ║
║                          {t('main.welcome.version')}                                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝    
"""
    
    print(welcome)
    input(t('main.welcome.press_enter'))


def main() -> int:
    """Основная функция."""
    try:
        welcome_screen()
        show_main_menu()
    except KeyboardInterrupt:
        print(t('main.welcome.interrupted'))
    
    return 0


if __name__ == "__main__":
    main()