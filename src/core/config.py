"""Конфигурация игры."""

from pathlib import Path
from typing import Any

import yaml

from core.exceptions import ConfigError


class Config:
    """Класс конфигурации игры.
    
    Управляет настройками приложения с поддержкой YAML файла.
    Применяет принцип KISS - простая загрузка и сохранение.
    """

    def __init__(self) -> None:
        """Инициализация конфигурации."""
        self.config_path = Path("config.yaml")
        self.data_dir = Path("data")
        self.saves_dir = Path("saves")

        # Настройки по умолчанию (YAGNI - только необходимое)
        self.settings: dict[str, Any] = {
            "language": "ru",
            "theme": "default",
        }

        self.load()

    def load(self) -> None:
        """Загрузить конфигурацию из файла.
        
        Raises:
            ConfigError: При ошибке чтения или парсинга YAML
        """
        if not self.config_path.exists():
            self.save()
            return
            
        try:
            with open(self.config_path, encoding="utf-8") as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    self.settings.update(file_config)
        except yaml.YAMLError as e:
            raise ConfigError(f"Ошибка чтения конфигурации: {e}") from e
        except OSError as e:
            raise ConfigError(f"Ошибка доступа к файлу конфигурации: {e}") from e

    def save(self) -> None:
        """Сохранить конфигурацию в файл.
        
        Raises:
            ConfigError: При ошибке записи файла
        """
        try:
            # Создаем директорию если нужно
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.settings, 
                    f, 
                    default_flow_style=False,
                    allow_unicode=True, 
                    indent=2
                )
        except OSError as e:
            raise ConfigError(f"Ошибка сохранения конфигурации: {e}") from e

    def get(self, key: str, default: Any = None) -> Any:
        """Получить настройку по ключу.
        
        Args:
            key: Ключ настройки
            default: Значение по умолчанию
            
        Returns:
            Значение настройки или default
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Установить настройку.
        
        Args:
            key: Ключ настройки
            value: Новое значение
        """
        self.settings[key] = value
