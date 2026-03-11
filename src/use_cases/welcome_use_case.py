"""Сценарий приветственного экрана.

Следует Clean Architecture - зависит только от интерфейсов и сущностей.
"""

from src.interfaces.welcome_factory import WelcomeScreenFactory
from src.welcome_dto import WelcomeScreenRequest, WelcomeScreenResponse


class ShowWelcomeScreenUseCase:
    """Сценарий отображения приветственного экрана.

    Следует Clean Architecture - зависит только от абстракций и сущностей,
    не зависит от конкретных реализаций инфраструктуры.
    """

    def __init__(self, screen_factory: WelcomeScreenFactory) -> None:
        """Инициализация use case.

        Args:
            screen_factory: Фабрика для создания приветственных экранов
        """
        self._screen_factory = screen_factory

    def execute(self, request: WelcomeScreenRequest) -> WelcomeScreenResponse:
        """Выполнить сценарий отображения.

        Args:
            request: Запрос на отображение экрана

        Returns:
            Ответ с данными для отображения
        """
        welcome_screen = self._screen_factory.create_screen(request)

        return WelcomeScreenResponse(
            title=welcome_screen.content.get_title(),
            subtitle=welcome_screen.content.get_subtitle(),
            description=welcome_screen.content.get_description(),
            ascii_art=(
                welcome_screen.ascii_art.get_value()
                if welcome_screen.ascii_art
                else None
            ),
            language=welcome_screen.language.get_code(),
            press_enter_text=welcome_screen.press_enter_text,
        )
