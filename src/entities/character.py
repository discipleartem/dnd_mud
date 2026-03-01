"""Персонаж D&D - простая бизнес-сущность.

Следует Zen Python:
- Простое лучше сложного
- Явное лучше неявного
- Читаемость важна
"""

from dataclasses import dataclass

from interfaces.i18n_api import I18nTranslator


@dataclass
class Character:
    """Бизнес-сущность персонажа D&D.

    Содержит только базовые поля для текущего этапа разработки.
    Никаких зависимостей от базы данных или UI.
    """

    name: str
    level: int = 1
    hit_points: int = 10
    max_hit_points: int = 10
    _translator: I18nTranslator | None = None

    def set_translator(self, translator: I18nTranslator) -> None:
        """Установить переводчик для локализации.

        Args:
            translator: Переводчик
        """
        self._translator = translator

    def is_alive(self) -> bool:
        """Проверить, жив ли персонаж."""
        return self.hit_points > 0

    def get_status(self) -> str:
        """Получить статус персонажа."""
        if not self.is_alive():
            return self._t("character.status.dead")

        hp_percentage = (self.hit_points / self.max_hit_points) * 100

        if hp_percentage >= 80:
            return self._t("character.status.healthy")
        if hp_percentage >= 40:
            return self._t("character.status.wounded")
        return self._t("character.status.heavily_wounded")

    def _t(self, key: str, **kwargs) -> str:
        """Перевести строку.

        Args:
            key: Ключ перевода
            **kwargs: Параметры для форматирования

        Returns:
            Переведенная строка или ключ если переводчик не доступен
        """
        if self._translator:
            return self._translator.translate(key, **kwargs)
        return key

    def __str__(self) -> str:
        """Строковое представление."""
        level_text = self._t("levels.novice") if self.level <= 5 else self._t("levels.adventurer")
        return (
            f"{self.name} ({level_text}, "
            f"HP: {self.hit_points}/{self.max_hit_points})"
        )
