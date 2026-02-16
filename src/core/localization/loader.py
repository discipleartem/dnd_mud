# src/core/localization/loader.py
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class LocalizationLoader:
    """Загрузчик локализации из YAML файлов."""
    
    def __init__(self, locale: str = "ru"):
        self.locale = locale
        self._data: Dict[str, Any] = {}
        self._load_localization()
    
    def _load_localization(self) -> None:
        """Загружает локализацию из YAML файла."""
        try:
            path = Path(__file__).parent.parent.parent.parent / "data" / "yaml" / "localization" / f"{self.locale}.yaml"
            with open(path, 'r', encoding='utf-8') as file:
                self._data = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Локализация {self.locale} не найдена, используем значения по умолчанию")
            self._data = {}
    
    def get_attribute_info(self, attribute_name: str) -> Dict[str, str]:
        """Возвращает локализованную информацию о характеристике."""
        return self._data.get('attributes', {}).get(attribute_name, {})
    
    def get_attribute_name(self, attribute_name: str) -> str:
        """Возвращает локализованное название характеристики."""
        info = self.get_attribute_info(attribute_name)
        return info.get('name', attribute_name)
    
    def get_attribute_description(self, attribute_name: str) -> str:
        """Возвращает локализованное описание характеристики."""
        info = self.get_attribute_info(attribute_name)
        return info.get('description', '')

# Глобальный экземпляр
localization = LocalizationLoader()