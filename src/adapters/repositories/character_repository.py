"""Менеджер персонажей D&D MUD."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union, TypedDict, Dict
from datetime import datetime

from ...domain.entities.character import Character


class CharacterData(TypedDict):
    """Данные персонажа."""

    name: str
    race: Dict[str, Union[str, int]]
    character_class: Dict[str, Union[str, int]]
    level: int
    attributes: Dict[str, Dict[str, Union[str, int]]]
    hp_max: int
    hp_current: int
    ac: int
    gold: int


class CharacterSaveData(TypedDict):
    """Данные сохранения персонажа."""

    character: CharacterData
    save_date: str


@dataclass
class CharacterSaveDataWrapper:
    """Обертка для данных сохранения персонажа."""

    pass


class CharacterManager:
    """Простой менеджер персонажей."""

    _instance: Optional["CharacterManager"] = None
    _saves_dir: Optional[Path] = None

    def __new__(cls) -> "CharacterManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._saves_dir = (
                Path(__file__).parent.parent.parent / "data" / "saves"
            )
            if cls._instance._saves_dir:
                cls._instance._saves_dir.mkdir(exist_ok=True)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "CharacterManager":
        """Возвращает единственный экземпляр менеджера."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def save_character(self, character: Character) -> bool:
        """Сохраняет персонажа."""
        try:
            filename = f"{character.name}_{character.race.name}_{character.character_class.name}.json"
            if self._saves_dir:
                filepath = self._saves_dir / filename
            else:
                return False

            save_data = {
                "name": character.name,
                "level": character.level,
                "race_name": character.race.name,
                "class_name": character.character_class.name,
                "strength": character.get_attribute_value("strength"),
                "dexterity": character.get_attribute_value("dexterity"),
                "constitution": character.get_attribute_value("constitution"),
                "intelligence": character.get_attribute_value("intelligence"),
                "wisdom": character.get_attribute_value("wisdom"),
                "charisma": character.get_attribute_value("charisma"),
                "hp_max": character.hp_max,
                "hp_current": character.hp_current,
                "ac": character.ac,
                "gold": getattr(character, "gold", 0),
                "created_at": datetime.now().isoformat(),
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception:
            return False

    def load_character(self, filename: str) -> Optional[Character]:
        """Загружает персонажа."""
        try:
            if self._saves_dir:
                filepath = self._saves_dir / filename
            else:
                return None

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            from ...domain.entities.universal_race_factory import UniversalRaceFactory
            from ...domain.entities.class_factory import CharacterClassFactory
            from ...domain.entities.attribute import Attribute

            # Создаем персонажа из сохраненных данных
            race = UniversalRaceFactory.create_race(data["race_name"])
            character_class = CharacterClassFactory.create_class(data["class_name"])

            attributes = {
                "strength": Attribute("strength", data["strength"]),
                "dexterity": Attribute("dexterity", data["dexterity"]),
                "constitution": Attribute("constitution", data["constitution"]),
                "intelligence": Attribute("intelligence", data["intelligence"]),
                "wisdom": Attribute("wisdom", data["wisdom"]),
                "charisma": Attribute("charisma", data["charisma"]),
            }

            character = Character(
                name=data["name"],
                level=data["level"],
                race=race,
                character_class=character_class,
                attributes=attributes,
                hp_max=data["hp_max"],
                hp_current=data["hp_current"],
                ac=data["ac"],
                gold=data.get("gold", 0),
            )

            return character
        except Exception:
            return None

    def list_characters(self) -> List[str]:
        """Возвращает список сохраненных персонажей."""
        try:
            if self._saves_dir:
                return [f.name for f in self._saves_dir.glob("*.json")]
            return []
        except Exception:
            return []

    def get_character_info(self, filename: str) -> Optional[dict[str, Union[str, int]]]:
        """Возвращает базовую информацию о персонаже."""
        try:
            if self._saves_dir:
                filepath = self._saves_dir / filename
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                return {
                    "name": data["name"],
                    "race": data["race_name"],
                    "class": data["class_name"],
                    "level": data["level"],
                }
            return None
        except Exception:
            return None


class CharacterRepository:
    """Репозиторий для работы с персонажами."""

    def __init__(self, save_directory: Optional[Path] = None):
        """Инициализирует репозиторий."""
        self.save_directory = save_directory or Path("data/saves")

    def save_character(self, character: Character, format_type: str = "json") -> bool:
        """Сохраняет персонажа."""
        try:
            save_data = {
                "character": {
                    "name": character.name,
                    "race": {"name": character.race.name, "type": "race"},
                    "character_class": {
                        "name": character.character_class.name,
                        "type": "class",
                    },
                    "level": character.level,
                    "attributes": {
                        attr_name: {"value": attr.value, "name": attr_name}
                        for attr_name, attr in character.attributes.items()
                    },
                    "hp_max": character.hp_max,
                    "hp_current": character.hp_current,
                    "ac": character.ac,
                    "gold": character.gold,
                },
                "save_date": datetime.now().isoformat(),
            }
            if format_type.lower() == "json":
                filepath = self.save_directory / f"{character.name}.json"
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                return True
            elif format_type.lower() == "yaml":
                import yaml

                filepath = self.save_directory / f"{character.name}.yaml"
                with open(filepath, "w", encoding="utf-8") as f:
                    yaml.dump(
                        save_data, f, default_flow_style=False, allow_unicode=True
                    )
                return True
            return False
        except Exception:
            return False

    def load_character(self, filename: str) -> Optional[Character]:
        """Загружает персонажа."""
        try:
            filepath = self.save_directory / filename
            if not filepath.exists():
                return None

            if filename.endswith(".json"):
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return self._create_character_from_dict(data)
            elif filename.endswith((".yaml", ".yml")):
                import yaml

                with open(filepath, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return self._create_character_from_dict(data)
            return None
        except Exception:
            return None

    def list_characters(self) -> List[str]:
        """Возвращает список сохраненных персонажей."""
        try:
            return (
                [f.name for f in self.save_directory.glob("*.json") if f.is_file()]
                + [f.name for f in self.save_directory.glob("*.yaml") if f.is_file()]
                + [f.name for f in self.save_directory.glob("*.yml") if f.is_file()]
            )
        except Exception:
            return []

    def _create_character_from_dict(
        self, data: Dict[str, Union[str, int, Dict]]
    ) -> Optional[Character]:
        """Создает персонажа из словаря."""
        try:
            character_data = data.get("character", data)
            if not isinstance(character_data, dict):
                return None

            from ...domain.entities.universal_race_factory import UniversalRaceFactory
            from ...domain.entities.class_factory import CharacterClassFactory
            from ...domain.entities.attribute import Attribute

            race_data = character_data.get("race", {})
            class_data = character_data.get("character_class", {})

            race_name = (
                race_data.get("name", "Человек")
                if isinstance(race_data, dict)
                else str(race_data)
            )
            class_name = (
                class_data.get("name", "Воин")
                if isinstance(class_data, dict)
                else str(class_data)
            )

            race = UniversalRaceFactory.create_race(race_name)
            character_class = CharacterClassFactory.create_class(class_name)

            attributes_data = character_data.get("attributes", {})
            attributes = {}
            if isinstance(attributes_data, dict):
                for attr_name, attr_info in attributes_data.items():
                    if isinstance(attr_info, dict) and "value" in attr_info:
                        attributes[attr_name] = Attribute(attr_name, attr_info["value"])
                    elif isinstance(attr_info, (int, float)):
                        attributes[attr_name] = Attribute(attr_name, int(attr_info))

            def safe_get_int(key: str, default: int) -> int:
                value = character_data.get(key, default)
                return (
                    int(value)
                    if isinstance(value, (int, str)) and str(value).isdigit()
                    else default
                )

            level = safe_get_int("level", 1)
            hp_max = safe_get_int("hp_max", 10)
            hp_current = safe_get_int("hp_current", 10)
            ac = safe_get_int("ac", 10)
            gold = safe_get_int("gold", 0)

            return Character(
                name=character_data.get("name", "Безымянный"),
                race=race,
                character_class=character_class,
                level=level,
                attributes=attributes,
                hp_max=hp_max,
                hp_current=hp_current,
                ac=ac,
                gold=gold,
            )
        except Exception:
            return None


# Функции-обертки для обратной совместимости
def save_character(character: Character, format_type: str = "json") -> bool:
    """Сохраняет персонажа через репозиторий."""
    repository = CharacterRepository()
    return repository.save_character(character, format_type)


def load_character(filename: str) -> Optional[Character]:
    """Загружает персонажа через репозиторий."""
    repository = CharacterRepository()
    return repository.load_character(filename)


def list_characters() -> List[str]:
    """Возвращает список персонажей через репозиторий."""
    repository = CharacterRepository()
    return repository.list_characters()


def get_character_info(filename: str) -> Optional[dict[str, Union[str, int]]]:
    """Возвращает информацию о персонаже через менеджер."""
    manager = CharacterManager()
    return manager.get_character_info(filename)
