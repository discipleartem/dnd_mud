"""Сервисы для отображения информации о расах.

Этот модуль реализует принцип разделения ответственности (SRP),
выделяя логику отображения информации о расах из доменных моделей.
Следует принципу KISS, предоставляя простые и явные методы.
"""

from typing import TYPE_CHECKING

from i18n import t

if TYPE_CHECKING:
    from ..entities.race import Feature


def _get_feature_emoji(feature_name: str) -> str:
    """Получить эмодзи для черты персонажа.

    Args:
        feature_name: Название черты

    Returns:
        Эмодзи соответствующий черте
    """
    feature_emoji_map = {
        "темное зрение": "🌙",
        "светочувствительность": "☀️",
        "устойчивость к магии": "🛡️",
        "мастерство": "⚔️",
        "ловкость": "🏃",
        "маскировка": "🥷",
    }

    feature_name_lower = feature_name.lower()
    return feature_emoji_map.get(feature_name_lower, "⚡")


class RaceDisplayService:
    """Сервис для отображения информации о расах в UI."""

    @staticmethod
    def display_features_with_emoji(
        features: list["Feature"], indent: str = "   "
    ) -> None:
        """Отобразить черты с эмодзи.

        Args:
            features: Список черт для отображения
            indent: Отступ для форматирования
        """
        features_label = t("new_game.details_section.features_label")
        print(f"{indent}{features_label}")
        for feature in features:
            feature_emoji = _get_feature_emoji(feature.name)
            print(f"{indent}   • {feature_emoji} {feature.name}")
            print(f"{indent}     {feature.description}")

    @staticmethod
    def display_abilities_description(
        description: str, indent: str = "   "
    ) -> None:
        """Отобразить описание способностей.

        Args:
            description: Описание способностей
            indent: Отступ для форматирования
        """
        if description:
            abilities_label = t("new_game.details_section.abilities_label")
            print(f"{indent}{abilities_label} {description}")
