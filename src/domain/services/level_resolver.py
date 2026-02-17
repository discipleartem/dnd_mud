"""
Сервис определения начального уровня персонажа.

Применяемые паттерны:
- Strategy (Стратегия) — разные источники определения уровня
- Chain of Responsibility (Цепочка обязанностей) — проверка источников по приоритету

Применяемые принципы:
- Single Responsibility — только определение начального уровня
- Open/Closed — легко добавить новые источники уровня
- Dependency Inversion — зависимость от абстракций конфигурации
"""

from typing import Optional, Dict, Any
from pathlib import Path
import yaml

from .game_config import game_config


class LevelSource:
    """Источник определения уровня."""
    
    def __init__(self, name: str, priority: int, level: int):
        self.name = name
        self.priority = priority
        self.level = level


class LevelResolver:
    """Сервис определения начального уровня персонажа."""
    
    def __init__(self):
        """Инициализирует резолвер."""
        self._mods_path = Path(__file__).parent.parent.parent.parent / "data" / "mods"
        self._adventures_path = Path(__file__).parent.parent.parent.parent / "data" / "adventures"
        self._config_path = Path(__file__).parent.parent.parent.parent / "data" / "config"
    
    def get_starting_level(self) -> int:
        """Определяет начальный уровень персонажа.
        
        Приоритеты:
        1. Активные модификации (самый высокий приоритет)
        2. Активное приключение
        3. Базовая конфигурация
        4. По умолчанию = 1
        
        Returns:
            Начальный уровень персонажа (1-20)
        """
        sources = self._collect_all_sources()
        
        # Сортируем по приоритету (чем меньше число, тем выше приоритет)
        sources.sort(key=lambda x: x.priority)
        
        # Берем первый источник с валидным уровнем
        for source in sources:
            if self._is_valid_level(source.level):
                return source.level
        
        # Если ничего не найдено, возвращаем уровень по умолчанию
        return 1
    
    def _collect_all_sources(self) -> list[LevelSource]:
        """Собирает все возможные источники уровня."""
        sources = []
        
        # 1. Проверяем активные моды
        mod_level = self._get_level_from_active_mods()
        if mod_level is not None:
            sources.append(LevelSource("Активная модификация", 1, mod_level))
        
        # 2. Проверяем активное приключение
        adventure_level = self._get_level_from_active_adventure()
        if adventure_level is not None:
            sources.append(LevelSource("Активное приключение", 2, adventure_level))
        
        # 3. Проверяем базовую конфигурацию
        config_level = self._get_level_from_config()
        if config_level is not None:
            sources.append(LevelSource("Конфигурация", 3, config_level))
        
        # 4. Уровень по умолчанию
        default_level = game_config.get_default_starting_level()
        sources.append(LevelSource("По умолчанию", 999, default_level))
        
        return sources
    
    def _get_level_from_active_mods(self) -> Optional[int]:
        """Получает уровень из активных модов."""
        active_mods = game_config.get_active_mods_info()
        
        # Берем уровень от первого активного мода
        for mod in active_mods:
            if mod.starting_level and self._is_valid_level(mod.starting_level):
                return mod.starting_level
        
        return None
    
    def _get_level_from_active_adventure(self) -> Optional[int]:
        """Получает уровень из активного приключения."""
        active_adventure = game_config.get_active_adventure_info()
        
        if active_adventure and active_adventure.starting_level:
            if self._is_valid_level(active_adventure.starting_level):
                return active_adventure.starting_level
        
        return None
    
    def _get_level_from_config(self) -> Optional[int]:
        """Получает уровень из базовой конфигурации."""
        config_file = self._config_path / "game_config.yaml"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            
            # Ищем настройку начального уровня
            if "starting_level" in config:
                level = config["starting_level"]
                if self._is_valid_level(level):
                    return level
            
            # Проверяем настройки персонажа
            if "character_creation" in config:
                char_creation = config["character_creation"]
                if "default_level" in char_creation:
                    level = char_creation["default_level"]
                    if self._is_valid_level(level):
                        return level
                        
        except (yaml.YAMLError, IOError):
            pass
        
        return None
    
    def _is_valid_level(self, level: Any) -> bool:
        """Проверяет, что уровень является валидным."""
        try:
            int_level = int(level)
            return 1 <= int_level <= 20
        except (ValueError, TypeError):
            return False
    
    def get_level_info(self) -> Dict[str, Any]:
        """Возвращает подробную информацию об определении уровня."""
        sources = self._collect_all_sources()
        sources.sort(key=lambda x: x.priority)
        
        final_level = self.get_starting_level()
        active_source = None
        
        for source in sources:
            if self._is_valid_level(source.level) and source.level == final_level:
                active_source = source
                break
        
        return {
            "final_level": final_level,
            "active_source": active_source.name if active_source else "По умолчанию",
            "all_sources": [
                {
                    "name": source.name,
                    "priority": source.priority,
                    "level": source.level,
                    "is_active": source == active_source
                }
                for source in sources
            ]
        }


# Глобальный экземпляр для удобного использования
level_resolver = LevelResolver()
