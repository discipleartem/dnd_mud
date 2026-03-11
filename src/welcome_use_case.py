"""Простой сценарий приветственного экрана.

Следует KISS и Zen Python - просто и явно.
"""

from src.services.welcome_service import WelcomeService
from src.welcome_dto import WelcomeScreenRequest, WelcomeScreenResponse


class ShowWelcomeScreenUseCase:
    """Простой сценарий отображения приветственного экрана.

    Следует KISS - просто и понятно.
    """

    def __init__(self, service: WelcomeService | None = None) -> None:
        """Инициализация use case.

        Args:
            service: Сервис приветственного экрана. Если None, создается экземпляр.
        """
        self.service = service if service is not None else WelcomeService()

    def execute(self, request: WelcomeScreenRequest) -> WelcomeScreenResponse:
        """Выполнить сценарий отображения."""
        welcome_screen = self.service.create_welcome_screen(
            language_code=request.language,
            show_ascii_art=request.show_ascii_art
        )

        display_data = self.service.get_display_content(welcome_screen)

        return WelcomeScreenResponse(
            title=display_data["title"],
            subtitle=display_data["subtitle"],
            description=display_data["description"],
            ascii_art=display_data["ascii_art"] if display_data["ascii_art"] else None,
            language=display_data["language"],
            press_enter_text=display_data["press_enter_text"]
        )
