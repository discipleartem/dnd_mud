"""Простой сервис приветственного экрана.

Следует KISS - просто и понятно.
"""

from typing import Final

from ..constants import (
    DEFAULT_DESCRIPTION,
    DEFAULT_LANGUAGE,
    DEFAULT_PRESS_ENTER,
    DEFAULT_SUBTITLE,
    DEFAULT_TITLE,
)
from ..utils.translation_loader import TranslationLoader
from ..value_objects.ascii_art import AsciiArt
from ..value_objects.language import Language
from ..value_objects.welcome_content import WelcomeContent
from ..welcome_screen import WelcomeScreen

# Явное значение по умолчанию (Zen Python: явное лучше неявного)
DEFAULT_LANGUAGE_CODE: Final[str] = DEFAULT_LANGUAGE


class WelcomeService:
    """Простой сервис приветственного экрана.

    Следует KISS - просто и понятно.
    """

    def __init__(self) -> None:
        """Инициализация сервиса."""
        self._loader = TranslationLoader()

    def create_welcome_screen(
        self,
        language_code: str | None = None,
        show_ascii_art: bool = True
    ) -> WelcomeScreen:
        """Создать приветственный экран."""
        language = self._get_language(language_code)
        lang_code = language.get_code()

        content = WelcomeContent(
            title=self._get_translation(lang_code, "welcome.title", DEFAULT_TITLE),
            subtitle=self._get_translation(lang_code, "welcome.subtitle", DEFAULT_SUBTITLE),
            description=self._get_translation(lang_code, "welcome.description", DEFAULT_DESCRIPTION)
        )

        return WelcomeScreen(
            content=content,
            ascii_art=AsciiArt.create_dnd_logo() if show_ascii_art else None,
            language=language,
            press_enter_text=self._get_translation(lang_code, "welcome.press_enter", DEFAULT_PRESS_ENTER)
        )

    def get_display_content(self, screen: WelcomeScreen) -> dict[str, str]:
        """Получить контент для отображения."""
        ascii_art_value = ""
        if screen.ascii_art and not screen.ascii_art.is_empty():
            ascii_art_value = screen.ascii_art.value

        return {
            "title": screen.content.get_title(),
            "subtitle": screen.content.get_subtitle(),
            "description": screen.content.get_description(),
            "ascii_art": ascii_art_value,
            "language": screen.language.get_code(),
            "press_enter_text": screen.press_enter_text.strip()
        }

    def _get_language(self, language_code: str | None) -> Language:
        """Получить язык.

        Следует KISS - простая логика без вложенностей.
        """
        if not language_code:
            return Language.create_default()

        try:
            language = Language.from_string(language_code)
            # Проверяем наличие переводов
            if self._get_translation(language_code, "welcome.title", ""):
                return language
        except ValueError:
            pass

        return Language.create_default()

    def _get_translation(self, language_code: str, key: str, default: str) -> str:
        """Получить перевод с fallback на default."""
        translation = self._loader.get_translation(language_code, key, default)
        return translation if translation is not None else default
