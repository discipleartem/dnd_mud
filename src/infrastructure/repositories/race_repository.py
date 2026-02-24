"""Реализация репозитория рас на основе YAML.

Конкретная реализация IRaceRepository для работы с YAML файлами.
Следует принципам Clean Architecture.
"""

from pathlib import Path
from typing import Any

from src.domain.entities.race import Feature, Race, SubRace
from src.domain.value_objects.size import Size, SizeCategory
from src.infrastructure.loaders.yaml_loader import YamlLoader
from src.interfaces.repositories import IRaceRepository, RepositoryError


class YamlRaceRepository(IRaceRepository):
    """Репозиторий рас на основе YAML файла.

    Реализует загрузку и сохранение рас из YAML файла.
    Использует YamlLoader для работы с данными.
    """

    def __init__(self, data_file: Path, yaml_loader: YamlLoader | None = None):
        """Инициализация репозитория.

        Args:
            data_file: Путь к YAML файлу с данными рас
            yaml_loader: Загрузчик YAML (опционально)
        """
        self._data_file = data_file
        self._loader = yaml_loader or YamlLoader(enable_cache=True)
        self._races_cache: dict[str, Race] | None = None

    def save(self, entity: Race) -> Race:
        """Сохранить расу в YAML файл.

        Args:
            entity: Раса для сохранения

        Returns:
            Сохранённая раса

        Raises:
            RepositoryError: При ошибке сохранения
        """
        try:
            # Загружаем текущие данные
            data = self._loader.load_from_file(self._data_file)

            # Конвертируем расу в YAML формат
            race_data = self._race_to_dict(entity)

            # Обновляем данные
            if "races" not in data:
                data["races"] = {}

            # Ищем ID расы (используем имя как ID)
            race_id = entity.name.lower().replace(" ", "_")
            data["races"][race_id] = race_data

            # Сохраняем обратно в файл
            self._save_yaml_data(data)

            # Обновляем кэш
            if self._races_cache is not None:
                self._races_cache[race_id] = entity

            return entity

        except Exception as e:
            raise RepositoryError(
                f"Ошибка при сохранении расы {entity.name}: {e}"
            ) from e

    def find_by_id(self, entity_id: str) -> Race | None:
        """Найти расу по ID.

        Args:
            entity_id: ID расы

        Returns:
            Раса или None если не найдена
        """
        races = self._load_races()
        return races.get(entity_id)

    def find_all(self) -> list[Race]:
        """Получить все расы.

        Returns:
            Список всех рас
        """
        races = self._load_races()
        return list(races.values())

    def delete(self, entity_id: str) -> bool:
        """Удалить расу.

        Args:
            entity_id: ID расы

        Returns:
            True если удалена, False если не найдена
        """
        try:
            # Загружаем текущие данные
            data = self._loader.load_from_file(self._data_file)

            if "races" not in data or entity_id not in data["races"]:
                return False

            # Удаляем расу
            del data["races"][entity_id]

            # Сохраняем обратно
            self._save_yaml_data(data)

            # Обновляем кэш
            if (
                self._races_cache is not None
                and entity_id in self._races_cache
            ):
                del self._races_cache[entity_id]

            return True

        except Exception as e:
            raise RepositoryError(
                f"Ошибка при удалении расы {entity_id}: {e}"
            ) from e

    def find_by_name(self, name: str) -> Race | None:
        """Найти расу по названию.

        Args:
            name: Название расы

        Returns:
            Раса или None если не найдена
        """
        races = self._load_races()

        for race in races.values():
            if race.name.lower() == name.lower():
                return race

        return None

    def get_all_race_names(self) -> list[str]:
        """Получить список всех названий рас.

        Returns:
            Список названий рас
        """
        races = self._load_races()
        return [race.name for race in races.values()]

    def _load_races(self) -> dict[str, Race]:
        """Загрузить расы из файла с кэшированием.

        Returns:
            Словарь рас
        """
        if self._races_cache is None:
            try:
                data = self._loader.load_from_file(self._data_file)
                self._races_cache = {}

                for race_id, race_data in data.get("races", {}).items():
                    race = self._dict_to_race(race_id, race_data)
                    self._races_cache[race_id] = race

            except Exception as e:
                raise RepositoryError(
                    f"Ошибка при загрузке рас из {self._data_file}: {e}"
                ) from e

        return self._races_cache

    def _dict_to_race(self, race_id: str, race_data: dict[str, Any]) -> Race:
        """Преобразовать словарь в Race.

        Args:
            race_id: ID расы
            race_data: Данные расы

        Returns:
            Объект Race
        """
        # Создание черт
        features = self._create_features_list(race_data.get("features", []))

        # Создание подрас
        subraces = self._create_subraces_dict(race_data.get("subraces", {}))

        # Получение размера
        size = self._get_size_from_string(race_data.get("size", "medium"))

        return Race(
            name=race_data["name"],
            description=race_data["description"],
            ability_bonuses=race_data.get("ability_bonuses", {}),
            ability_bonuses_description=race_data.get(
                "ability_bonuses_description", ""
            ),
            size=size,
            speed=race_data.get("speed", 30),
            age=race_data.get("age", {}),
            languages=race_data.get("languages", []),
            features=features,
            subraces=subraces,
            allow_base_race_choice=race_data.get(
                "allow_base_race_choice", False
            ),
        )

    def _race_to_dict(self, race: Race) -> dict[str, Any]:
        """Преобразовать Race в словарь.

        Args:
            race: Раса для конвертации

        Returns:
            Словарь данных расы
        """
        return {
            "name": race.name,
            "description": race.description,
            "ability_bonuses": race.ability_bonuses,
            "ability_bonuses_description": race.ability_bonuses_description,
            "size": race.size.category.value,
            "speed": race.speed,
            "age": race.age,
            "languages": race.languages,
            "features": [
                {
                    "name": feature.name,
                    "description": feature.description,
                    "mechanics": feature.mechanics,
                }
                for feature in race.features
            ],
            "subraces": {
                subrace_id: {
                    "name": subrace.name,
                    "description": subrace.description,
                    "ability_bonuses": subrace.ability_bonuses,
                    "ability_bonuses_description": (
                        subrace.ability_bonuses_description
                    ),
                    "languages": subrace.languages,
                    "features": [
                        {
                            "name": feature.name,
                            "description": feature.description,
                            "mechanics": feature.mechanics,
                        }
                        for feature in subrace.features
                    ],
                    "inherit_base_abilities": subrace.inherit_base_abilities,
                }
                for subrace_id, subrace in race.subraces.items()
            },
            "allow_base_race_choice": race.allow_base_race_choice,
        }

    def _create_features_list(
        self, features_data: list[dict[str, Any]]
    ) -> list[Feature]:
        """Создать список черт из данных.

        Args:
            features_data: Данные черт

        Returns:
            Список черт
        """
        return [
            Feature(
                name=feature_data["name"],
                description=feature_data["description"],
                mechanics=feature_data.get("mechanics", {}),
            )
            for feature_data in features_data
        ]

    def _create_subraces_dict(
        self, subraces_data: dict[str, Any]
    ) -> dict[str, SubRace]:
        """Создать словарь подрас из данных.

        Args:
            subraces_data: Данные подрас

        Returns:
            Словарь подрас
        """
        subraces = {}

        for subrace_id, subrace_data in subraces_data.items():
            features = self._create_features_list(
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
                features=features,
                inherit_base_abilities=subrace_data.get(
                    "inherit_base_abilities", True
                ),
            )

        return subraces

    def _get_size_from_string(self, size_str: str) -> Size:
        """Получить объект Size из строки.

        Args:
            size_str: Строковое представление размера

        Returns:
            Объект Size
        """
        try:
            category = SizeCategory(size_str.lower())
            return Size.from_category(category)
        except ValueError:
            return Size.from_category(SizeCategory.MEDIUM)

    def _save_yaml_data(self, data: dict[str, Any]) -> None:
        """Сохранить данные в YAML файл.

        Args:
            data: Данные для сохранения
        """
        import yaml

        with open(self._data_file, "w", encoding="utf-8") as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

    def clear_cache(self) -> None:
        """Очистить кэш рас."""
        self._races_cache = None
        self._loader.clear_cache()

    def preload(self) -> None:
        """Предзагрузить расы в кэш."""
        self._load_races()
