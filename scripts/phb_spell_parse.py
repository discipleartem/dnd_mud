"""Извлечение описаний заклинаний из локального PHB PDF (pdftotext)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PDF = ROOT / "docs" / "PHB_ D&D_2023 RUS.pdf"

SCHOOL_RU_TO_EN: dict[str, str] = {
    "воплощение": "evocation",
    "ограждение": "abjuration",
    "иллюзия": "illusion",
    "некромантия": "necromancy",
    "очарование": "enchantment",
    "преобразование": "transmutation",
    "прорицание": "divination",
    "призыв": "conjuration",
}

_LEVEL_LINE_RE = re.compile(
    r"^((?:\d+ уровень)|заговор),\s*(.+)$",
    re.IGNORECASE,
)
_TITLE_RE = re.compile(r"^[А-ЯЁ0-9][А-ЯЁ0-9 /\-–—]+$")
_SKIP_TITLES = frozenset(
    {
        "ЧАСТЬ 3 : ЗАКЛИНАНИЯ",
        "ОПИСАНИЕ ЗАКЛИНАНИЙ",
    }
)


def extract_pdf_text(pdf_path: Path | None = None) -> str:
    path = pdf_path or DEFAULT_PDF
    if not path.is_file():
        return ""
    proc = subprocess.run(
        ["pdftotext", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def _normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().upper())


def _is_title_line(line: str) -> bool:
    s = line.strip()
    if not s or s in _SKIP_TITLES:
        return False
    if "ЧАСТЬ " in s:
        return False
    if not _TITLE_RE.match(s):
        return False
    letters = [c for c in s if c.isalpha()]
    if len(letters) < 3:
        return False
    upper = sum(1 for c in letters if c.upper() == c)
    return upper / len(letters) >= 0.85


def _parse_level_line(line: str) -> tuple[int | str, str, str] | None:
    m = _LEVEL_LINE_RE.match(line.strip())
    if not m:
        return None
    level_raw, school_raw = m.group(1).lower(), m.group(2).strip().lower()
    if level_raw == "заговор":
        level: int | str = 0
        level_label = "Заговор"
    else:
        level = int(level_raw.split()[0])
        level_label = f"{level} уровень"
    school_en = SCHOOL_RU_TO_EN.get(school_raw, school_raw)
    school_label = school_raw.capitalize()
    return level, level_label, f"{school_label} (`{school_en}`)"


_DURATION_PREFIXES = (
    "Концентрация",
    "Мгновенная",
    "1 раунд",
    "1 минута",
    "10 минут",
    "1 час",
    "8 часов",
    "24 часа",
    "До рассеивания",
    "Специальная",
)


def _split_merged_field(value: str) -> tuple[str, list[str]]:
    """Отделяет эффект, склеенный pdftotext с полем длительности/компонентов."""
    extra: list[str] = []
    if "На больших уровнях:" in value:
        before, after = value.split("На больших уровнях:", 1)
        value = before.strip()
        extra.append(f"На больших уровнях:{after.strip()}")
    m = re.match(
        r"^(Мгновенная|Концентрация(?:, вплоть до [^А-ЯЁ]+)?|"
        r"1 раунд|1 минута|10 минут|1 час|8 часов|24 часа|"
        r"До рассеивания|Специальная)\s+([А-ЯЁ].+)$",
        value,
    )
    if m:
        return m.group(1).strip(), extra + [m.group(2).strip()]
    for prefix in _DURATION_PREFIXES:
        if value.startswith(prefix):
            tail = value[len(prefix) :].strip()
            if len(tail) > 15 and tail[0].isupper():
                return prefix, extra + [tail]
            break
    return value, extra


def _parse_parameters(lines: list[str]) -> tuple[dict[str, Any], int]:
    params: dict[str, Any] = {}
    idx = 0
    keys = {
        "Время накладывания:": "casting_time",
        "Дистанция:": "range",
        "Компоненты:": "components",
        "Длительность:": "duration",
    }
    while idx < len(lines):
        line = lines[idx].strip()
        matched = False
        for prefix, key in keys.items():
            if line.startswith(prefix):
                value = line[len(prefix) :].strip()
                idx += 1
                while idx < len(lines):
                    nxt = lines[idx].strip()
                    if not nxt or any(nxt.startswith(p) for p in keys):
                        break
                    if _is_title_line(nxt) and idx + 1 < len(lines):
                        if _parse_level_line(lines[idx + 1].strip()):
                            break
                    value = f"{value} {nxt}".strip()
                    idx += 1
                params[key] = value
                matched = True
                break
        if not matched:
            break
    merged_extra: list[str] = []
    for key in ("duration", "components", "range"):
        if key in params:
            cleaned, extra = _split_merged_field(params[key])
            params[key] = cleaned
            merged_extra.extend(extra)
    params["_merged_effect"] = merged_extra
    return params, idx


def _split_effect_and_higher(
    body_lines: list[str],
) -> tuple[list[str], str | None]:
    effect_parts: list[str] = []
    higher_parts: list[str] = []
    for line in body_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if "На больших уровнях:" in stripped:
            before, after = stripped.split("На больших уровнях:", 1)
            if before.strip():
                effect_parts.append(before.strip())
            if after.strip():
                higher_parts.append(after.strip())
            continue
        effect_parts.append(stripped)
    higher = (
        f"На больших уровнях: {' '.join(higher_parts)}"
        if higher_parts
        else None
    )
    effect_text = " ".join(effect_parts)
    return ([effect_text] if effect_text else []), higher


def parse_spell_descriptions(text: str) -> dict[str, dict[str, Any]]:
    marker = "ОПИСАНИЕ ЗАКЛИНАНИЙ"
    pos = text.find(marker)
    if pos < 0:
        return {}
    section = text[pos:]
    lines = section.splitlines()
    spells: dict[str, dict[str, Any]] = {}
    i = 0
    while i < len(lines) - 1:
        title_line = lines[i].strip()
        if not _is_title_line(title_line):
            i += 1
            continue
        level_line = lines[i + 1].strip()
        level_info = _parse_level_line(level_line)
        if not level_info:
            i += 1
            continue
        level, level_label, school_label = level_info
        i += 2
        param_lines = lines[i:]
        params, offset = _parse_parameters(param_lines)
        raw_merged = params.pop("_merged_effect", [])
        merged_effect: list[str] = (
            raw_merged if isinstance(raw_merged, list) else []
        )
        i += offset
        body_lines: list[str] = list(merged_effect)
        while i < len(lines):
            s = lines[i].strip()
            if _is_title_line(s) and i + 1 < len(lines):
                if _parse_level_line(lines[i + 1].strip()):
                    break
            if s.startswith("ЧАСТЬ 3"):
                break
            body_lines.append(lines[i])
            i += 1
        effect_lines, higher = _split_effect_and_higher(body_lines)
        key = _normalize_title(title_line)
        spells[key] = {
            "title": (
                title_line.title() if title_line.isupper() else title_line
            ),
            "title_raw": title_line,
            "level": level,
            "level_label": level_label,
            "school_label": school_label,
            "casting_time": params.get("casting_time", "—"),
            "range": params.get("range", "—"),
            "components": params.get("components", "—"),
            "duration": params.get("duration", "—"),
            "effect_lines": effect_lines,
            "higher_levels": higher,
        }
    return spells


def load_spells_index(rules_dir: Path) -> dict[str, dict[str, Any]]:
    path = rules_dir / "_index" / "spells.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    spells = data.get("spells", {})
    return spells if isinstance(spells, dict) else {}


def map_parsed_to_ids(
    parsed: dict[str, dict[str, Any]],
    spells_index: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    by_title: dict[str, str] = {}
    for spell_id, meta in spells_index.items():
        ru = str(meta.get("ru", ""))
        by_title[_normalize_title(ru)] = spell_id
    mapped: dict[str, dict[str, Any]] = {}
    for title_key, payload in parsed.items():
        mapped_id = by_title.get(title_key)
        if mapped_id:
            mapped[mapped_id] = payload
    return mapped


def effect_to_bullets(effect_lines: list[str]) -> str:
    if not effect_lines:
        return "_См. PHB PDF._\n"
    text = " ".join(effect_lines)
    # Разбиваем на предложения для читаемых буллетов
    chunks = re.split(r"(?<=[.!?])\s+", text)
    parts = [f"- {chunk.strip()}" for chunk in chunks if chunk.strip()]
    return "\n".join(parts) + "\n"
