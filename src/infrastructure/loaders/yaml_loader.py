"""Реализация YAML загрузчика с кэшированием.

Улучшенная реализация загрузчика YAML данных с поддержкой кэширования
и обработки ошибок согласно принципам Clean Architecture.
"""

import threading
from pathlib import Path
from typing import Any

import yaml

from src.interfaces.loaders import ICacheableLoader, IYamlLoader, LoaderError


class YamlLoader(IYamlLoader, ICacheableLoader[dict[str, Any]]):
    """Реализация загрузчика YAML данных с кэшированием.

    Следует принципу Single Responsibility - только загрузка YAML.
    Поддерживает кэширование для повышения производительности.
    """

    def __init__(self, enable_cache: bool = True):
        """Инициализация загрузчика.

        Args:
            enable_cache: Включить кэширование результатов
        """
        self._enable_cache = enable_cache
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_lock = threading.RLock()

    def load(self, source: Any) -> dict[str, Any]:
        """Загрузить данные из источника.

        Args:
            source: Источник данных (Path или строка)

        Returns:
            Загруженные данные

        Raises:
            LoaderError: При ошибке загрузки
        """
        if isinstance(source, Path):
            return self.load_from_file(source)
        elif isinstance(source, str):
            if source.strip().startswith(("{", "[", '"', "'")):
                return self.load_from_string(source)
            else:
                return self.load_from_file(Path(source))
        else:
            raise LoaderError(
                f"Неподдерживаемый тип источника: {type(source)}"
            )

    def load_from_file(self, file_path: Path) -> dict[str, Any]:
        """Загрузить данные из YAML файла.

        Args:
            file_path: Путь к YAML файлу

        Returns:
            Распарсенные данные

        Raises:
            FileNotFoundError: Если файл не найден
            LoaderError: При ошибке парсинга YAML
        """
        if not isinstance(file_path, Path):
            raise LoaderError(f"Ожидается Path, получено: {type(file_path)}")

        # Проверяем кэш
        cache_key = str(file_path.absolute())
        if self._enable_cache and self.is_cached(cache_key):
            with self._cache_lock:
                return self._cache[cache_key].copy()

        try:
            with open(file_path, encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}

            # Сохраняем в кэш
            if self._enable_cache:
                with self._cache_lock:
                    self._cache[cache_key] = data.copy()

            return data

        except FileNotFoundError as e:
            raise LoaderError(f"Файл не найден: {file_path}") from e
        except yaml.YAMLError as e:
            raise LoaderError(
                f"Ошибка парсинга YAML в файле {file_path}: {e}"
            ) from e
        except UnicodeDecodeError as e:
            raise LoaderError(
                f"Ошибка кодировки файла {file_path}: {e}"
            ) from e
        except Exception as e:
            raise LoaderError(
                f"Неизвестная ошибка при загрузке {file_path}: {e}"
            ) from e

    def load_from_string(self, yaml_string: str) -> dict[str, Any]:
        """Загрузить данные из YAML строки.

        Args:
            yaml_string: YAML строка

        Returns:
            Распарсенные данные

        Raises:
            LoaderError: При ошибке парсинга YAML
        """
        if not isinstance(yaml_string, str):
            raise LoaderError(
                f"Ожидается строка, получено: {type(yaml_string)}"
            )

        # Проверяем кэш
        cache_key = f"string:{hash(yaml_string)}"
        if self._enable_cache and self.is_cached(cache_key):
            with self._cache_lock:
                return self._cache[cache_key].copy()

        try:
            data = yaml.safe_load(yaml_string) or {}

            # Сохраняем в кэш
            if self._enable_cache:
                with self._cache_lock:
                    self._cache[cache_key] = data.copy()

            return data

        except yaml.YAMLError as e:
            raise LoaderError(f"Ошибка парсинга YAML строки: {e}") from e
        except Exception as e:
            raise LoaderError(
                f"Неизвестная ошибка при парсинге YAML: {e}"
            ) from e

    def clear_cache(self) -> None:
        """Очистить кэш загрузчика."""
        with self._cache_lock:
            self._cache.clear()

    def is_cached(self, source: Any) -> bool:
        """Проверить наличие данных в кэше.

        Args:
            source: Источник данных

        Returns:
            True если данные в кэше
        """
        if not self._enable_cache:
            return False

        cache_key = (
            str(source)
            if isinstance(source, (str, Path))
            else f"string:{hash(str(source))}"
        )

        with self._cache_lock:
            return cache_key in self._cache

    def get_cache_stats(self) -> dict[str, Any]:
        """Получить статистику кэша.

        Returns:
            Статистика использования кэша
        """
        with self._cache_lock:
            return {
                "enabled": self._enable_cache,
                "entries": len(self._cache),
                "keys": list(self._cache.keys()),
            }

    def preload_file(self, file_path: Path) -> None:
        """Предзагрузить файл в кэш.

        Args:
            file_path: Путь к файлу для предзагрузки
        """
        if self._enable_cache:
            self.load_from_file(file_path)

    def preload_files(self, file_paths: list[Path]) -> None:
        """Предзагрузить несколько файлов в кэш.

        Args:
            file_paths: Список путей к файлам
        """
        if self._enable_cache:
            for file_path in file_paths:
                try:
                    self.preload_file(file_path)
                except LoaderError:
                    # Игнорируем ошибки при предзагрузке
                    pass


class ValidatedYamlLoader(YamlLoader):
    """YAML загрузчик с валидацией схемы.

    Расширяет базовый загрузчик возможностью валидации данных
    по предоставленной схеме.
    """

    def __init__(
        self, schema: dict[str, Any] | None = None, enable_cache: bool = True
    ):
        """Инициализация загрузчика со схемой.

        Args:
            schema: Схема для валидации (опционально)
            enable_cache: Включить кэширование
        """
        super().__init__(enable_cache=enable_cache)
        self._schema = schema

    def load_from_file(self, file_path: Path) -> dict[str, Any]:
        """Загрузить и валидировать данные из YAML файла.

        Args:
            file_path: Путь к YAML файлу

        Returns:
            Валидированные данные
        """
        data = super().load_from_file(file_path)

        if self._schema:
            self._validate_data(data, str(file_path))

        return data

    def load_from_string(self, yaml_string: str) -> dict[str, Any]:
        """Загрузить и валидировать данные из YAML строки.

        Args:
            yaml_string: YAML строка

        Returns:
            Валидированные данные
        """
        data = super().load_from_string(yaml_string)

        if self._schema:
            self._validate_data(data, "YAML строка")

        return data

    def _validate_data(self, data: dict[str, Any], source: str) -> None:
        """Валидировать данные по схеме.

        Args:
            data: Данные для валидации
            source: Источник данных для ошибок

        Raises:
            LoaderError: Если данные не соответствуют схеме
        """
        # Простая валидация - можно расширить
        if not isinstance(data, dict):
            raise LoaderError(f"Данные должны быть словарем: {source}")

        # Проверка обязательных полей
        required_fields = (self._schema or {}).get("required", [])
        for field in required_fields:
            if field not in data:
                raise LoaderError(
                    f"Обязательное поле отсутствует: {field} в {source}"
                )

        # Проверка типов полей
        field_types = (self._schema or {}).get("types", {})
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                raise LoaderError(
                    f"Поле {field} должно быть типа {expected_type.__name__}, "
                    f"получено {type(data[field]).__name__} в {source}"
                )
