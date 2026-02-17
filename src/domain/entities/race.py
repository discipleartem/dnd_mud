"""
Модуль рас D&D MUD.

Определяет класс расы и их бонусы к характеристикам.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from ..interfaces.localization import get_text


@dataclass
class Race:
    """Класс расы D&D."""

    name: str
    bonuses: Dict[str, int] = field(default_factory=dict)
    description: str = field(default="")
    subraces: Dict[str, "Race"] = field(default_factory=dict)
    alternative_features: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Загружает локализацию."""
        if self.name:
            # НЕ меняем name - это ключ для локализации!
            # Загружаем бонусы из YAML если они не заданы
            if not self.bonuses:
                self.bonuses = {}
            # Загружаем альтернативные особенности
            if not self.alternative_features:
                self.alternative_features = {}

    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название."""
        return get_text(f"race_name.{self.name}")

    def apply_bonuses(self, attributes: Dict[str, int]) -> Dict[str, int]:
        """Применяет расовые бонусы к характеристикам.

        Args:
            attributes: Словарь с характеристиками персонажа

        Returns:
            Словарь с примененными бонусами
        """
        result = attributes.copy()
        for attr_name, bonus in self.bonuses.items():
            if attr_name in result:
                result[attr_name] += bonus
        return result

    def get_subrace(self, subrace_name: str) -> "Race":
        """Возвращает подрасу по имени."""
        return self.subraces.get(subrace_name)

    def add_subrace(self, subrace: "Race") -> None:
        """Добавляет подрасу."""
        self.subraces[subrace.name] = subrace

    def has_alternative_features(self) -> bool:
        """Проверяет наличие альтернативных особенностей."""
        return bool(self.alternative_features)

    def get_alternative_options(self) -> Dict[str, Any]:
        """Возвращает доступные альтернативные опции."""
        return self.alternative_features.get("options", {})

    def apply_alternative_bonuses(
        self, attributes: Dict[str, int], choices: Dict[str, Any]
    ) -> Dict[str, int]:
        """Применяет альтернативные бонусы к характеристикам.

        Args:
            attributes: Текущие характеристики
            choices: Выбранные альтернативные опции

        Returns:
            Характеристики с примененными бонусами
        """
        result = attributes.copy()

        # Обрабатываем выбор увеличения характеристик
        if "ability_scores" in choices:
            chosen_attrs = choices["ability_scores"]
            for attr in chosen_attrs:
                if attr in result:
                    result[attr] += 1

        return result
