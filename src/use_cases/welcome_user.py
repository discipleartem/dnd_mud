"""Use Case для приветствия пользователя.

Следует Clean Architecture - зависит только от Entities и Interfaces.
Содержит бизнес-логику приветственного экрана.
"""

from src.dto.welcome_dto import WelcomeRequest, WelcomeResponse
from src.interfaces.services.ascii_art_service import AsciiArtService
from src.interfaces.services.translation_service_interface import (
    TranslationService,
)


class WelcomeUserUseCase:
    """Use Case для приветствия пользователя.

    Следует Clean Architecture - содержит бизнес-логику
    подготовки приветственного экрана.
    """

    def __init__(
        self,
        translation_service: TranslationService,
        ascii_art_service: AsciiArtService,
    ) -> None:
        """Инициализация Use Case.

        Args:
            translation_service: Сервис переводов
            ascii_art_service: Сервис ASCII art
        """
        self._translation_service = translation_service
        self._ascii_art_service = ascii_art_service

    def execute(self, request: WelcomeRequest) -> WelcomeResponse:
        """Выполнить приветствие пользователя.

        Args:
            request: Запрос на приветствие

        Returns:
            Данные для отображения приветствия
        """
        try:
            # Бизнес-валидация языка
            language_code = self._validate_language(request.language)

            # Получение переводов
            translations = self._get_translations(language_code)

            # Бизнес-валидация контента
            self._validate_content(translations)

            # Получение ASCII art если нужно
            ascii_art = None
            if request.show_ascii_art:
                try:
                    ascii_art = self._ascii_art_service.get_dnd_logo()
                except Exception:
                    ascii_art = None

            return WelcomeResponse(
                title=translations["title"],
                subtitle=translations["subtitle"],
                description=translations["description"],
                ascii_art=ascii_art,
                language=language_code,
                press_enter_text=translations["press_enter"],
            )

        except Exception:
            # Fallback на базовые значения
            return self._get_fallback_response(request)

    def _validate_language(self, language_code: str) -> str:
        """Валидировать и нормализовать язык.

        Args:
            language_code: Код языка

        Returns:
            Валидный код языка

        Raises:
            ValueError: Если язык не поддерживается
        """
        if not language_code or not language_code.strip():
            return "ru"  # Язык по умолчанию

        language_code = language_code.strip().lower()

        if not self._translation_service.is_language_supported(language_code):
            # Проверка поддерживаемых языков
            supported = self._translation_service.get_supported_languages()
            if "ru" in supported:
                return "ru"
            elif supported:
                return supported[0]
            else:
                raise ValueError("Нет поддерживаемых языков")

        return language_code

    def _validate_content(self, translations: dict) -> None:
        """Валидация контента приветственного экрана.

        Args:
            translations: Словарь с переводами

        Raises:
            ValueError: Если контент невалиден
        """
        if not translations.get("title") or not translations["title"].strip():
            raise ValueError("Заголовок не может быть пустым")

        if (
            not translations.get("subtitle")
            or not translations["subtitle"].strip()
        ):
            raise ValueError("Подзаголовок не может быть пустым")

        if (
            not translations.get("description")
            or not translations["description"].strip()
        ):
            raise ValueError("Описание не может быть пустым")

        if (
            not translations.get("press_enter")
            or not translations["press_enter"].strip()
        ):
            translations["press_enter"] = "Нажмите Enter для продолжения..."

    def _get_translations(self, language_code: str) -> dict:
        """Получить переводы для приветствия.

        Args:
            language_code: Код языка

        Returns:
            Словарь с переводами
        """
        translations = {
            "title": self._translation_service.get_translation(
                language_code, "welcome_title", "Добро пожаловать в D&D MUD"
            ),
            "subtitle": self._translation_service.get_translation(
                language_code,
                "welcome_subtitle",
                "Текстовая многопользовательская ролевая игра",
            ),
            "description": self._translation_service.get_translation(
                language_code,
                "welcome_description",
                "Создайте персонажа, исследуйте мир и сражайтесь с монстрами в текстовом формате",
            ),
            "press_enter": self._translation_service.get_translation(
                language_code,
                "press_enter",
                "Нажмите Enter для продолжения...",
            ),
        }

        return translations

    def _get_fallback_response(
        self, request: WelcomeRequest
    ) -> WelcomeResponse:
        """Получить ответ в случае ошибок.

        Args:
            request: Оригинальный запрос

        Returns:
            Базовый ответ без внешних зависимостей
        """
        # При ошибках не пытаемся получать ASCII art, чтобы избежать дополнительных ошибок
        return WelcomeResponse(
            title="D&D Text MUD",
            subtitle="Текстовая многопользовательская игра",
            description="Создайте персонажа и начните приключение",
            ascii_art=None,  # Всегда None при fallback
            language=request.language or "ru",
            press_enter_text="Нажмите Enter для продолжения...",
        )

    def _get_simple_ascii_art(self) -> str:
        """Получить простой ASCII art без внешних сервисов.

        Returns:
            Простой ASCII логотип
        """
        return r"""
    ____  _____ _____ _____ ___  _   _
   |  _ \| ____|_   _|_   _/ _ \| \ | |
   | | | |  _|   | |   | || | | |  \| |
   | |_| | |___  | |   | || |_| | |\  |
   |____/|_____| |_|   |_| \___/|_| \_|
        """

    def get_supported_languages(self) -> list:
        """Получить список поддерживаемых языков.

        Returns:
            Список кодов языков
        """
        try:
            return self._translation_service.get_supported_languages()
        except Exception:
            return ["ru"]  # Fallback
