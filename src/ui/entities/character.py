"""Сущности персонажа D&D MUD."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional

from i18n import t

if TYPE_CHECKING:
    from .abilities import AbilityScores
    from .language_loader import Language
    from .race import Race, SubRace


class Size(Enum):
    """Размер персонажа с поддержкой локализации."""

    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"
    COLOSSAL = "colossal"

    def get_localized_name(self) -> str:
        """Получить локализованное название размера."""
        result = t(f"character.size.{self.value}")
        return result if isinstance(result, str) else str(result)

    def __str__(self) -> str:
        """Строковое представление с локализацией."""
        return self.get_localized_name()


@dataclass
class Character:
    """Персонаж D&D."""

    name: str = "Безымянный"
    race: Optional["Race"] = None
    _class: str = ""
    level: int = 1
    subrace: Optional["SubRace"] = None
    sub_class: str | None = None
    ability_scores: Optional["AbilityScores"] = None

    @property
    def size(self) -> Size:
        """Получить размер персонажа от расы."""
        return self.race.size if self.race else Size.MEDIUM

    @property
    def speed(self) -> int:
        """Получить скорость персонажа от расы."""
        return self.race.speed if self.race else 30

    @property
    def age(self) -> dict[str, int]:
        """Получить возрастные характеристики от расы."""
        return self.race.age if self.race else {}

    @property
    def languages(self) -> list[str]:
        """Получить языки персонажа от расы и подрасы."""
        languages = []
        if self.race:
            languages.extend(self.race.languages)
        if self.subrace:
            languages.extend(self.subrace.languages)
        return languages

    def get_language_objects(self) -> list["Language"]:
        """Получить объекты языков персонажа с поддержкой локализации."""
        from .language_loader import LanguageLoader

        loader = LanguageLoader()
        language_objects = []

        for lang_code in self.languages:
            lang_obj = loader.get_language(lang_code)
            if lang_obj:
                language_objects.append(lang_obj)

        return language_objects

    def get_learnable_languages(self) -> list["Language"]:
        """Получить языки, которые может изучить персонаж."""
        from .language_loader import LanguageLoader

        loader = LanguageLoader()
        learnable = set()

        if self.race:
            race_code = self._normalize_entity_name(self.race.name)
            race_languages = loader.get_learnable_languages_for_race(race_code)
            learnable.update(race_languages)

        if self._class:
            class_code = self._normalize_entity_name(self._class)
            class_languages = loader.get_learnable_languages_for_class(
                class_code
            )
            learnable.update(class_languages)

        known_codes = {lang.code for lang in self.get_language_objects()}
        return [lang for lang in learnable if lang.code not in known_codes]

    def _normalize_entity_name(self, entity_name: str) -> str:
        """Нормализовать имя сущности для поиска."""
        return entity_name.lower().replace(" ", "_")

    def can_learn_language(self, lang_code: str) -> bool:
        """Проверить, может ли персонаж изучить конкретный язык."""
        from .language_loader import LanguageLoader

        loader = LanguageLoader()
        language = loader.get_language(lang_code)

        if not language or lang_code in self.languages:
            return False

        if self.race:
            race_code = self._normalize_entity_name(self.race.name)
            if language.is_learnable_by_race(race_code):
                return True

        if self._class:
            class_code = self._normalize_entity_name(self._class)
            if language.is_learnable_by_class(class_code):
                return True

        return False
