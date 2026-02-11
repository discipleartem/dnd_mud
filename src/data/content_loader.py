"""Базовый загрузчик контента - Template Method паттерн."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, TypeVar, Generic

import yaml
from pydantic import BaseModel, ValidationError
from rich.console import Console

T = TypeVar('T')


class ContentLoader(ABC, Generic[T]):
    """Базовый класс для загрузчиков YAML контента.
    
    Реализует Template Method паттерн:
    - Определяет общую логику загрузки
    - Дочерние классы реализуют конкретные типы контента
    """
    
    def __init__(self, console: Console) -> None:
        """Инициализация загрузчика."""
        self.console = console
        self._cache: dict[str, T] = {}
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Получить тип контента для отладки."""
        pass
    
    @abstractmethod
    def validate_manifest(self, manifest_data: dict[str, Any]) -> T:
        """Валидировать манифест контента.
        
        Args:
            manifest_data: Данные из YAML файла
            
        Returns:
            T: Валидированный объект контента
        """
        pass
    
    @abstractmethod
    def load_content(self, content_path: Path) -> dict[str, T]:
        """Загрузить контент из указанного пути.
        
        Args:
            content_path: Путь к файлу контента
            
        Returns:
            dict[str, T]: Словарь {id: content}
        """
        pass
    
    def load_all_content(self, content_dir: Path) -> dict[str, T]:
        """Загрузить весь контент из директории.
        
        Args:
            content_dir: Директория с контентом
            
        Returns:
            dict[str, T]: Словарь всего контента
        """
        content_map: dict[str, T] = {}
        
        if not content_dir.exists():
            self.console.print(f"[yellow]Директория не найдена: {content_dir}[/yellow]")
            return content_map
        
        try:
            for content_file in content_dir.glob("*.yaml"):
                if content_file.is_file():
                    content = self.load_single_content(content_file)
                    if content:
                        content_map[content_file.stem] = content
                        
        except Exception as e:
            self.console.print(f"[red]Ошибка загрузки контента: {e}[/red]")
        
        return content_map
    
    def load_single_content(self, content_file: Path) -> T | None:
        """Загрузить один файл контента.
        
        Args:
            content_file: Путь к файлу
            
        Returns:
            T | None: Объект контента или None
        """
        stem = content_file.stem
        
        # Проверяем кэш
        if stem in self._cache:
            return self._cache[stem]
        
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and isinstance(data, dict):
                    manifest = data.get('manifest', {})
                    content = self.validate_manifest(data)
                    if content:
                        self._cache[stem] = content
                        return content
                else:
                    self.console.print(f"[red]Ошибка в манифесте: {content_file}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Ошибка загрузки {content_file}: {e}[/red]")
        
        return None
    
    def get_cached_content(self, content_id: str) -> T | None:
        """Получить контент из кэша."""
        return self._cache.get(content_id)
    
    def clear_cache(self) -> None:
        """Очистить кэш контента."""
        self._cache.clear()
    
    def get_cache_info(self) -> dict[str, Any]:
        """Получить информацию о кэше для отладки."""
        return {
            "content_type": self.get_content_type(),
            "cached_items": len(self._cache),
            "cache_keys": list(self._cache.keys())
        }
