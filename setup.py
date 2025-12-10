#!/usr/bin/env python3
import sys
from cx_Freeze import setup, Executable
import os
from pathlib import Path

# Определяем платформу и соответствующие настройки
is_windows = sys.platform.startswith("win")
is_mac = sys.platform.startswith("darwin")

# Определяем имя целевого файла в зависимости от платформы
target_name = "dnd_mud-windows.exe" if is_windows else "dnd_mud-linux"
build_dir = f"dist/dnd_mud-{'windows' if is_windows else 'linux'}"

# Подготовка файлов для включения в сборку
include_files = []

# Получаем абсолютный путь к корню проекта
project_root = Path(__file__).parent.absolute()

# Включаем директорию data/yaml (конфигурации и базовая локализация)
yaml_dir = project_root / "data" / "yaml"
if yaml_dir.exists():
    include_files.append((str(yaml_dir), "data/yaml"))

# Включаем директорию data/mods (модификации)
mods_dir = project_root / "data" / "mods"
if mods_dir.exists():
    include_files.append((str(mods_dir), "data/mods"))

# Включаем директорию data/adventures (приключения, если существует)
adventures_dir = project_root / "data" / "adventures"
if adventures_dir.exists():
    include_files.append((str(adventures_dir), "data/adventures"))

# Создаём директорию data/saves (будет создана при первом запуске, но включаем структуру)
saves_dir = Path("data/saves")
saves_dir.mkdir(parents=True, exist_ok=True)

# Основные настройки
setup(
    name="DND MUD",
    version="1.0.0",
    description="DND MUD Game",
    author="Tomas",
    options={
        "build_exe": {
            "build_exe": build_dir,
            "packages": [],
            "excludes": ["tkinter", "unittest", "matplotlib", "numpy"],
            "include_files": include_files,
            "optimize": 1
        }
    },
    executables=[
        Executable(
            "src/main.py",
            target_name=target_name,
            base=None
        )
    ]
)