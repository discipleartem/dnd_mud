"""Реализация интерфейса локализации для доменного слоя."""

from typing import Optional
from src.domain.interfaces.localization import LocalizationInterface


class LocalizationAdapter(LocalizationInterface):
    """Адаптер для существующей системы локализации."""
    
    def __init__(self, loader):
        """Инициализирует адаптер с существующим loader."""
        self._loader = loader
    
    def get_text(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """Получает локализованный текст по ключу."""
        try:
            # Пробуем получить через существующий loader
            if hasattr(self._loader, 'get_text'):
                return self._loader.get_text(key, **kwargs)
            elif hasattr(self._loader, 'get_attribute_name'):
                # Для совместимости со старыми методами
                if 'attribute' in key:
                    return self._loader.get_attribute_name(key.split('.')[-1])
                elif 'skill' in key:
                    return self._loader.get_skill_name(key.split('.')[-1])
                else:
                    return default or key
            else:
                return default or key
        except:
            return default or key
    
    def get_language(self) -> str:
        """Получает текущий язык."""
        if hasattr(self._loader, 'get_language'):
            return self._loader.get_language()
        return "ru"
    
    def set_language(self, language: str) -> None:
        """Устанавливает язык."""
        if hasattr(self._loader, 'set_language'):
            self._loader.set_language(language)