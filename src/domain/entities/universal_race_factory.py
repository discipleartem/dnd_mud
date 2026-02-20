# src/domain/entities/universal_race_factory.py
"""Универсальная фабрика рас D&D 5e."""

from typing import Dict, List, Optional, Union, Any
from .race import Race, RaceData, RaceFeature


class UniversalRaceFactory:
    """Фабрика для создания рас с поддержкой подрас."""

    _races_cache: Dict[str, Race] = {}
    _races_data: Dict[str, Any] = {}

    @classmethod
    def _load_races_data(cls) -> None:
        """Зружает данные рас из YAML."""
        if cls._races_data:
            return

        try:
            # Временно используем встроенные данные
            cls._load_fallback_data()
        except Exception:
            cls._load_fallback_data()

    @classmethod
    def _load_fallback_data(cls) -> None:
        """Зружает встроенные данные рас."""
        cls._races_data = {
            "human": {
                "name": "Человек",
                "display_name": "Человек",
                "description": "Самые адаптивные и амбициозные существа в этом мире.",
                "bonuses": {
                    "strength": 1,
                    "dexterity": 1,
                    "constitution": 1,
                    "intelligence": 1,
                    "wisdom": 1,
                    "charisma": 1,
                },
                "features": [],
                "size": "medium",
                "speed": 30,
                "languages": ["common"],
                "subraces": {},
                "alternative_features": {},
                "ability_scores": [],
                "allowed_attributes": [],
            },
            "elf": {
                "name": "Эльф",
                "display_name": "Эльф",
                "description": "Древняя и изящная раса, живущая в гармонии с магией и природой.",
                "bonuses": {"dexterity": 2},
                "features": [
                    {
                        "name": "Яркий ум",
                        "description": "Преимущество на спасброски от очарования",
                    },
                    {
                        "name": "Тёмное зрение",
                        "description": "Видит в условиях слабого освещения на 60 футов",
                    },
                ],
                "size": "medium",
                "speed": 30,
                "languages": ["common", "elvish"],
                "subraces": {},
                "alternative_features": {},
                "ability_scores": [],
                "allowed_attributes": [],
            },
        }

    @classmethod
    def create_race(cls, race_key: str, subrace_key: Optional[str] = None) -> Race:
        """Создает расу по ключу.

        Args:
            race_key: Ключ расы (human, elf, dwarf)
            subrace_key: Ключ подрасы (необязательно)

        Returns:
            Объект расы
        """
        cache_key = f"{race_key}_{subrace_key}" if subrace_key else race_key

        if cache_key in cls._races_cache:
            return cls._races_cache[cache_key]

        cls._load_races_data()

        if race_key not in cls._races_data:
            raise ValueError(f"Раса '{race_key}' не найдена")

        race_data = cls._races_data[race_key]

        # Создаем базовую расу
        # Создаем RaceData с правильной структурой
        race_dict: RaceData = {
            "name": str(race_data["name"]),
            "display_name": str(race_data["display_name"]),
            "description": str(race_data["description"]),
            "bonuses": {
                k: int(v)
                for k, v in race_data["bonuses"].items()
                if isinstance(v, (int, str)) and str(v).isdigit()
            },
            "features": race_data["features"],
            "size": str(race_data["size"]),
            "speed": int(race_data["speed"]),
            "languages": list(race_data["languages"]),
            "subraces": race_data.get("subraces", {}),
            "alternative_features": race_data.get("alternative_features"),
        }
        race = Race.from_dict(race_dict)

        # Применяем подрасу если указана
        subraces = race_data.get("subraces")
        if subrace_key and isinstance(subraces, dict) and subrace_key in subraces:
            subrace_data = subraces[subrace_key]

            # Применяем бонусы подрасы
            bonuses = subrace_data.get("bonuses", {})
            if isinstance(bonuses, dict):
                for attr, bonus in bonuses.items():
                    if isinstance(bonus, (int, str)) and str(bonus).isdigit():
                        race.add_bonus(attr, int(bonus))

            # Добавляем особенности подрасы
            features = subrace_data.get("features")
            if isinstance(features, list):
                for feature in features:
                    if isinstance(feature, dict):
                        # Преобразуем в RaceFeature с правильными типами
                        race_feature: Dict[str, Union[str, int, List[str], None]] = {
                            "name": str(feature.get("name", "")),
                            "description": str(feature.get("description", "")),
                            "type": str(feature.get("type")),
                            "bonus_value": feature.get("bonus_value"),
                            "max_choices": feature.get("max_choices"),
                            "choices": feature.get("choices"),
                        }
                        # Преобразуем в RaceFeature с правильными типами
                        if isinstance(race_feature, dict):
                            # Создаем RaceFeature с обязательными полями
                            bonus_value = race_feature.get("bonus_value")
                            max_choices = race_feature.get("max_choices")
                            race_feature_instance = RaceFeature(
                                name=str(race_feature.get("name", "")),
                                description=str(race_feature.get("description", "")),
                                type=str(race_feature.get("type", "")),
                                bonus_value=(
                                    int(bonus_value)
                                    if isinstance(bonus_value, int)
                                    else (
                                        int(bonus_value)
                                        if isinstance(bonus_value, str)
                                        and bonus_value.isdigit()
                                        else None
                                    )
                                ),
                                max_choices=(
                                    int(max_choices)
                                    if isinstance(max_choices, int)
                                    else (
                                        int(max_choices)
                                        if isinstance(max_choices, str)
                                        and max_choices.isdigit()
                                        else None
                                    )
                                ),
                                choices=list(feature.get("choices", [])),
                            )
                            race.add_feature(race_feature_instance)

        cls._races_cache[cache_key] = race
        return race

    @classmethod
    def get_race_choices(cls) -> Dict[str, str]:
        """Возвращает словарь для меню выбора рас."""
        cls._load_races_data()
        choices = {}
        choice_num = 1

        for race_key in cls._races_data:
            race_data = cls._races_data[race_key]
            choices[str(choice_num)] = race_data.get("display_name", race_key)
            choice_num += 1

        return choices

    @classmethod
    def get_race_key_by_choice(cls, choice_num: int) -> Optional[str]:
        """Возвращает ключ расы по номеру выбора."""
        cls._load_races_data()
        race_keys = list(cls._races_data.keys())

        if 1 <= choice_num <= len(race_keys):
            return race_keys[choice_num - 1]

        return None

    @classmethod
    def get_subrace_choices(cls, race_key: str) -> Dict[str, str]:
        """Возвращает подрасы для указанной расы."""
        cls._load_races_data()

        if race_key not in cls._races_data:
            return {}

        race_data = cls._races_data[race_key]
        subraces = race_data.get("subraces")
        if not isinstance(subraces, dict):
            return {}
        choices = {}
        choice_num = 1

        for subrace_key, subrace_data in subraces.items():
            display_name = subrace_data.get("display_name", subrace_key)
            choices[str(choice_num)] = str(display_name)  # Явное преобразование в str
            choice_num += 1

        return choices

    @classmethod
    def get_subrace_key_by_choice(cls, race_key: str, choice_num: int) -> Optional[str]:
        """Возвращает ключ подрасы по номеру выбора."""
        subraces_data = cls._races_data[race_key].get("subraces")
        if not isinstance(subraces_data, dict):
            return None
        subrace_keys = list(subraces_data.keys())

        if 1 <= choice_num <= len(subrace_keys):
            # Явно преобразуем в int для mypy, так как проверка диапазона гарантирует безопасность
            index = int(choice_num - 1)
            return subrace_keys[index]

        return None

    @classmethod
    def get_available_races(cls) -> Dict[str, str]:
        """Возвращает доступные расы."""
        cls._load_races_data()
        races = {}
        for race_key, race_data in cls._races_data.items():
            races[race_key] = race_data.get("display_name", race_key)
        return races

    @classmethod
    def get_all_races(cls) -> List[Race]:
        """Возвращает все объекты рас."""
        cls._load_races_data()
        races = []
        for race_key in cls._races_data.keys():
            race = cls.create_race(race_key)
            races.append(race)
        return races

    @classmethod
    def get_formatted_race_info(
        cls, race_key: str, subrace_key: Optional[str] = None
    ) -> Dict[str, Union[str, int, List[str]]]:
        """Возвращает форматированную информацию о расе."""
        race = cls.create_race(race_key, subrace_key)

        result: Dict[str, Union[str, int, List[str]]] = {
            "name": race.localized_name,
            "description": race.localized_description,
            "bonuses": cls._format_bonuses(race.get_all_bonuses()),
            "features": cls._format_features(
                [
                    {"name": f.name, "description": f.description}
                    for f in race.get_all_features()
                ]
            ),
            "size": race.size,
            "speed": race.speed,
            "languages": ", ".join(race.languages),
        }
        return result

    @classmethod
    def get_subrace_only_info(
        cls, race_key: str, subrace_key: str
    ) -> Dict[str, Union[str, int, List[str]]]:
        """Возвращает информацию только о подрасе."""
        cls._load_races_data()

        if race_key not in cls._races_data:
            return {}

        race_data = cls._races_data[race_key]
        subraces_data = race_data.get("subraces")
        if not isinstance(subraces_data, dict) or subrace_key not in subraces_data:
            return {}

        subrace_data = subraces_data[subrace_key]
        bonuses_raw = subrace_data.get("bonuses", {})
        features_raw = subrace_data.get("features", [])

        # Преобразуем бонусы в правильный формат
        bonuses_dict: Dict[str, int] = {}
        if isinstance(bonuses_raw, dict):
            bonuses_dict = {
                k: int(v)
                for k, v in bonuses_raw.items()
                if isinstance(v, (int, str)) and str(v).isdigit()
            }

        # Преобразуем особенности в правильный формат
        features_list: List[Dict[str, Union[str, int]]] = []
        if isinstance(features_raw, list):
            features_list = features_raw

        result: Dict[str, Union[str, int, List[str]]] = {
            "name": str(subrace_data.get("display_name", subrace_key)),
            "description": str(subrace_data.get("description", "")),
            "bonuses": cls._format_bonuses(bonuses_dict),
            "features": cls._format_features(features_list),
        }
        return result

    @classmethod
    def _format_bonuses(cls, bonuses: Dict[str, int]) -> str:
        """Форматирует бонусы для вывода."""
        if not bonuses:
            return ""

        lines = []
        for attr, bonus in bonuses.items():
            if bonus > 0:
                lines.append(f" {attr}: +{bonus}")

        return "\n".join(lines)

    @classmethod
    def _format_features(
        cls, features: Union[List[Dict[str, Union[str, int]]], str]
    ) -> str:
        """Форматирует особенности для вывода."""
        if isinstance(features, str):
            return features

        if not isinstance(features, list) or not features:
            return ""

        lines = []
        for feature in features:
            if isinstance(feature, dict):
                name = feature.get("name", "Неизвестная особенность")
                description = feature.get("description", "")
                lines.append(f"• {name}: {description}")

        return "\n".join(lines)

    @classmethod
    def clear_cache(cls) -> None:
        """Очищает кэш рас."""
        cls._races_cache.clear()
        cls._races_data.clear()
