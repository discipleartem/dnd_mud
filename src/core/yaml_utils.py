"""Базовые утилиты для работы с YAML файлами в проекте.

Этот модуль предоставляет базовый класс для загрузки данных из YAML файлов,
избегая дублирования кода (принцип DRY) и следуя принципу KISS.
"""

from pathlib import Path
from typing import Any

import yaml


class BaseYamlLoader:
    """Базовый класс для загрузки данных из YAML файлов.

    Реализует паттерн Template Method для унификации процесса загрузки
    YAML данных в различных частях проекта. Следует принципу DRY,
    избегая дублирования кода загрузки.

    Пример использования:
        class RaceLoader(BaseYamlLoader):
            def __init__(self):
                super().__init__(Path("data/races.yaml"))

            def load_races(self):
                data = self._load_yaml_data()
                return data.get("races", {})
    """

    def __init__(self, data_path: Path) -> None:
        """Инициализация загрузчика.

        Args:
            data_path: Путь к YAML файлу с данными.
        """
        self.data_path = data_path

    def _load_yaml_data(self) -> dict[str, Any]:
        """Загрузить данные из YAML файла.

        Returns:
            Распарсенные данные из YAML.

        Raises:
            FileNotFoundError: Если файл не найден.
            yaml.YAMLError: При ошибке парсинга YAML.
        """
        with open(self.data_path, encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
