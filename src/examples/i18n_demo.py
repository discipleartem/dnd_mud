"""Демонстрация работы системы i18n.

Следует Zen Python:
- Простое лучше сложного
- Явное лучше неявного
- Читаемость важна
"""

from pathlib import Path

from entities.character import Character
from entities.i18n import I18nConfig
from ui.console import Console
from use_cases.i18n_manager import I18nManagerImpl


def main() -> None:
    """Демонстрация работы локализации."""
    print("=== Демонстрация системы i18n ===\n")

    # Инициализация системы i18n
    data_dir = Path(__file__).parent.parent.parent / "data"
    manager = I18nManagerImpl(data_dir)

    config = I18nConfig(
        default_language="ru",
        fallback_language="en",
        cache_enabled=True,
        auto_detect_language=False,  # Отключаем для демо
    )

    manager.initialize(config)
    manager.load_all_translations()

    translator = manager.get_translator()

    # Демонстрация интерфейса с локализацией
    console = Console(translator)

    # Показываем приветствие на разных языках
    print("1. Приветствие на разных языках:")

    # Русский
    translator.set_language("ru")
    console.print_title(console.t("ui.main_menu.title"))
    console.print_info(console.t("welcome"))

    # Английский
    translator.set_language("en")
    console.print_title(console.t("ui.main_menu.title"))
    console.print_info(console.t("welcome"))

    print("\n" + "="*50 + "\n")

    # Демонстрация персонажа с локализацией
    print("2. Локализованный персонаж:")

    hero = Character("Арагорн", level=5, hit_points=45, max_hit_points=55)
    hero.set_translator(translator)

    translator.set_language("ru")
    print(f"Русский: {hero}")
    print(f"Статус: {hero.get_status()}")

    translator.set_language("en")
    print(f"English: {hero}")
    print(f"Status: {hero.get_status()}")

    print("\n" + "="*50 + "\n")

    # Демонстрация меню с локализацией
    print("3. Локализованное меню:")

    translator.set_language("ru")
    console.print_title(console.t("ui.main_menu.title"))
    console.print_menu_item(1, console.t("ui.main_menu.new_game"))
    console.print_menu_item(2, console.t("ui.main_menu.load_game"))
    console.print_menu_item(3, console.t("ui.main_menu.settings"))
    console.print_menu_item(4, console.t("ui.main_menu.exit"))

    print("\n" + "-"*30 + "\n")

    translator.set_language("en")
    console.print_title(console.t("ui.main_menu.title"))
    console.print_menu_item(1, console.t("ui.main_menu.new_game"))
    console.print_menu_item(2, console.t("ui.main_menu.load_game"))
    console.print_menu_item(3, console.t("ui.main_menu.settings"))
    console.print_menu_item(4, console.t("ui.main_menu.exit"))

    print("\n" + "="*50 + "\n")

    # Демонстрация форматирования
    print("4. Форматирование с параметрами:")

    translator.set_language("ru")
    character_created = console.t("ui.character_creation.success", name="Гэндальф")
    console.print_success(character_created)

    translator.set_language("en")
    character_created = console.t("ui.character_creation.success", name="Gandalf")
    console.print_success(character_created)

    print("\n" + "="*50 + "\n")

    # Демонстрация ошибок
    print("5. Локализованные ошибки:")

    translator.set_language("ru")
    console.print_error(console.t("errors.number_expected"))
    console.print_error(console.t("errors.range_error", min=1, max=10))

    translator.set_language("en")
    console.print_error(console.t("errors.number_expected"))
    console.print_error(console.t("errors.range_error", min=1, max=10))

    print("\n" + "="*50 + "\n")

    # Статистика системы
    print("6. Статистика системы i18n:")
    stats = manager.get_statistics()

    translator.set_language("ru")
    console.print_info(f"Текущий язык: {stats['current_language']}")
    console.print_info(f"Размер кэша: {stats['size']}")
    console.print_info(f"Доступных языков: {stats['available_languages']}")

    print("\nДемонстрация завершена!")


if __name__ == "__main__":
    main()
