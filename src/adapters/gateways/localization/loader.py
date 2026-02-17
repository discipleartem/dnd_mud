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
    
    def get_skill_info(self, skill_name: str) -> Dict[str, str]:
        """Возвращает локализованную информацию о навыке."""
        return self._data.get('skills', {}).get(skill_name, {})
    
    def get_skill_name(self, skill_name: str) -> str:
        """Возвращает локализованное название навыка."""
        info = self.get_skill_info(skill_name)
        return info.get('name', skill_name)
    
    def get_skill_description(self, skill_name: str) -> str:
        """Возвращает локализованное описание навыка."""
        info = self.get_skill_info(skill_name)
        return info.get('description', '')
    
    def get_saving_throw_info(self, save_name: str) -> Dict[str, str]:
        """Возвращает локализованную информацию о спасброске."""
        return self._data.get('saving_throws', {}).get(save_name, {})
    
    def get_saving_throw_name(self, save_name: str) -> str:
        """Возвращает локализованное название спасброска."""
        info = self.get_saving_throw_info(save_name)
        return info.get('name', save_name)
    
    def get_saving_throw_description(self, save_name: str) -> str:
        """Возвращает локализованное описание спасброска."""
        info = self.get_saving_throw_info(save_name)
        return info.get('description', '')
    
    def get_race_info(self, race_name: str) -> Dict[str, Any]:
        """Возвращает информацию о расе из YAML."""
        try:
            path = Path(__file__).parent.parent.parent.parent / "data" / "yaml" / "attributes" / "races.yaml"
            with open(path, 'r', encoding='utf-8') as file:
                races_data = yaml.safe_load(file)
                return races_data.get(race_name, {})
        except FileNotFoundError:
            print(f"Файл рас не найден, возвращаем пустые данные")
            return {}
    
    def get_race_name(self, race_name: str) -> str:
        """Возвращает локализованное название расы."""
        info = self.get_race_info(race_name)
        return info.get('name', race_name)
    
    def get_all_races(self) -> Dict[str, Any]:
        """Возвращает все доступные расы."""
        try:
            path = Path(__file__).parent.parent.parent.parent / "data" / "yaml" / "attributes" / "races.yaml"
            with open(path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print(f"Файл рас не найден, возвращаем пустой словарь")
            return {}
    
    def get_core_attributes(self) -> Dict[str, Any]:
        """Возвращает базовые атрибуты из конфигурации."""
        try:
            path = Path(__file__).parent.parent.parent.parent / "data" / "yaml" / "attributes" / "core_attributes.yaml"
            with open(path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print(f"Файл атрибутов не найден, возвращаем пустой словарь")
            return {}

# Глобальный экземпляр
localization = LocalizationLoader()