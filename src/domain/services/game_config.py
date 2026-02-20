# src/domain/services/game_config.py
"""Конфигурация игры."""

from dataclasses import dataclass
from typing import Dict, List, Union, Optional, TypedDict
from pathlib import Path


class ModData(TypedDict):
    """Данные мода."""

    name: str
    enabled: bool
    description: str
    is_active: bool
    folder_name: str
    starting_level: int
    version: str
    author: str
    dependencies: Optional[List[str]]
    config: Optional[Dict[str, Union[str, int, bool]]]
    load_order: Optional[int]


class AdventureSettings(TypedDict):
    """Настройки приключений."""

    show_all: Optional[bool]
    active: Optional[str]


class AdventureData(TypedDict):
    """Данные приключения."""

    name: str
    file: str
    enabled: bool
    description: str
    is_active: bool
    file_name: str
    recommended_level: int
    difficulty: str
    min_level: int
    max_level: int
    prerequisites: Optional[List[str]]
    show_all: bool
    active: str
    rewards: Optional[Dict[str, Union[int, List[str]]]]
    completion_requirements: Optional[Dict[str, Union[str, int]]]
    time_limit: Optional[int]
    encounters: Optional[List[Dict[str, Union[str, int]]]]


class CharacterCreationConfig(TypedDict):
    """Конфигурация создания персонажа."""

    point_buy: bool
    rolling_method: str
    max_level: int
    allow_multiclass: bool
    min_level: int
    starting_gold: int
    allowed_races: Optional[List[str]]
    allowed_classes: Optional[List[str]]
    attribute_points: int
    default_level: Optional[int]


class UIConfig(TypedDict):
    """Конфигурация интерфейса."""

    theme: str
    language: str
    show_tooltips: bool
    auto_save: bool
    save_interval: int
    window_size: Optional[List[int]]
    font_size: int
    color_scheme: str


@dataclass
class ModInfo:
    """Информация о модификации."""

    name: str
    enabled: bool = False
    description: str = ""
    is_active: bool = False
    folder_name: str = ""
    starting_level: int = 1

    @classmethod
    def from_dict(cls, data: ModData) -> "ModInfo":
        """Создает из словаря."""
        return cls(
            name=data.get("name", ""),
            enabled=data.get("enabled", False),
        )


class AdventureInfo:
    """Информация о приключении."""

    def __init__(
        self,
        name: str,
        file: str = "",
        enabled: bool = False,
        description: str = "",
        is_active: bool = False,
        file_name: str = "",
        recommended_level: int = 1,
        difficulty: str = "средний",
    ):
        self.name = name
        self.file = file
        self.enabled = enabled
        self.description = description
        self.is_active = is_active
        self.file_name = file_name
        self.recommended_level = recommended_level
        self.difficulty = difficulty

    @classmethod
    def from_dict(cls, data: AdventureData) -> "AdventureInfo":
        """Создает из словаря."""
        return cls(
            name=data.get("name", ""),
            file=data.get("file", ""),
            enabled=data.get("enabled", False),
            description=data.get("description", ""),
            is_active=data.get("is_active", False),
            file_name=data.get("file_name", ""),
        )


@dataclass
class GameConfig:
    """Основная конфигурация игры."""

    # Настройки персонажа
    character_creation: CharacterCreationConfig

    # Настройки UI
    ui: UIConfig

    # Модификации
    mods: Dict[str, ModInfo]

    # Приключения
    adventures: Dict[str, AdventureData]
    adventure_settings: AdventureSettings

    @classmethod
    def get_default_config(cls) -> "GameConfig":
        """Возвращает конфигурацию по умолчанию."""
        return cls(
            character_creation={
                "point_buy": False,
                "rolling_method": "standard_array",
                "max_level": 20,
                "allow_multiclass": True,
                "min_level": 1,
                "starting_gold": 10,
                "allowed_races": None,
                "allowed_classes": None,
                "attribute_points": 27,
                "default_level": 1,
            },
            ui={
                "theme": "dark",
                "language": "ru",
                "show_tooltips": True,
                "auto_save": True,
                "save_interval": 300,
                "window_size": [1200, 800],
                "font_size": 12,
                "color_scheme": "default",
            },
            mods={},
            adventure_settings={"show_all": False, "active": None},
            adventures={},
        )

    def get_available_mods(self) -> List[ModInfo]:
        """Возвращает список доступных модификаций."""
        mods = []
        for mod_name, mod_info in self.mods.items():
            mods.append(mod_info)
        return mods

    def get_available_adventures(self) -> List[AdventureInfo]:
        """Возвращает список доступных приключений."""
        adventures = []
        for adventure_data in self.adventures.values():
            adventures.append(AdventureInfo.from_dict(adventure_data))
        return adventures

    def deactivate_mod(self, mod_name: str) -> None:
        """Деактивирует модификацию."""
        for mod in self.get_available_mods():
            if mod.name == mod_name:
                mod.enabled = False
                break

    def activate_mod(self, mod_name: str) -> None:
        """Активирует модификацию."""
        for mod in self.get_available_mods():
            if mod.name == mod_name:
                mod.enabled = True
                break

    def get_show_all_adventures(self) -> bool:
        """Возвращает настройку показа всех приключений."""
        return bool(self.adventure_settings.get("show_all", False))

    def set_show_all_adventures(self, show: bool) -> None:
        """Устанавливает настройку показа всех приключений."""
        self.adventure_settings["show_all"] = show

    def get_default_starting_level(self) -> int:
        """Возвращает начальный уровень по умолчанию."""
        level = self.character_creation.get("default_level", 1)
        return int(level) if level is not None else 1

    def set_default_starting_level(self, level: int) -> None:
        """Устанавливает начальный уровень по умолчанию."""
        self.character_creation["default_level"] = level

    def get_active_adventure_info(self) -> Optional[AdventureInfo]:
        """Возвращает информацию об активном приключении."""
        active_name = self.adventure_settings.get("active")
        if active_name and active_name in self.adventures:
            return AdventureInfo.from_dict(self.adventures[active_name])
        return None

    def get_non_tutorial_adventures(self) -> List[AdventureInfo]:
        """Возвращает список приключений кроме учебного."""
        non_tutorial = []
        for adventure_data in self.adventures.values():
            if adventure_data.get("file_name") != "tutorial_adventure.yaml":
                non_tutorial.append(AdventureInfo.from_dict(adventure_data))
        return non_tutorial

    def set_active_adventure(self, adventure_name: str) -> None:
        """Устанавливает активное приключение."""
        self.adventure_settings["active"] = adventure_name


# Глобальный экземпляр конфигурации
game_config = GameConfig.get_default_config()


def load_config(config_path: Optional[Path] = None) -> None:
    """Загружает конфигурацию из файла."""
    global game_config

    if config_path and config_path.exists():
        try:
            import yaml

            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Обновляем конфигурацию
            if "character_creation" in data:
                game_config.character_creation.update(data["character_creation"])

            if "ui" in data:
                game_config.ui.update(data["ui"])

            if "mods" in data:
                game_config.mods.update(data["mods"])

            if "adventures" in data:
                game_config.adventures.update(data["adventures"])

        except Exception:
            # Оставляем конфигурацию по умолчанию при ошибке
            pass


def get_mods() -> List[ModInfo]:
    """Возвращает список модификаций."""
    mods = []
    for mod_name, mod_info in game_config.mods.items():
        mods.append(mod_info)
    return mods


def get_adventures() -> List[AdventureInfo]:
    """Возвращает список приключений."""
    adventures = []
    for adventure_data in game_config.adventures.values():
        adventures.append(AdventureInfo.from_dict(adventure_data))
    return adventures


def is_mod_enabled(mod_name: str) -> bool:
    """Проверяет, включена ли модификация."""
    for mod in get_mods():
        if mod.name == mod_name:
            return mod.enabled
    return False


def is_adventure_enabled(adventure_name: str) -> bool:
    """Проверяет, доступно ли приключение."""
    for adventure in get_adventures():
        if adventure.name == adventure_name:
            return adventure.enabled
    return False


def get_available_mods() -> List[ModInfo]:
    """Возвращает список доступных модификаций."""
    return get_mods()


def get_available_adventures() -> List[AdventureInfo]:
    """Возвращает список доступных приключений."""
    if game_config.adventure_settings.get("show_all", False):
        return get_adventures()
    else:
        return [adventure for adventure in get_adventures() if adventure.enabled]


def get_show_all_adventures() -> bool:
    """Возвращает настройку показа всех приключений."""
    return game_config.get_show_all_adventures()


def set_show_all_adventures(show: bool) -> None:
    """Устанавливает настройку показа всех приключений."""
    game_config.adventure_settings["show_all"] = show


def get_default_starting_level() -> int:
    """Возвращает начальный уровень по умолчанию."""
    level = game_config.character_creation.get("default_level", 1)
    return int(level) if level is not None else 1


def set_default_starting_level(level: int) -> None:
    """Устанавливает начальный уровень по умолчанию."""
    game_config.character_creation["default_level"] = level


def activate_mod(mod_name: str) -> bool:
    """Активирует модификацию.

    Returns:
        True если мод успешно активирован, иначе False
    """
    for mod in get_mods():
        if mod.name == mod_name:
            mod.enabled = True
            return True
    return False


def deactivate_mod(mod_name: str) -> bool:
    """Деактивирует модификацию.

    Returns:
        True если мод успешно деактивирован, иначе False
    """
    for mod in get_mods():
        if mod.name == mod_name:
            mod.enabled = False
            return True
    return False


def set_active_adventure(adventure_name: str) -> bool:
    """Устанавливает активное приключение.

    Returns:
        True если приключение успешно установлено, иначе False
    """
    try:
        game_config.adventure_settings["active"] = adventure_name
        return True
    except Exception:
        return False
