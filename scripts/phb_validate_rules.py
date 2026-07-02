#!/usr/bin/env python3
"""Валидация структуры docs/rules/ против toc.yaml."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "docs" / "rules"
TOC_PATH = RULES_DIR / "toc.yaml"


def validate_toc() -> list[str]:
    """Проверяет, что все записи toc.yaml указывают на существующие файлы."""
    errors: list[str] = []
    if not TOC_PATH.is_file():
        errors.append(f"Отсутствует {TOC_PATH}")
        return errors
    data = yaml.safe_load(TOC_PATH.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    for entry in entries:
        file_rel = entry.get("file")
        if not file_rel:
            errors.append(f"Запись без file: {entry}")
            continue
        path = RULES_DIR / file_rel
        if not path.is_file():
            errors.append(f"Файл не найден: {path}")
    return errors


def validate_spell_indexes() -> list[str]:
    """Проверяет наличие индексов заклинаний."""
    errors: list[str] = []
    for name in ("_index-by-level.md", "_index-by-school.md"):
        path = RULES_DIR / "spells" / name
        if not path.is_file():
            errors.append(f"Отсутствует индекс: {path}")
    return errors


def validate_min_counts() -> list[str]:
    """Минимальные ожидания по количеству файлов."""
    errors: list[str] = []
    expectations = {
        "races": (RULES_DIR / "races", 9),
        "classes": (RULES_DIR / "classes", 12),
        "backgrounds": (RULES_DIR / "backgrounds", 13),
        "spells": (RULES_DIR / "spells", 200),
        "appendices": (RULES_DIR / "appendices", 5),
    }
    for label, (dir_path, minimum) in expectations.items():
        if not dir_path.is_dir():
            errors.append(f"Каталог отсутствует: {dir_path}")
            continue
        count = len(list(dir_path.glob("*.md")))
        if count < minimum:
            errors.append(f"{label}: {count} файлов, ожидается >= {minimum}")
    return errors


def main() -> int:
    """CLI entry point."""
    all_errors = (
        validate_toc() + validate_spell_indexes() + validate_min_counts()
    )
    if all_errors:
        for err in all_errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print("phb_validate_rules: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
