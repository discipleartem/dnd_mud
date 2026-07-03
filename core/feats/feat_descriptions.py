"""Текстовые описания черт из YAML."""

import re
from typing import Any

_BENEFITS_MARKER = re.compile(
    r"(?:,\s*)?(?:и\s+)?(?:вы\s+)?(?:дающие\s+)?"
    r"получаете\s+следующие\s+преимущества",
    re.IGNORECASE,
)
_BENEFITS_LINE_MARKER = re.compile(
    r"получаете\s+следующие\s+преимущества|дающие\s+следующие\s+преимущества",
    re.IGNORECASE,
)


def _collapse_whitespace(text: str) -> str:
    """Схлопнуть пробелы и переносы для поиска маркера в description_full."""
    return re.sub(r"\s+", " ", text.strip())


def feat_intro_from_full(description_full: str) -> str:
    """Вводный текст PHB до «…получаете следующие преимущества:»."""
    normalized = _collapse_whitespace(description_full)
    match = _BENEFITS_MARKER.search(normalized)
    if not match:
        return ""
    intro = normalized[: match.start()].strip().rstrip(",").strip()
    return intro


def feat_benefit_lines_from_full(description_full: str) -> list[str]:
    """Строки преимуществ (маркированный список) из description_full."""
    lines: list[str] = []
    for raw in description_full.strip().splitlines():
        stripped = raw.strip()
        if not stripped.startswith("•"):
            continue
        if _BENEFITS_LINE_MARKER.search(stripped):
            continue
        lines.append(stripped)
    return lines


def feat_summary_description(feat: dict[str, Any]) -> str:
    """Краткое описание для списка выбора."""
    short = feat.get("description_short")
    if isinstance(short, str) and short.strip():
        return short.strip()
    full = feat.get("description_full")
    if isinstance(full, str) and full.strip():
        intro = feat_intro_from_full(full)
        if intro:
            return intro
    raw = feat.get("description", "")
    return str(raw).strip()


def feat_full_description_lines(feat: dict[str, Any]) -> list[str]:
    """Строки детального описания (преимущества) для экрана подтверждения."""
    full = feat.get("description_full")
    if isinstance(full, str) and full.strip():
        benefits = feat_benefit_lines_from_full(full)
        if benefits:
            return benefits
        return [
            line.rstrip() for line in full.strip().splitlines() if line.strip()
        ]
    if isinstance(full, list):
        return [str(line) for line in full if str(line).strip()]

    lines: list[str] = []
    raw_grants = feat.get("grants", [])
    if isinstance(raw_grants, list):
        for grant in raw_grants:
            if not isinstance(grant, dict):
                continue
            gdesc = str(grant.get("description", "")).strip()
            if not gdesc:
                continue
            gname = str(grant.get("name", "")).strip()
            if gname and gname not in gdesc:
                lines.append(f"• {gname}: {gdesc}")
            else:
                lines.append(f"• {gdesc}")
    if not lines:
        summary = str(feat.get("description", "")).strip()
        if summary:
            lines.append(summary)
    return lines
