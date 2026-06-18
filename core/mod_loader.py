"""Сканирование и управление модификациями (модами).

Моды — это YAML-файлы в папке mods/.
Состояние (включён/выключен) хранится в database/mods_state.yaml.
"""

from pathlib import Path

import yaml

MODS_DIR = Path("mods")
MODS_STATE_FILE = Path("database/mods_state.yaml")


def scan_mods() -> list[dict]:
    """Найти все YAML-файлы модов в папке mods/.

    Returns:
        Список словарей с данными каждого мода
    """
    if not MODS_DIR.exists() or not MODS_DIR.is_dir():
        return []

    mods = []
    for yaml_file in sorted(MODS_DIR.glob("*.yaml")):
        try:
            with open(yaml_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            # Проверяем, что это валидный мод (есть поле "name")
            if data and isinstance(data, dict) and data.get("name"):
                data["_file"] = str(yaml_file)
                mods.append(data)
        except (yaml.YAMLError, OSError):
            continue

    return mods


def load_mods_state() -> dict:
    """Загрузить состояния включения/выключения модов.

    Returns:
        Словарь вида {"имя_мода": True/False}
    """
    if not MODS_STATE_FILE.exists():
        return {}

    try:
        with open(MODS_STATE_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("mods", {})
    except (yaml.YAMLError, OSError):
        return {}


def save_mods_state(state: dict) -> None:
    """Сохранить состояния включения/выключения модов.

    Args:
        state: Словарь вида {"имя_мода": True/False}
    """
    MODS_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MODS_STATE_FILE, "w", encoding="utf-8") as f:
        yaml.dump({"mods": state}, f, allow_unicode=True, default_flow_style=False)


def toggle_mod(mod_name: str) -> bool:
    """Переключить мод (включить/выключить).

    Args:
        mod_name: Имя мода

    Returns:
        Новое состояние: True — включён, False — выключен
    """
    state = load_mods_state()
    state[mod_name] = not state.get(mod_name, False)
    save_mods_state(state)
    return state[mod_name]


def is_mod_enabled(mod_name: str) -> bool:
    """Проверить, включён ли мод.

    Args:
        mod_name: Имя мода

    Returns:
        True если мод включён
    """
    state = load_mods_state()
    return state.get(mod_name, False)