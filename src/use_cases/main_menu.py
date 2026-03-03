"""Use Case для главного меню игры."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class MenuItem:
    """Элемент меню."""

    title: str
    action: Callable[[], None]


class MainMenuUseCase:
    """Сценарий главного меню."""

    def __init__(self) -> None:
        self.menu_items: list[MenuItem] = []

    def add_menu_item(self, item: MenuItem) -> None:
        """Добавить пункт меню."""
        self.menu_items.append(item)

    def display_menu(self) -> None:
        """Отобразить меню."""
        print("\n" + "=" * 50)
        print("D&D MUD - Главное меню")
        print("=" * 50)

        for i, item in enumerate(self.menu_items, 1):
            print(f"{i}. {item.title}")

        print("=" * 50)
        print("5. Выход")

    def get_user_choice(self) -> MenuItem | None:
        """Получить выбор пользователя."""
        while True:
            try:
                choice = input("\nВаш выбор: ").strip()

                # Проверка выхода
                if choice in ["5", "q", "quit", "exit"]:
                    return None

                # Поиск по номеру
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(self.menu_items):
                        return self.menu_items[index]
                    else:
                        print("Неверный номер. Попробуйте снова.")
                        continue

                print("Введите номер пункта меню (1-5).")

            except KeyboardInterrupt:
                print("\n\nДо свидания!")
                return None
            except Exception as e:
                print(f"Ошибка: {e}")
                continue

    def execute(self) -> None:
        """Выполнить главное меню."""
        while True:
            self.display_menu()
            choice = self.get_user_choice()

            if choice is None:
                break

            try:
                choice.action()
            except Exception as e:
                print(f"Ошибка выполнения: {e}")
                input("Нажмите Enter для продолжения...")
