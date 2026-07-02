#!/usr/bin/env python3
"""Извлечение текста из локального PHB PDF (dev-tool, не runtime MUD)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PDF = ROOT / "docs" / "PHB_ D&D_2023 RUS.pdf"
BUILD_DIR = ROOT / "build" / "phb_sections"


def pdf_path(custom: Path | None = None) -> Path:
    """Возвращает путь к PDF или бросает FileNotFoundError."""
    path = custom or DEFAULT_PDF
    if not path.is_file():
        msg = f"PHB PDF не найден: {path}"
        raise FileNotFoundError(msg)
    return path


def extract_pages(pdf: Path, start: int, end: int) -> str:
    """Извлекает текст страниц start..end через pdftotext."""
    result = subprocess.run(
        ["pdftotext", "-f", str(start), "-l", str(end), str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return normalize_text(result.stdout)


def extract_full(pdf: Path) -> str:
    """Извлекает весь PDF одним вызовом."""
    result = subprocess.run(
        ["pdftotext", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return normalize_text(result.stdout)


def normalize_text(text: str) -> str:
    """Нормализует пробелы и переносы после pdftotext."""
    text = text.replace("\f", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def write_section(chapter: str, section_id: str, content: str) -> Path:
    """Сохраняет сырой текст раздела в build/ (gitignored)."""
    out_dir = BUILD_DIR / chapter
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{section_id}.txt"
    path.write_text(content, encoding="utf-8")
    return path


def extract_range_to_file(
    chapter: str,
    section_id: str,
    start: int,
    end: int,
    pdf: Path | None = None,
) -> Path:
    """Извлекает диапазон страниц и пишет в build/phb_sections/."""
    content = extract_pages(pdf_path(pdf), start, end)
    return write_section(chapter, section_id, content)
