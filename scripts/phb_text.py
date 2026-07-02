#!/usr/bin/env python3
"""Очистка и структурирование текста PHB для markdown-пересказа."""

from __future__ import annotations

import re


def paragraphs(text: str) -> list[str]:
    """Разбивает текст на абзацы."""
    parts = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    return parts


def to_bullets(text: str, max_items: int = 12) -> list[str]:
    """Преобразует абзацы в маркированный список (сжатый пересказ)."""
    items: list[str] = []
    for para in paragraphs(text):
        cleaned = re.sub(r"\s+", " ", para)
        if len(cleaned) < 20:
            continue
        if len(cleaned) > 400:
            sentences = re.split(r"(?<=[.!?])\s+", cleaned)
            for sent in sentences[:3]:
                if len(sent) > 15:
                    items.append(sent)
        else:
            items.append(cleaned)
        if len(items) >= max_items:
            break
    return items


def strip_headers(text: str) -> str:
    """Убирает повторяющиеся заголовки глав из извлечённого текста."""
    lines = text.splitlines()
    out: list[str] = []
    skip_patterns = (
        r"^ГЛАВА \d+",
        r"^ЧАСТЬ \d+",
        r"^ПРИЛОЖЕНИЕ",
        r"^ВВЕДЕНИЕ$",
        r"^СОДЕРЖАНИЕ$",
    )
    for line in lines:
        if any(
            re.match(p, line.strip(), re.IGNORECASE) for p in skip_patterns
        ):
            continue
        out.append(line)
    return "\n".join(out)


def summarize_section(text: str, max_bullets: int = 10) -> str:
    """Формирует markdown-секцию «Для игроков» из сырого текста."""
    cleaned = strip_headers(text)
    bullets = to_bullets(cleaned, max_items=max_bullets)
    if not bullets:
        return "_См. PHB PDF для полного текста._\n"
    return "\n".join(f"- {b}" for b in bullets) + "\n"


def extract_tables_from_text(text: str) -> list[str]:
    """Ищет строки с числовыми таблицами (упрощённо)."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    numeric = [ln for ln in lines if re.search(r"\d", ln) and len(ln) < 80]
    return numeric[:20]
