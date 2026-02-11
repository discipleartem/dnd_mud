"""Менеджер локализации с приоритетами источников."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml
from rich.console import Console


class LocalizationManager:
    """Менеджер локализации с поддержкой приоритетов.
    
    Приоритеты источников:
    - adventure: 200 (высший)
    - mod: 100 (средний)  
    - base: 0 (базовый)
    
    Adventure и mod могут переопределять ключи из base.
    """
    
    def __init__(self, console: Console) -> None:
        """Инициализация менеджера локализации."""
        self.console = console
        self._cache: dict[str, dict[str, str]] = {}
        self._sources: list[tuple[int, str, Path]] = []
        
    def add_source(self, source_path: Path, priority: int) -> None:
        """Добавить источник локализации.
        
        Args:
            source_path: Путь к YAML файлу локализации
            priority: Приоритет источника (0/100/200)
        """
        if source_path.exists():
            self._sources.append((priority, source_path))
            # Сортируем по приоритету (высший первый)
            self._sources.sort(key=lambda x: x[0], reverse=True)
            self._cache.clear()  # Сбрасываем кэш
    
    def load_localization(self) -> None:
        """Загрузить все источники локализации."""
        if self._cache:
            return  # Уже загружено
        
        for priority, source_path in self._sources:
            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        for lang_key, translations in data.items():
                            if isinstance(translations, dict):
                                # Добавляем в кэш с учетом приоритета
                                if lang_key not in self._cache:
                                    self._cache[lang_key] = {}
                                
                                self._cache[lang_key].update(translations)
                                
            except Exception as e:
                self.console.print(f"[red]Ошибка загрузки локализации {source_path}: {e}[/red]")
    
    def get_text(self, key: str, language: str = "ru", **kwargs: Any) -> str:
        """Получить локализованный текст.
        
        Args:
            key: Ключ перевода
            language: Язык (ru/en)
            **kwargs: Параметры для форматирования
            
        Returns:
            str: Локализованный текст или ключ если не найден
        """
        if not self._cache:
            self.load_localization()
        
        # Ищем в указанном языке
        if language in self._cache and key in self._cache[language]:
            text = self._cache[language][key]
            return text.format(**kwargs) if kwargs else text
        
        # Fallback на base язык
        if "ru" in self._cache and key in self._cache["ru"]:
            text = self._cache["ru"][key]
            return text.format(**kwargs) if kwargs else text
        
        # Fallback на ключ в скобках
        return f"[{key}]"
    
    def get_available_languages(self) -> list[str]:
        """Получить список доступных языков."""
        if not self._cache:
            self.load_localization()
        
        return list(self._cache.keys())
    
    def reload(self) -> None:
        """Перезагрузить локализацию."""
        self._cache.clear()
        self.load_localization()
    
    def get_cache_info(self) -> dict[str, Any]:
        """Получить информацию о кэше для отладки."""
        if not self._cache:
            self.load_localization()
        
        info = {
            "languages": list(self._cache.keys()),
            "total_keys": sum(len(translations) for translations in self._cache.values()),
            "sources": [(priority, str(path)) for priority, path in self._sources]
        }
        return info
    
    def _format_debug_info(self) -> str:
        """Отформатировать отладочную информацию."""
        info = self.get_cache_info()
        lines = [
            "=== Localization Manager Debug Info ===",
            f"Languages: {', '.join(info['languages'])}",
            f"Total keys: {info['total_keys']}",
            "Sources (by priority):"
        ]
        
        for priority, path in info["sources"]:
            lines.append(f"  Priority {priority}: {path}")
        
        return "\n".join(lines)
