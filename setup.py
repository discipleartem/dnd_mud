#!/usr/bin/env python3
import sys
from cx_Freeze import setup, Executable
import os

# Определяем платформу и соответствующие настройки
is_windows = sys.platform.startswith("win")
is_mac = sys.platform.startswith("darwin")

# Определяем имя целевого файла в зависимости от платформы
target_name = "dnd_mud-windows.exe" if is_windows else "dnd_mud-linux"
build_dir = f"dist/dnd_mud-{'windows' if is_windows else 'linux'}"

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
            "include_files": [],
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