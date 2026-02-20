# src/core/localization/loader.py
import yaml
from pathlib import Path
from typing import Dict, List, Union, TypedDict, Optional


class LocalizationData(TypedDict):
    """Структура данных локализации."""

    attributes: Dict[str, Dict[str, str]]
    skills: Dict[str, Dict[str, str]]
    saving_throws: Dict[str, Dict[str, str]]
    races: Dict[str, Dict[str, Union[str, Dict[str, str], List[str]]]]


class RaceData(TypedDict):
    """Данные расы."""

    name: str
    description: str
    short_description: Optional[str]
    bonuses: Optional[Dict[str, int]]
    features: Optional[List[Dict[str, Union[str, int, bool]]]]


class CoreAttributes(TypedDict):
    """Базовые атрибуты."""

    base_attributes: Dict[str, Dict[str, Union[str, int]]]


class LocalizationLoader:
    """Загрузчик локализации из YAML файлов."""

    def __init__(self, locale: str = "ru"):
        self.locale = locale
        self._data: LocalizationData = {
            "attributes": {},
            "skills": {},
            "saving_throws": {},
            "races": {},
        }
        self._load_localization()

    def _load_localization(self) -> None:
        """Загружает локализацию из YAML файла."""
        try:
            path = (
                Path(__file__).parent.parent.parent.parent
                / "data"
                / "yaml"
                / "localization"
                / f"{self.locale}.yaml"
            )
            with open(path, "r", encoding="utf-8") as file:
                self._data = yaml.safe_load(file)
        except FileNotFoundError:
            print(
                f"Локализация {self.locale} не найдена, используем значения по умолчанию"
            )
            self._data = {
                "attributes": {},
                "skills": {},
                "saving_throws": {},
                "races": {},
            }

    def get_attribute_info(self, attribute_name: str) -> Dict[str, str]:
        """Возвращает локализованную информацию о характеристике."""
        result = self._data.get("attributes", {}).get(attribute_name, {})
        return result if isinstance(result, dict) else {}

    def get_attribute_name(self, attribute_name: str) -> str:
        """Возвращает локализованное название характеристики."""
        info = self.get_attribute_info(attribute_name)
        return info.get("name", attribute_name)

    def get_attribute_description(self, attribute_name: str) -> str:
        """Возвращает локализованное описание характеристики."""
        info = self.get_attribute_info(attribute_name)
        return info.get("description", "")

    def get_skill_info(self, skill_name: str) -> Dict[str, str]:
        """Возвращает локализованную информацию о навыке."""
        result = self._data.get("skills", {}).get(skill_name, {})
        return result if isinstance(result, dict) else {}

    def get_skill_name(self, skill_name: str) -> str:
        """Возвращает локализованное название навыка."""
        info = self.get_skill_info(skill_name)
        return info.get("name", skill_name)

    def get_skill_description(self, skill_name: str) -> str:
        """Возвращает локализованное описание навыка."""
        info = self.get_skill_info(skill_name)
        return info.get("description", "")

    def get_saving_throw_info(self, save_name: str) -> Dict[str, str]:
        """Возвращает локализованную информацию о спасброске."""
        result = self._data.get("saving_throws", {}).get(save_name, {})
        return result if isinstance(result, dict) else {}

    def get_saving_throw_name(self, save_name: str) -> str:
        """Возвращает локализованное название спасброска."""
        info = self.get_saving_throw_info(save_name)
        return info.get("name", save_name)

    def get_saving_throw_description(self, save_name: str) -> str:
        """Возвращает локализованное описание спасброска."""
        info = self.get_saving_throw_info(save_name)
        return info.get("description", "")

    def get_race_info(self, race_name: str) -> RaceData:
        """Возвращает информацию о расе из YAML."""
        try:
            path = (
                Path(__file__).parent.parent.parent.parent
                / "data"
                / "yaml"
                / "races"
                / "races.yaml"
            )
            with open(path, "r", encoding="utf-8") as file:
                races_data = yaml.safe_load(file)
                race_data = races_data.get(race_name, {})
                # Преобразуем в RaceData с полями по умолчанию
                return {
                    "name": race_data.get("name", race_name),
                    "description": race_data.get("description", ""),
                    "short_description": race_data.get("short_description"),
                    "bonuses": race_data.get("bonuses"),
                    "features": race_data.get("features"),
                }
        except FileNotFoundError:
            print("Файл рас не найден, возвращаем пустые данные")
            return {
                "name": race_name,
                "description": "",
                "short_description": None,
                "bonuses": None,
                "features": None,
            }

    def get_race_name(self, race_name: str) -> str:
        """Возвращает локализованное название расы."""
        info = self.get_race_info(race_name)
        return info.get("name", race_name)

    def get_all_races(self) -> Dict[str, RaceData]:
        """Возвращает все доступные расы."""
        try:
            path = (
                Path(__file__).parent.parent.parent.parent
                / "data"
                / "yaml"
                / "races"
                / "races.yaml"
            )
            with open(path, "r", encoding="utf-8") as file:
                races_data = yaml.safe_load(file) or {}
                # Преобразуем все расы в RaceData
                result: Dict[str, RaceData] = {}
                for race_name, race_data in races_data.items():
                    if isinstance(race_data, dict):
                        result[race_name] = {
                            "name": race_data.get("name", race_name),
                            "description": race_data.get("description", ""),
                            "short_description": race_data.get("short_description"),
                            "bonuses": race_data.get("bonuses"),
                            "features": race_data.get("features"),
                        }
                return result
        except FileNotFoundError:
            print("Файл рас не найден, возвращаем пустой словарь")
            return {}

    def get_core_attributes(self) -> CoreAttributes:
        """Возвращает базовые атрибуты из конфигурации."""
        try:
            path = (
                Path(__file__).parent.parent.parent.parent
                / "data"
                / "yaml"
                / "attributes"
                / "core_attributes.yaml"
            )
            with open(path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if data and "base_attributes" in data:
                    return {"base_attributes": data["base_attributes"]}
                else:
                    return {"base_attributes": {}}
        except FileNotFoundError:
            print("Файл атрибутов не найден, возвращаем пустой словарь")
            return {"base_attributes": {}}


# Глобальный экземпляр
localization = LocalizationLoader()
