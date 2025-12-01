"""
Data Validator - валидация игровых данных по схемам
"""
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List


class DataValidator:
    """Валидатор данных игры"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.schemas_path = Path(config_manager.get('paths.schemas', 'game/data/schemas'))
        self.logger = logging.getLogger(__name__)

        self.schemas: Dict[str, Dict] = {}
        self._load_schemas()

    def _load_schemas(self):
        """Загрузка всех схем валидации"""
        if not self.schemas_path.exists():
            self.logger.warning(f"Директория схем не найдена: {self.schemas_path}")
            return

        schema_files = self.schemas_path.glob('*.yaml')

        for schema_file in schema_files:
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    # Загружаем все схемы из файла (может быть несколько через ---)
                    schemas = list(yaml.safe_load_all(f))

                    for schema in schemas:
                        if schema:
                            # Получаем имя схемы из первого ключа
                            schema_name = list(schema.keys())[0] if schema else None
                            if schema_name:
                                self.schemas[schema_name] = schema[schema_name]
                                self.logger.debug(f"Загружена схема: {schema_name}")

            except Exception as e:
                self.logger.error(f"Ошибка загрузки схемы {schema_file}: {e}")

    def validate_race(self, race_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Валидация данных расы

        Args:
            race_data: Данные расы для проверки

        Returns:
            Кортеж (валидна, список ошибок)
        """
        return self._validate_data(race_data, 'race_schema')

    def validate_class(self, class_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Валидация данных класса

        Args:
            class_data: Данные класса для проверки

        Returns:
            Кортеж (валидна, список ошибок)
        """
        return self._validate_data(class_data, 'class_schema')

    def validate_character(self, character_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Валидация данных персонажа

        Args:
            character_data: Данные персонажа для проверки

        Returns:
            Кортеж (валидна, список ошибок)
        """
        return self._validate_data(character_data, 'character_schema')

    def validate_mod(self, mod_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Валидация модификации

        Args:
            mod_data: Данные мода для проверки

        Returns:
            Кортеж (валидна, список ошибок)
        """
        return self._validate_data(mod_data, 'mod_schema')

    def _validate_data(self, data: Dict[str, Any], schema_name: str) -> tuple[bool, List[str]]:
        """
        Базовая валидация данных по схеме

        Args:
            data: Данные для проверки
            schema_name: Имя схемы

        Returns:
            Кортеж (валидна, список ошибок)
        """
        errors = []

        if schema_name not in self.schemas:
            errors.append(f"Схема {schema_name} не найдена")
            return False, errors

        schema = self.schemas[schema_name]

        # Базовая валидация
        valid = self._validate_object(data, schema, errors, path="root")

        return valid and len(errors) == 0, errors

    def _validate_object(self, data: Any, schema: Dict, errors: List[str], path: str = "") -> bool:
        """
        Рекурсивная валидация объекта

        Args:
            data: Данные для проверки
            schema: Схема валидации
            errors: Список для накопления ошибок
            path: Текущий путь в структуре данных

        Returns:
            True если валидно
        """
        # Проверка типа
        expected_type = schema.get('type')

        if expected_type:
            if expected_type == 'object' and not isinstance(data, dict):
                errors.append(f"{path}: Ожидался объект, получен {type(data).__name__}")
                return False
            elif expected_type == 'array' and not isinstance(data, list):
                errors.append(f"{path}: Ожидался массив, получен {type(data).__name__}")
                return False
            elif expected_type == 'string' and not isinstance(data, str):
                errors.append(f"{path}: Ожидалась строка, получен {type(data).__name__}")
                return False
            elif expected_type == 'integer' and not isinstance(data, int):
                errors.append(f"{path}: Ожидалось число, получен {type(data).__name__}")
                return False

        # Проверка обязательных полей для объектов
        if isinstance(data, dict) and 'required' in schema:
            for required_field in schema['required']:
                if required_field not in data:
                    errors.append(f"{path}: Отсутствует обязательное поле '{required_field}'")

        # Проверка свойств объекта
        if isinstance(data, dict) and 'properties' in schema:
            for key, value in data.items():
                if key in schema['properties']:
                    field_schema = schema['properties'][key]
                    self._validate_object(
                        value,
                        field_schema,
                        errors,
                        f"{path}.{key}"
                    )

        # Проверка элементов массива
        if isinstance(data, list) and 'items' in schema:
            for idx, item in enumerate(data):
                self._validate_object(
                    item,
                    schema['items'],
                    errors,
                    f"{path}[{idx}]"
                )

        # Проверка минимума/максимума для чисел
        if isinstance(data, int):
            if 'minimum' in schema and data < schema['minimum']:
                errors.append(f"{path}: Значение {data} меньше минимума {schema['minimum']}")
            if 'maximum' in schema and data > schema['maximum']:
                errors.append(f"{path}: Значение {data} больше максимума {schema['maximum']}")

        # Проверка длины для строк
        if isinstance(data, str):
            if 'minLength' in schema and len(data) < schema['minLength']:
                errors.append(f"{path}: Длина строки {len(data)} меньше {schema['minLength']}")
            if 'maxLength' in schema and len(data) > schema['maxLength']:
                errors.append(f"{path}: Длина строки {len(data)} больше {schema['maxLength']}")

        # Проверка enum (допустимых значений)
        if 'enum' in schema:
            if data not in schema['enum']:
                errors.append(f"{path}: Значение '{data}' не входит в список допустимых: {schema['enum']}")

        return len(errors) == 0

    def validate_file(self, file_path: Path, schema_type: str) -> tuple[bool, List[str]]:
        """
        Валидация файла

        Args:
            file_path: Путь к файлу
            schema_type: Тип схемы (race, class, character, mod)

        Returns:
            Кортеж (валидна, список ошибок)
        """
        schema_map = {
            'race': 'race_schema',
            'class': 'class_schema',
            'character': 'character_schema',
            'mod': 'mod_schema'
        }

        if schema_type not in schema_map:
            return False, [f"Неизвестный тип схемы: {schema_type}"]

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif file_path.suffix == '.json':
                    import json
                    data = json.load(f)
                else:
                    return False, [f"Неподдерживаемый формат файла: {file_path.suffix}"]

            return self._validate_data(data, schema_map[schema_type])

        except Exception as e:
            return False, [f"Ошибка чтения файла: {e}"]

    def get_schema(self, schema_name: str) -> Optional[Dict]:
        """Получить схему по имени"""
        return self.schemas.get(schema_name)

    def list_schemas(self) -> List[str]:
        """Получить список всех загруженных схем"""
        return list(self.schemas.keys())