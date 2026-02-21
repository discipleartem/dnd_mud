"""Репозиторий размеров.

Находится в слое Frameworks, так как зависит от YAML файлов.
"""

import yaml
from typing import Dict
from pathlib import Path


class SizeRepository:
    """Репозиторий размеров."""
    
    def __init__(self, data_dir: str = "data") -> None:
        self._data_dir = Path(data_dir)
        self._size_values = self._load_sizes()
    
    def _load_sizes(self) -> Dict[str, str]:
        """Загрузить названия размеров."""
        try:
            with open(self._data_dir / "sizes.yaml", 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f) or {}
                return raw_data.get("size_values", {})
        except FileNotFoundError:
            print("❌ Файл sizes.yaml не найден")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Ошибка чтения YAML sizes.yaml: {e}")
            return {}
    
    def get_size_name(self, size_key: str) -> str:
        """Получить человекочитаемое название размера."""
        return self._size_values.get(size_key, size_key)