from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from i18n import t
from src.core.yaml_utils import BaseYamlLoader
from src.services.language_service import get_language_service
from src.ui.services.language_display_service import (
    LanguageDisplayService,
)

from .character import Size


@dataclass
class Feature:
    """Черта расы или подрасы."""

    name: str
    description: str
    mechanics: dict[str, Any]


@dataclass
class SubRace:
    """Подраса."""

    name: str
    description: str
    ability_bonuses: dict[str, int] = field(default_factory=dict)
    ability_bonuses_description: str = ""
    languages: list[str] = field(default_factory=list)
    features: list[Feature] = field(default_factory=list)
    inherit_base_abilities: bool = True


@dataclass
class Race:
    """Раса персонажа."""

    name: str
    description: str
    ability_bonuses: dict[str, int] = field(default_factory=dict)
    ability_bonuses_description: str = ""
    size: Size = Size.MEDIUM
    speed: int = 30
    age: dict[str, int] = field(default_factory=dict)
    languages: list[str] = field(default_factory=list)
    features: list[Feature] = field(default_factory=list)
    subraces: dict[str, SubRace] = field(default_factory=dict)
    allow_base_race_choice: bool = False

    @staticmethod
    def get_all_races() -> dict[str, "Race"]:
        """Получить все расы."""
        loader = RaceLoader()
        return loader.load_races()

    def get_languages_display(self) -> str:
        """Получить локализованный список языков.

        Returns:
            Отформатированная строка с языками или сообщение об отсутствии
        """
        if not self.languages:
            result = t("errors.no_languages")
            return result if isinstance(result, str) else str(result)

        localized_language_names = self._get_localized_language_names()
        return ", ".join(localized_language_names)

    def _get_localized_language_names(self) -> list[str]:
        """Получить локализованные названия языков.

        Returns:
            Список локализованных названий языков
        """
        language_service = get_language_service()
        localized_names = []

        for language_code in self.languages:
            language = language_service.get_language_by_code(language_code)
            if language is not None:
                localized_names.append(
                    LanguageDisplayService.get_language_name(language)
                )
            else:
                localized_names.append(language_code)

        return localized_names

    def get_effective_ability_bonuses(
        self, subrace: Optional["SubRace"] = None
    ) -> dict[str, int]:
        """Получить итоговые бонусы к характеристикам.

        Args:
            subrace: Опциональная подраса

        Returns:
            Словарь итоговых бонусов к характеристикам
        """
        final_bonuses = {}

        if self._should_include_base_abilities(subrace):
            final_bonuses.update(self.ability_bonuses)

        if subrace is not None:
            final_bonuses.update(subrace.ability_bonuses)

        return final_bonuses

    def _should_include_base_abilities(
        self, subrace: Optional["SubRace"]
    ) -> bool:
        """Проверить, нужно ли включать бонусы базовой расы.

        Args:
            subrace: Опциональная подраса

        Returns:
            True если нужно включить бонусы базовой расы
        """
        return subrace is None or subrace.inherit_base_abilities

    @staticmethod
    def get_race_by_name(race_name: str) -> Optional["Race"]:
        """Получить расу по названию."""
        races = Race.get_all_races()
        for race in races.values():
            if race.name.lower() == race_name.lower():
                return race
        return None


class RaceLoader(BaseYamlLoader):
    """Загрузчик рас из YAML файла."""

    def __init__(self, data_path: Path | None = None) -> None:
        if data_path is None:
            data_path = self._get_default_data_path()
        super().__init__(data_path)

    def _get_default_data_path(self) -> Path:
        """Получить путь к файлу данных по умолчанию.

        Returns:
            Путь к файлу races.yaml
        """
        base_path = Path(__file__).parent.parent.parent.parent
        return base_path / "data" / "races.yaml"

    def load_races(self) -> dict[str, Race]:
        """Загрузить все расы из YAML файла.

        Returns:
            Словарь рас с их ID

        Raises:
            FileNotFoundError: Если файл не найден
            yaml.YAMLError: При ошибке парсинга YAML
        """
        data = self._load_yaml_data()
        return {
            race_id: self._create_race_from_data(race_id, race_data)
            for race_id, race_data in data.get("races", {}).items()
        }

    def _create_race_from_data(
        self, race_id: str, race_data: dict[str, Any]
    ) -> Race:
        """Создать объект Race из данных YAML."""
        features = self._create_features_list(race_data.get("features", []))
        subraces = self._create_subraces_dict(race_data.get("subraces", {}))
        size = self._get_size_from_string(race_data.get("size", "medium"))

        name = race_data["name"]
        description = race_data["description"]
        ability_bonuses = race_data.get("ability_bonuses", {})
        ability_bonuses_desc = race_data.get("ability_bonuses_description", "")
        speed = race_data.get("speed", 30)
        age = race_data.get("age", {})
        languages = race_data.get("languages", [])
        allow_base_choice = race_data.get("allow_base_race_choice", False)

        return Race(
            name=name,
            description=description,
            ability_bonuses=ability_bonuses,
            ability_bonuses_description=ability_bonuses_desc,
            size=size,
            speed=speed,
            age=age,
            languages=languages,
            features=features,
            subraces=subraces,
            allow_base_race_choice=allow_base_choice,
        )

    def _create_features_list(
        self, features_data: list[dict]
    ) -> list[Feature]:
        """Создать список черт из данных."""
        return [
            Feature(
                name=feature_data["name"],
                description=feature_data["description"],
                mechanics=feature_data["mechanics"],
            )
            for feature_data in features_data
        ]

    def _create_subraces_dict(
        self, subraces_data: dict[str, Any]
    ) -> dict[str, SubRace]:
        """Создать словарь подрас из данных."""
        subraces = {}
        for subrace_id, subrace_data in subraces_data.items():
            subrace_features = self._create_features_list(
                subrace_data.get("features", [])
            )

            subraces[subrace_id] = SubRace(
                name=subrace_data.get("name", subrace_id),
                description=subrace_data.get("description", ""),
                ability_bonuses=subrace_data.get("ability_bonuses", {}),
                ability_bonuses_description=subrace_data.get(
                    "ability_bonuses_description", ""
                ),
                languages=subrace_data.get("languages", []),
                features=subrace_features,
                inherit_base_abilities=subrace_data.get(
                    "inherit_base_abilities", True
                ),
            )
        return subraces

    def _get_size_from_string(self, size_str: str) -> Size:
        """Получить объект Size из строки.

        Args:
            size_str: Строковое представление размера.

        Returns:
            Объект Size или MEDIUM по умолчанию.
        """
        try:
            return Size(size_str)
        except ValueError:
            return Size.MEDIUM

    def get_race(self, race_id: str) -> Race | None:
        """Получить расу по ID.

        Args:
            race_id: ID расы для поиска.

        Returns:
            Объект расы или None если не найдена.
        """
        races = self.load_races()
        return races.get(race_id)

    def get_all_race_names(self) -> list[str]:
        """Получить список всех названий рас.

        Returns:
            Список названий рас.
        """
        races = self.load_races()
        return [race.name for race in races.values()]
