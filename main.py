"""Главная точка входа в D&D Text MUD.

Простая архитектура следуя принципам KISS, YAGNI и Zen Python.
Без избыточных абстракций и сложного DI.
"""

import sys

from src.console.welcome_adapter import WelcomeScreenAdapter
from src.welcome_dto import WelcomeScreenRequest
from src.welcome_use_case import ShowWelcomeScreenUseCase


class Application:
    """Основной класс приложения.

    Следует принципу KISS - просто и понятно.
    Минимум зависимостей, явная логика.
    """

    def __init__(self) -> None:
        """Инициализация приложения."""
        self.use_case = ShowWelcomeScreenUseCase()
        self.adapter = WelcomeScreenAdapter()

    def run_welcome_screen(self) -> None:
        """Запустить приветственный экран."""
        print("Запуск приветственного экрана...")

        # Создаем запрос с явными параметрами (Zen Python)
        request = WelcomeScreenRequest(
            language="ru",
            show_ascii_art=True
        )

        # Выполняем Use Case
        response = self.use_case.execute(request)

        # Отображаем через адаптер
        self.adapter.display(response)

        print("Приветственный экран завершён")

    def run(self) -> None:
        """Запустить приложение."""
        try:
            self.run_welcome_screen()
            print("Приложение успешно завершено")

        except KeyboardInterrupt:
            print("Приложение прервано пользователем")
        except Exception as error:
            print(f"Критическая ошибка приложения: {error}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    """Главная функция.

    Простая точка входа без избыточности.
    """
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
