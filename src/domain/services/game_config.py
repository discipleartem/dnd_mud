"""
Сервис управления конфигурацией игры.

Применяемые паттерны:
- Singleton (Одиночка) - единый источник конфигурации
- Observer (Наблюдатель) - уведомление об изменениях
- Repository (Хранилище) - работа с файлами конфигурации

Применяемые принципы:
- Single Responsibility - только управление конфигурацией
- Open/Closed - легко добавить новые настройки
- Dependency Inversion - зависимость от абстракций файловой системы
"""

from typing import Dict, List, Optional, Set
from pathlib import Path
import yaml
import json
from dataclasses import dataclass, asdict


@dataclass
class ModInfo:
    """Информация о моде."""
    
    name: str
    description: str
    version: str
    author: str
    folder_name: str
    is_active: bool = False
    starting_level: Optional[int] = None


@dataclass
class AdventureInfo:
    """Информация о приключении."""
    
    name: str
    description: str
    file_name: str
    recommended_level: Optional[int] = None
    difficulty: str = "Средний"
    is_active: bool = False
    starting_level: Optional[int] = None


@dataclass
class GameSettings:
    """Настройки игры."""
    
    active_mods: List[str] = None
    active_adventure: Optional[str] = None
    show_all_adventures: bool = True
    default_starting_level: int = 1
    
    def __post_init__(self):
        if self.active_mods is None:
            self.active_mods = []


class GameConfig:
    """Сервис управления конфигурацией игры."""
    
    def __init__(self):
        """Инициализирует сервис конфигурации."""
        self._config_path = Path(__file__).parent.parent.parent.parent / "data" / "config"
        self._mods_path = Path(__file__).parent.parent.parent.parent / "data" / "mods"
        self._adventures_path = Path(__file__).parent.parent.parent.parent / "data" / "adventures"
        
        self._config_file = self._config_path / "game_settings.json"
        self._settings = GameSettings()
        
        # Загружаем настройки при инициализации
        self._load_settings()
    
    def _load_settings(self) -> None:
        """Загружает настройки из файла."""
        try:
            if self._config_file.exists():
                with open(self._config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._settings = GameSettings(**data)
            else:
                # Если файл не существует, создаем настройки по умолчанию
                self._settings = GameSettings()
                # Устанавливаем приключение Tutorial по умолчанию
                self._set_default_adventure()
                self._save_settings()
        except (json.JSONDecodeError, FileNotFoundError, TypeError):
            # Если файл поврежден, используем настройки по умолчанию
            self._settings = GameSettings()
            self._set_default_adventure()
            self._save_settings()
    
    def _set_default_adventure(self) -> None:
        """Устанавливает приключение по умолчанию только если есть другие приключения."""
        # Проверяем, есть ли приключения кроме учебного
        non_tutorial_adventures = self.get_non_tutorial_adventures()
        
        if not non_tutorial_adventures:
            # Если нет других приключений, не активируем ни одно
            self._settings.active_adventure = None
        else:
            # Если есть другие приключения, можно активировать учебное по умолчанию
            tutorial_file = "tutorial_adventure.yaml"
            adventures = self.get_available_adventures()
            
            for adventure in adventures:
                if adventure.file_name == tutorial_file:
                    self._settings.active_adventure = tutorial_file
                    break
    
    def _save_settings(self) -> None:
        """Сохраняет настройки в файл."""
        try:
            self._config_path.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self._settings), f, indent=2, ensure_ascii=False)
        except (IOError, TypeError):
            pass  # Логируем ошибку в реальном приложении
    
    def get_available_mods(self) -> List[ModInfo]:
        """Возвращает список доступных модов."""
        mods = []
        
        if not self._mods_path.exists():
            return mods
        
        for mod_folder in self._mods_path.iterdir():
            if not mod_folder.is_dir():
                continue
            
            config_file = mod_folder / "config.yaml"
            if not config_file.exists():
                continue
            
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f) or {}
                
                # Извлекаем информацию о моде
                name = config.get("name", mod_folder.name)
                description = config.get("description", "")
                version = config.get("version", "1.0.0")
                author = config.get("author", "Неизвестен")
                
                # Определяем начальный уровень из мода
                starting_level = None
                if "game_settings" in config and "starting_level" in config["game_settings"]:
                    starting_level = config["game_settings"]["starting_level"]
                elif "character_creation" in config and "starting_level" in config["character_creation"]:
                    starting_level = config["character_creation"]["starting_level"]
                
                # Проверяем, активен ли мод
                is_active = mod_folder.name in self._settings.active_mods
                
                mods.append(ModInfo(
                    name=name,
                    description=description,
                    version=version,
                    author=author,
                    folder_name=mod_folder.name,
                    is_active=is_active,
                    starting_level=starting_level
                ))
                
            except (yaml.YAMLError, IOError):
                continue
        
        return mods
    
    def get_available_adventures(self, include_tutorial: bool = True) -> List[AdventureInfo]:
        """Возвращает список доступных приключений."""
        adventures = []
        
        if not self._adventures_path.exists():
            return adventures
        
        for adventure_file in self._adventures_path.glob("*.yaml"):
            if not adventure_file.is_file():
                continue
            
            try:
                with open(adventure_file, "r", encoding="utf-8") as f:
                    adventure = yaml.safe_load(f) or {}
                
                name = adventure.get("name", adventure_file.stem)
                description = adventure.get("description", "")
                recommended_level = adventure.get("recommended_level")
                difficulty = adventure.get("difficulty", "Средний")
                
                # Для "Начало пути" всегда устанавливаем уровень 1
                if adventure_file.name == "tutorial_adventure.yaml":
                    starting_level = 1
                else:
                    # Определяем начальный уровень из приключения
                    starting_level = None
                    if "character_settings" in adventure and "starting_level" in adventure["character_settings"]:
                        starting_level = adventure["character_settings"]["starting_level"]
                    elif recommended_level:
                        starting_level = recommended_level
                
                # Проверяем, активно ли приключение
                is_active = adventure_file.name == self._settings.active_adventure
                
                # Фильтр учебного приключения если нужно
                if not include_tutorial and adventure_file.name == "tutorial_adventure.yaml":
                    continue
                
                # Проверяем, должно ли приключение отображаться
                should_show = self._settings.show_all_adventures or is_active
                
                if should_show:
                    adventures.append(AdventureInfo(
                        name=name,
                        description=description,
                        file_name=adventure_file.name,
                        recommended_level=recommended_level,
                        difficulty=difficulty,
                        is_active=is_active,
                        starting_level=starting_level
                    ))
                
            except (yaml.YAMLError, IOError):
                continue
        
        return adventures
    
    def get_non_tutorial_adventures(self) -> List[AdventureInfo]:
        """Возвращает список приключений кроме учебного."""
        return self.get_available_adventures(include_tutorial=False)
    
    def activate_mod(self, mod_folder_name: str) -> bool:
        """Активирует мод."""
        mods = self.get_available_mods()
        mod_exists = any(mod.folder_name == mod_folder_name for mod in mods)
        
        if not mod_exists:
            return False
        
        if mod_folder_name not in self._settings.active_mods:
            self._settings.active_mods.append(mod_folder_name)
            self._save_settings()
        
        return True
    
    def deactivate_mod(self, mod_folder_name: str) -> bool:
        """Деактивирует мод."""
        if mod_folder_name in self._settings.active_mods:
            self._settings.active_mods.remove(mod_folder_name)
            self._save_settings()
            return True
        return False
    
    def set_active_adventure(self, adventure_file_name: str) -> bool:
        """Устанавливает активное приключение."""
        adventures = self.get_available_adventures()
        adventure_exists = any(adv.file_name == adventure_file_name for adv in adventures)
        
        if not adventure_exists:
            return False
        
        self._settings.active_adventure = adventure_file_name
        self._save_settings()
        return True
    
    def get_active_mods_info(self) -> List[ModInfo]:
        """Возвращает информацию об активных модах."""
        all_mods = self.get_available_mods()
        return [mod for mod in all_mods if mod.is_active]
    
    def get_active_adventure_info(self) -> Optional[AdventureInfo]:
        """Возвращает информацию об активном приключении."""
        if not self._settings.active_adventure:
            return None
        
        adventures = self.get_available_adventures()
        for adventure in adventures:
            if adventure.file_name == self._settings.active_adventure:
                return adventure
        return None
    
    def set_show_all_adventures(self, show: bool) -> None:
        """Устанавливает флаг отображения всех приключений."""
        self._settings.show_all_adventures = show
        self._save_settings()
    
    def get_show_all_adventures(self) -> bool:
        """Возвращает флаг отображения всех приключений."""
        return self._settings.show_all_adventures
    
    def get_default_starting_level(self) -> int:
        """Возвращает начальный уровень по умолчанию."""
        return self._settings.default_starting_level
    
    def set_default_starting_level(self, level: int) -> None:
        """Устанавливает начальный уровень по умолчанию."""
        if 1 <= level <= 20:
            self._settings.default_starting_level = level
            self._save_settings()


# Глобальный экземпляр для удобного использования
game_config = GameConfig()
