"""Реализация сервиса переводов на основе JSON файлов.

Следует Clean Architecture - реализация интерфейса для работы с файлами.
Легко заменяемая реализация для разных источников данных.
"""

import json
import os

from src.interfaces.services.translation_service_interface import (
    TranslationError,
    TranslationService,
)


class FileTranslationService(TranslationService):
    """Реализация сервиса переводов на основе JSON файлов.

    Следует Clean Architecture - конкретная реализация
    для загрузки переводов из JSON файлов.
    """

    def __init__(self, translations_dir: str | None = None) -> None:
        """Инициализация сервиса.

        Args:
            translations_dir: Директория с файлами переводов
        """
        if translations_dir is None:
            # По умолчанию ищем в data/translations
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(current_dir))
            )
            translations_dir = os.path.join(
                project_root, "data", "translations"
            )

        self._translations_dir = translations_dir
        self._translations: dict[str, dict[str, str]] = {}
        self._supported_languages: list[str] = []

        self._load_translations()

    def get_translation(
        self, language_code: str, key: str, default: str
    ) -> str:
        """Получить перевод.

        Args:
            language_code: Код языка
            key: Ключ перевода
            default: Значение по умолчанию

        Returns:
            Переведённый текст или default
        """
        try:
            if language_code not in self._translations:
                return default

            if key not in self._translations[language_code]:
                return default

            return self._translations[language_code][key]

        except Exception as e:
            raise TranslationError(
                f"Ошибка получения перевода: {str(e)}"
            ) from e

    def get_supported_languages(self) -> list[str]:
        """Получить список поддерживаемых языков.

        Returns:
            Список кодов поддерживаемых языков
        """
        try:
            return self._supported_languages.copy()
        except Exception as e:
            raise TranslationError(f"Ошибка получения языков: {str(e)}") from e

    def is_language_supported(self, language_code: str) -> bool:
        """Проверить поддержку языка.

        Args:
            language_code: Код языка

        Returns:
            True если язык поддерживается
        """
        try:
            return language_code in self._translations
        except Exception as e:
            raise TranslationError(
                f"Ошибка проверки поддержки языка: {str(e)}"
            ) from e

    def _load_translations(self) -> None:
        """Загрузить переводы из файлов."""
        try:
            if not os.path.exists(self._translations_dir):
                # Создаём базовые переводы если директории нет
                self._create_default_translations()
                return

            # Загрузка всех JSON файлов
            for filename in os.listdir(self._translations_dir):
                if filename.endswith(".json"):
                    language_code = filename[:-5]  # Убираем .json
                    file_path = os.path.join(self._translations_dir, filename)

                    try:
                        with open(file_path, encoding="utf-8") as f:
                            translations = json.load(f)

                        if isinstance(translations, dict):
                            self._translations[language_code] = translations
                            self._supported_languages.append(language_code)

                    except (OSError, json.JSONDecodeError) as e:
                        print(
                            f"Предупреждение: не удалось загрузить файл {filename}: {e}"
                        )
                        continue

            # Если нет переводов, создаём базовые
            if not self._translations:
                self._create_default_translations()

        except Exception as e:
            raise TranslationError(
                f"Ошибка загрузки переводов: {str(e)}"
            ) from e

    def _create_default_translations(self) -> None:
        """Создать переводы по умолчанию."""
        default_translations = {
            "ru": {
                "welcome_title": "Добро пожаловать в D&D MUD",
                "welcome_subtitle": "Текстовая многопользовательская ролевая игра",
                "welcome_description": "Создайте персонажа, исследуйте мир и сражайтесь с монстрами в текстовом формате",
                "press_enter": "Нажмите Enter для продолжения...",
                "character_created": "Персонаж успешно создан",
                "character_sheet_title": "Лист персонажа",
                "level": "Уровень",
                "race": "Раса",
                "class": "Класс",
                "hit_points": "Хит-поинты",
                "armor_class": "Класс брони",
                "initiative": "Инициатива",
                "proficiency_bonus": "Бонус мастерства",
                "abilities": "Характеристики",
                "saving_throws": "Спасброски",
                "status": "Статус",
            },
            "en": {
                "welcome_title": "Welcome to D&D MUD",
                "welcome_subtitle": "Text-based multiplayer role-playing game",
                "welcome_description": "Create a character, explore the world and fight monsters in text format",
                "press_enter": "Press Enter to continue...",
                "character_created": "Character created successfully",
                "character_sheet_title": "Character Sheet",
                "level": "Level",
                "race": "Race",
                "class": "Class",
                "hit_points": "Hit Points",
                "armor_class": "Armor Class",
                "initiative": "Initiative",
                "proficiency_bonus": "Proficiency Bonus",
                "abilities": "Abilities",
                "saving_throws": "Saving Throws",
                "status": "Status",
            },
        }

        self._translations = default_translations
        self._supported_languages = list(default_translations.keys())

    def reload_translations(self) -> None:
        """Перезагрузить переводы.

        Полезно для обновления без перезапуска приложения.
        """
        self._translations.clear()
        self._supported_languages.clear()
        self._load_translations()

    def get_all_translations(self, language_code: str) -> dict[str, str]:
        """Получить все переводы для языка.

        Args:
            language_code: Код языка

        Returns:
            Словарь всех переводов
        """
        try:
            return self._translations.get(language_code, {}).copy()
        except Exception as e:
            raise TranslationError(
                f"Ошибка получения всех переводов: {str(e)}"
            ) from e
