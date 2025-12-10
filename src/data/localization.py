"""
Система локализации для DnD MUD Game.

Поддерживает:
- Базовую локализацию (data/yaml/localization.yaml)
- Локализацию модификаций (data/mods/*/localization.yaml)
- Локализацию приключений (data/adventures/*/localization.yaml)

Паттерны:
- Singleton для единственного экземпляра
- Strategy для разных источников локализации
- Chain of Responsibility для поиска переводов
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass


@dataclass
class LocalizationSource:
    """Источник локализации."""
    name: str  # Название источника (base, mod_name, adventure_name)
    priority: int  # Приоритет (выше = важнее)
    data: Dict[str, Any]  # Данные локализации
    source_type: str  # Тип: base, mod, adventure


class LocalizationManager:
    """
    Менеджер локализации.

    Паттерны:
    - Singleton: единственный экземпляр
    - Chain of Responsibility: поиск в цепочке источников

    Принципы:
    - DRY: единая система для всех типов локализации
    - SRP: отвечает только за локализацию
    - OCP: легко добавлять новые источники
    """

    _instance: Optional['LocalizationManager'] = None
    _initialized: bool = False

    # Приоритеты источников (выше = важнее)
    PRIORITY_BASE = 0
    PRIORITY_MOD = 100
    PRIORITY_ADVENTURE = 200

    def __new__(cls) -> 'LocalizationManager':
        """Singleton паттерн."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Инициализация менеджера локализации."""
        if self._initialized:
            return

        # Язык по умолчанию - русский
        self._current_language: str = "ru"
        self._sources: List[LocalizationSource] = []
        self._cache: Dict[str, str] = {}
        # Храним информацию о загруженных модах и приключениях для перезагрузки
        self._loaded_mods: Dict[str, Path] = {}  # mod_name -> mod_path
        self._loaded_adventures: Dict[str, Path] = {}  # adventure_name -> adventure_path
        self._initialized = True

        # Загрузка языка из настроек (если доступно)
        self._load_language_from_settings()

        # Загрузка базовой локализации
        self._load_base_localization()

    def set_language(self, language: str) -> None:
        """
        Установка языка интерфейса.

        Args:
            language: код языка (ru, en)
        """
        if language != self._current_language:
            self._current_language = language
            self._cache.clear()
            self._reload_all()

    def get_language(self) -> str:
        """Получение текущего языка."""
        return self._current_language

    def _load_language_from_settings(self) -> None:
        """Загрузка языка из settings.yaml."""
        settings_path = Path("data/yaml/settings.yaml")

        if not settings_path.exists():
            return

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Извлекаем язык из настроек (ui.language)
            if data and isinstance(data, dict):
                ui_settings = data.get('ui', {})
                if isinstance(ui_settings, dict):
                    language = ui_settings.get('language', 'ru')
                    if isinstance(language, str) and language:
                        self._current_language = language

        except Exception as e:
            # В случае ошибки используем язык по умолчанию (ru)
            print(f"Предупреждение: не удалось загрузить язык из настроек: {e}")

    def _load_base_localization(self) -> None:
        """Загрузка базовой локализации из data/yaml/localization.yaml."""
        base_path = Path("data/yaml/localization.yaml")

        if not base_path.exists():
            print(f"Предупреждение: базовая локализация не найдена: {base_path}")
            return

        try:
            with open(base_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Добавляем базовый источник
            source = LocalizationSource(
                name="base",
                priority=self.PRIORITY_BASE,
                data=data or {},
                source_type="base"
            )
            self._sources.append(source)

        except Exception as e:
            print(f"Ошибка загрузки базовой локализации: {e}")

    def load_mod_localization(self, mod_name: str, mod_path: Path) -> bool:
        """
        Загрузка локализации модификации.

        Args:
            mod_name: название мода
            mod_path: путь к директории мода

        Returns:
            bool: успешность загрузки
        """
        loc_path = mod_path / "localization.yaml"

        if not loc_path.exists():
            print(f"Предупреждение: локализация мода '{mod_name}' не найдена")
            return False

        try:
            with open(loc_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Удаляем старый источник этого мода (если есть)
            self._sources = [s for s in self._sources if s.name != f"mod_{mod_name}"]

            # Добавляем новый источник
            source = LocalizationSource(
                name=f"mod_{mod_name}",
                priority=self.PRIORITY_MOD,
                data=data or {},
                source_type="mod"
            )
            self._sources.append(source)

            # Сохраняем путь для перезагрузки
            self._loaded_mods[mod_name] = mod_path

            # Сортируем по приоритету (выше = важнее)
            self._sources.sort(key=lambda s: s.priority, reverse=True)

            # Очищаем кэш
            self._cache.clear()

            return True

        except Exception as e:
            print(f"Ошибка загрузки локализации мода '{mod_name}': {e}")
            return False

    def load_adventure_localization(self, adventure_name: str, adventure_path: Path) -> bool:
        """
        Загрузка локализации приключения.

        Args:
            adventure_name: название приключения
            adventure_path: путь к директории приключения

        Returns:
            bool: успешность загрузки
        """
        loc_path = adventure_path / "localization.yaml"

        if not loc_path.exists():
            print(f"Ошибка: приключение '{adventure_name}' должно иметь localization.yaml")
            return False

        try:
            with open(loc_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Удаляем старый источник этого приключения (если есть)
            self._sources = [s for s in self._sources
                             if s.name != f"adventure_{adventure_name}"]

            # Добавляем новый источник с высоким приоритетом
            source = LocalizationSource(
                name=f"adventure_{adventure_name}",
                priority=self.PRIORITY_ADVENTURE,
                data=data or {},
                source_type="adventure"
            )
            self._sources.append(source)

            # Сохраняем путь для перезагрузки
            self._loaded_adventures[adventure_name] = adventure_path

            # Сортируем по приоритету
            self._sources.sort(key=lambda s: s.priority, reverse=True)

            # Очищаем кэш
            self._cache.clear()

            return True

        except Exception as e:
            print(f"Ошибка загрузки локализации приключения '{adventure_name}': {e}")
            return False

    def unload_mod(self, mod_name: str) -> None:
        """
        Выгрузка локализации мода.

        Args:
            mod_name: название мода
        """
        self._sources = [s for s in self._sources if s.name != f"mod_{mod_name}"]
        # Удаляем из списка загруженных модов
        self._loaded_mods.pop(mod_name, None)
        self._cache.clear()

    def unload_adventure(self, adventure_name: str) -> None:
        """
        Выгрузка локализации приключения.

        Args:
            adventure_name: название приключения
        """
        self._sources = [s for s in self._sources
                         if s.name != f"adventure_{adventure_name}"]
        # Удаляем из списка загруженных приключений
        self._loaded_adventures.pop(adventure_name, None)
        self._cache.clear()

    def get(self, key: str, default: Optional[str] = None, **kwargs: Any) -> str:
        """
        Получение локализованной строки.

        Поиск идёт по цепочке источников от высокого приоритета к низкому:
        1. Приключения (priority 200)
        2. Моды (priority 100)
        3. Базовая локализация (priority 0)

        Args:
            key: ключ в формате "section.subsection.key" (например: "menu.continue")
            default: значение по умолчанию
            **kwargs: параметры для форматирования строки

        Returns:
            str: локализованная строка

        Examples:
            >>> loc.get("menu.continue")
            "Продолжить"

            >>> loc.get("combat.hit", target="Goblin", damage=5)
            "Вы нанесли 5 урона существу Goblin"
        """
        # Проверяем кэш
        cache_key = f"{self._current_language}:{key}"
        if cache_key in self._cache and not kwargs:
            return self._cache[cache_key]

        # Ищем в источниках (от высокого приоритета к низкому)
        for source in self._sources:
            value = self._get_from_source(source, key)
            if value is not None:
                # Кэшируем только если нет параметров форматирования
                if not kwargs:
                    self._cache[cache_key] = value

                # Применяем форматирование
                if kwargs:
                    try:
                        return value.format(**kwargs)
                    except KeyError as e:
                        print(f"Ошибка форматирования '{key}': отсутствует параметр {e}")
                        return value

                return value

        # Если не найдено, возвращаем default или сам ключ
        return default if default is not None else f"[{key}]"

    def _get_from_source(self, source: LocalizationSource, key: str) -> Optional[str]:
        """
        Получение значения из конкретного источника.

        Args:
            source: источник локализации
            key: ключ для поиска

        Returns:
            Optional[str]: найденное значение или None
        """
        # Проверяем наличие данных для текущего языка
        if self._current_language not in source.data:
            return None

        # Разбиваем ключ на части (например: "menu.continue" -> ["menu", "continue"])
        parts = key.split('.')
        current = source.data[self._current_language]

        # Идём по цепочке вложенных словарей
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        # Возвращаем только если это строка
        return current if isinstance(current, str) else None

    def has_key(self, key: str) -> bool:
        """
        Проверка наличия ключа локализации.

        Args:
            key: ключ для проверки

        Returns:
            bool: True если ключ существует
        """
        for source in self._sources:
            if self._get_from_source(source, key) is not None:
                return True
        return False

    def get_all_keys(self, prefix: str = "") -> List[str]:
        """
        Получение списка всех ключей локализации.

        Args:
            prefix: префикс для фильтрации (например: "menu")

        Returns:
            List[str]: список ключей
        """
        keys = set()

        for source in self._sources:
            if self._current_language in source.data:
                source_keys = self._extract_keys(
                    source.data[self._current_language],
                    prefix=""
                )
                keys.update(source_keys)

        # Фильтруем по префиксу
        if prefix:
            keys = {k for k in keys if k.startswith(prefix)}

        return sorted(keys)

    def _extract_keys(self, data: Any, prefix: str) -> List[str]:
        """
        Рекурсивное извлечение всех ключей из словаря.

        Args:
            data: данные для извлечения
            prefix: текущий префикс

        Returns:
            List[str]: список ключей
        """
        keys = []

        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, str):
                    keys.append(full_key)
                elif isinstance(value, dict):
                    keys.extend(self._extract_keys(value, full_key))

        return keys

    def _reload_all(self) -> None:
        """
        Перезагрузка всех источников локализации.
        
        Сохраняет и перезагружает все загруженные моды и приключения
        при смене языка.
        """
        # Сохраняем информацию о загруженных модах и приключениях
        loaded_mods = self._loaded_mods.copy()
        loaded_adventures = self._loaded_adventures.copy()

        # Очищаем источники
        self._sources.clear()
        self._cache.clear()

        # Загружаем базовую локализацию
        self._load_base_localization()

        # Перезагружаем все моды
        for mod_name, mod_path in loaded_mods.items():
            self.load_mod_localization(mod_name, mod_path)

        # Перезагружаем все приключения
        for adventure_name, adventure_path in loaded_adventures.items():
            self.load_adventure_localization(adventure_name, adventure_path)

    def get_loaded_sources(self) -> List[Dict[str, Any]]:
        """
        Получение информации о загруженных источниках локализации.

        Returns:
            List[Dict]: список источников с информацией
        """
        return [
            {
                "name": s.name,
                "type": s.source_type,
                "priority": s.priority,
                "has_current_language": self._current_language in s.data
            }
            for s in self._sources
        ]

    def debug_info(self) -> str:
        """
        Получение отладочной информации.

        Returns:
            str: информация о состоянии менеджера
        """
        info = [
            f"Текущий язык: {self._current_language}",
            f"Загружено источников: {len(self._sources)}",
            f"Размер кэша: {len(self._cache)}",
            "\nИсточники (по приоритету):"
        ]

        for source in self._sources:
            langs = list(source.data.keys())
            info.append(
                f"  - {source.name} (тип: {source.source_type}, "
                f"приоритет: {source.priority}, языки: {langs})"
            )

        return "\n".join(info)


# Глобальный экземпляр
localization_manager = LocalizationManager()


# Вспомогательная функция для удобства
def loc(key: str, default: Optional[str] = None, **kwargs: Any) -> str:
    """
    Короткая функция для получения локализации.

    Args:
        key: ключ локализации
        default: значение по умолчанию
        **kwargs: параметры форматирования

    Returns:
        str: локализованная строка

    Examples:
        >>> from src.data.localization import loc
        >>> text = loc("menu.continue")
        >>> text = loc("combat.hit", target="Goblin", damage=5)
    """
    return localization_manager.get(key, default, **kwargs)