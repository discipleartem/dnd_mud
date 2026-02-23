"""
Упрощённый менеджер локализации для D&D MUD.

Использует YAML файлы вместо gettext .po/.mo для простоты.
Реализует паттерн Singleton.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


class SimpleI18nManager:
    """Упрощённый менеджер локализации (Singleton).
    
    Использует YAML файлы для хранения переводов.
    """
    
    _instance: Optional['SimpleI18nManager'] = None
    _translations: Dict[str, Any] = {}
    
    def __new__(cls) -> 'SimpleI18nManager':
        """Создание единственного экземпляра (Singleton)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Инициализация менеджера локализации."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._default_language = 'ru'
        self._current_language = self._default_language
        self._locales_dir = Path(__file__).parent / 'localization'
        
        # Загрузка переводов
        self.load_translations(self._default_language)
    
    def load_translations(self, language_code: str) -> None:
        """Загрузка переводов из YAML файла.
        
        Args:
            language_code: Код языка (например, 'ru', 'en').
        """
        yaml_file = self._locales_dir / f'{language_code}.yaml'
        
        if yaml_file.exists():
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    self._translations = yaml.safe_load(f) or {}
                self._current_language = language_code
            except Exception as e:
                print(f"❌ Ошибка загрузки локализации: {e}")
                self._translations = {}
        else:
            print(f"⚠️  Файл локализации не найден: {yaml_file}")
            self._translations = {}
    
    def get(self, key: str, **kwargs) -> str:
        """Получение переведённой строки по ключу.
        
        Args:
            key: Ключ строки в формате 'section.subsection.key'
            **kwargs: Параметры для форматирования строки
            
        Returns:
            Переведённая строка.
        """
        # Навигация по вложенной структуре
        keys = key.split('.')
        value = self._translations
        
        try:
            for k in keys:
                value = value[k]
        except (KeyError, TypeError):
            # Если ключ не найден, возвращаем сам ключ
            return key
        
        # Форматирование строки если есть параметры
        if kwargs and isinstance(value, str):
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value
        
        return str(value) if not isinstance(value, list) else value
    
    def get_current_language(self) -> str:
        """Получение текущего языка."""
        return self._current_language
    
    def get_available_languages(self) -> list[str]:
        """Получение списка доступных языков."""
        languages = []
        if self._locales_dir.exists():
            for item in self._locales_dir.iterdir():
                if item.is_file() and item.suffix == '.yaml':
                    languages.append(item.stem)
        return languages
    
    def set_language(self, language_code: str) -> None:
        """Установка языка интерфейса.
        
        Args:
            language_code: Код языка.
        """
        self.load_translations(language_code)


# Глобальный экземпляр менеджера
_i18n_manager = SimpleI18nManager()

# Удобные функции для использования
def t(key: str, **kwargs) -> str:
    """Глобальная функция перевода.
    
    Args:
        key: Ключ строки
        **kwargs: Параметры для форматирования
        
    Returns:
        Переведённая строка.
    """
    return _i18n_manager.get(key, **kwargs)

def set_language(language_code: str) -> None:
    """Установка языка интерфейса.
    
    Args:
        language_code: Код языка.
    """
    _i18n_manager.set_language(language_code)

def get_current_language() -> str:
    """Получение текущего языка."""
    return _i18n_manager.get_current_language()

def get_available_languages() -> list[str]:
    """Получение списка доступных языков."""
    return _i18n_manager.get_available_languages()
