"""Главная точка входа в D&D Text MUD.

Следует Clean Architecture - точка входа с Dependency Injection.
Оркестрация всех компонентов через DI контейнер.
"""

import sys

from src.dependency_injection import ApplicationServices, get_container
from src.dto.welcome_dto import WelcomeControllerRequest
from src.frameworks.console.welcome_adapter import ConsoleWelcomeScreenAdapter


class Application:
    """Основной класс приложения.
    
    Следует Clean Architecture - оркестрация Use Cases через
    Dependency Injection контейнер.
    """

    def __init__(self) -> None:
        """Инициализация приложения."""
        self._services = ApplicationServices()
        self._welcome_controller = self._services.welcome_controller
        self._welcome_adapter = ConsoleWelcomeScreenAdapter()

    def run_welcome_screen(self) -> None:
        """Запустить приветственный экран."""
        print("Запуск приветственного экрана...")

        # Создание запроса через контроллер
        request = WelcomeControllerRequest(
            language="ru",
            show_ascii_art=True
        )

        # Выполнение через контроллер
        response = self._welcome_controller.show_welcome(request)

        # Отображение через адаптер
        if response.success and response.data:
            self._welcome_adapter.display(response.data)
        else:
            print(f"Ошибка: {response.message}")

        print("Приветственный экран завершён")

    def run(self) -> None:
        """Запустить приложение."""
        try:
            self.run_welcome_screen()
            print("\n🎉 Приложение успешно завершено")

        except KeyboardInterrupt:
            print("\nПриложение прервано пользователем")
        except Exception as error:
            print(f"Критическая ошибка приложения: {error}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    """Главная функция.
    
    Точка входа с proper dependency injection.
    """
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
