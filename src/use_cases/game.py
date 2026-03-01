"""Основной Use Case игры.

Следует принципам:
- KISS: Максимально простой класс
- SRP: Одна ответственность - управление игрой
- YAGNI: Только необходимая функциональность
"""


from entities.character import Character
from entities.game_session import GameSession
from interfaces.user_interface import UserInterface


class GameUseCase:
    """Основной Use Case для управления игрой.

    Объединяет логику меню и обработки выбора
    для максимального упрощения (KISS).
    """

    def __init__(self, ui: UserInterface) -> None:
        """Инициализация Use Case."""
        self.ui = ui
        self._session: GameSession | None = None

    def show_and_handle_menu(self) -> bool:
        """Показать меню и обработать выбор (KISS - один метод)."""
        self.ui.clear()
        self.ui.print_title("D&D Text MUD")
        self.ui.print_separator()

        # Простое меню без лишней сложности
        menu_items = {
            1: "Новая игра",
            2: "Загрузить игру",
            3: "Настройки",
            4: "Моды",
            5: "Выход"
        }

        for number, text in menu_items.items():
            self.ui.print_menu_item(number, text)

        self.ui.print_separator()
        choice = self.ui.get_int_input("Ваш выбор: ", 1, 5)

        # Прямая обработка без лишней сложности
        if choice == 5:
            self.ui.print_success("Спасибо за игру!")
            return False
        elif choice == 1:
            self._handle_new_game()
        elif choice in (2, 3, 4):
            self._show_message("Функция пока недоступна.")
        else:
            self.ui.print_error("Неверный выбор. Попробуйте снова.")

        return True

    def _handle_new_game(self) -> None:
        """Обработать новую игру."""
        try:
            # Создаём персонажа с простой валидацией
            name = self.ui.get_input("Введите имя персонажа: ").strip()
            character = Character(name=name)

            # Создаём сессию
            self._session = GameSession(player=character, session_name=f"Приключения {name}")

            self.ui.print_success(f"Персонаж {name} создан!")
            self.ui.print_info(f"{character}")
            self.ui.print_info(f"Статус: {character.get_status()}")

        except ValueError as e:
            self.ui.print_error(f"Ошибка создания персонажа: {e}")

    def _show_message(self, message: str) -> None:
        """Показать сообщение и ждать ввода."""
        self.ui.print_info(message)
        self.ui.get_input("Нажмите Enter для продолжения...")

    def get_current_session(self) -> GameSession | None:
        """Получить текущую сессию."""
        return self._session

    def has_active_session(self) -> bool:
        """Проверить, есть ли активная сессия."""
        return self._session is not None
