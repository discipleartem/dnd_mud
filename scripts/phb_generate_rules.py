#!/usr/bin/env python3
"""Генерация docs/rules/ из локального PHB PDF (пересказ)."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml
from phb_data import (
    APPENDICES,
    BACKGROUNDS,
    CHAPTER_PRESERVE,
    CHAPTERS,
    CLASS_HEADINGS,
    CLASSES,
    RACE_HEADINGS,
    RACES,
    SCHOOL_RU_TO_EN,
    SPELL_RU_TO_EN,
    EntityRef,
)
from phb_extract import extract_pages, pdf_path, write_section
from phb_text import summarize_section, to_bullets

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "docs" / "rules"


@dataclass
class SpellEntry:
    """Распарсенное заклинание из PDF."""

    name_ru: str
    level_line: str
    level: int
    school_ru: str
    casting_time: str
    range_: str
    components: str
    duration: str
    body: str
    higher_levels: str


def slugify_ru(name: str) -> str:
    """Транслитерация RU названия в slug, если нет в словаре."""
    trans = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }
    lower = name.lower().replace("ё", "е")
    parts: list[str] = []
    for ch in lower:
        if ch in trans:
            parts.append(trans[ch])
        elif ch.isalnum():
            parts.append(ch)
        else:
            parts.append("_")
    slug = re.sub(r"_+", "_", "".join(parts)).strip("_")
    return slug or "spell"


def spell_slug(name_ru: str) -> str:
    """EN slug заклинания."""
    key = name_ru.upper().strip()
    mapped = SPELL_RU_TO_EN.get(key)
    if mapped is not None:
        return str(mapped)
    return slugify_ru(name_ru)


def _truncate_at_next_heading(text: str) -> str:
    """Обрезает текст при следующем заголовке или номере страницы."""
    lines = text.splitlines()
    kept: list[str] = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^\d{1,3}$", stripped):
            break
        if re.match(r"^ЧАСТЬ \d+", stripped):
            break
        if (
            re.match(r"^[А-ЯЁ][А-ЯЁ \-–]{3,}$", stripped)
            and len(stripped) < 65
            and kept
        ):
            break
        kept.append(line)
    return "\n".join(kept).strip()


def parse_level(level_line: str) -> int:
    """Парсит уровень заклинания из строки «N уровень» или «Заговор»."""
    if level_line.lower().startswith("заговор"):
        return 0
    m = re.search(r"(\d+)", level_line)
    return int(m.group(1)) if m else 0


def parse_spells(text: str) -> list[SpellEntry]:
    """Парсит описания заклинаний из текста гл. 11."""
    pattern = re.compile(
        r"(?ms)^([А-ЯЁ][А-ЯЁа-яё \-–]{2,70})\n"
        r"((?:Заговор|\d+) уровень, ([^\n]+))\n"
        r"Время накладывания: ([^\n]+)\n"
        r"Дистанция: ([^\n]+)\n"
        r"Компоненты: ([^\n]+(?:\n(?![А-ЯЁ]{3,})[^\n]+)*)\n"
        r"Длительность: ([^\n]+)\n"
    )
    entries: list[SpellEntry] = []
    for m in pattern.finditer(text):
        name = m.group(1).strip()
        if len(name) < 3 or name in {"ЗАКЛИНАНИЯ", "ЗАГОВОРЫ"}:
            continue
        body_start = m.end()
        next_m = pattern.search(text, body_start)
        body_end = next_m.start() if next_m else len(text)
        body_raw = text[body_start:body_end]
        body_raw = _truncate_at_next_heading(body_raw)
        higher = ""
        hl_pat = (
            r"На больших уровнях:\s*[^\n]+"
            r"(?:\n(?![А-ЯЁ]{3,}[^\n]{0,60}$)[^\n]+)*"
        )
        hl_match = re.search(hl_pat, body_raw, re.IGNORECASE)
        if hl_match:
            higher = re.sub(r"\s+", " ", hl_match.group(0)).strip()
            body_raw = body_raw[: hl_match.start()].strip()
        entries.append(
            SpellEntry(
                name_ru=name,
                level_line=m.group(2).strip(),
                level=parse_level(m.group(2)),
                school_ru=m.group(3).strip().lower(),
                casting_time=m.group(4).strip(),
                range_=m.group(5).strip(),
                components=re.sub(r"\s+", " ", m.group(6)).strip(),
                duration=m.group(7).strip(),
                body=body_raw.strip(),
                higher_levels=higher,
            )
        )
    return entries


def parse_spells_fallback(text: str) -> list[SpellEntry]:
    """Дополнительный парсер по строкам уровня (для пропущенных заклинаний)."""
    pattern = re.compile(
        r"(?ms)^([А-ЯЁ][А-ЯЁа-яё \-–]{2,70})\n"
        r"((?:Заговор|\d+) уровень, ([^\n]+))\n"
        r"Время накладывания: ([^\n]+)\n"
        r"Дистанция: ([^\n]+)\n"
        r"Компоненты: ([^\n]+)\n"
        r"Длительность: ([^\n]+)\n"
    )
    entries: list[SpellEntry] = []
    for m in pattern.finditer(text):
        name = m.group(1).strip()
        if len(name) < 3:
            continue
        body_start = m.end()
        next_m = pattern.search(text, body_start)
        body_end = next_m.start() if next_m else len(text)
        body_raw = _truncate_at_next_heading(text[body_start:body_end])
        entries.append(
            SpellEntry(
                name_ru=name,
                level_line=m.group(2).strip(),
                level=parse_level(m.group(2)),
                school_ru=m.group(3).strip().lower(),
                casting_time=m.group(4).strip(),
                range_=m.group(5).strip(),
                components=m.group(6).strip(),
                duration=m.group(7).strip(),
                body=body_raw,
                higher_levels="",
            )
        )
    return entries


def merge_spells(
    primary: list[SpellEntry], fallback: list[SpellEntry]
) -> list[SpellEntry]:
    """Объединяет списки заклинаний без дубликатов по slug."""
    seen: set[str] = set()
    merged: list[SpellEntry] = []
    for sp in primary + fallback:
        slug = spell_slug(sp.name_ru)
        if slug in seen:
            continue
        seen.add(slug)
        merged.append(sp)
    return merged


def frontmatter(
    *,
    phb_chapter: int,
    phb_section: str,
    phb_pages: tuple[int, int],
    phb_part: int,
    entity_id: str,
    tags: list[str],
    mud_status: str,
    yaml_ref: str | None = None,
) -> str:
    """Формирует YAML frontmatter."""
    data: dict[str, object] = {
        "phb_chapter": phb_chapter,
        "phb_section": phb_section,
        "phb_pages": list(phb_pages),
        "phb_part": phb_part,
        "id": entity_id,
        "tags": tags,
        "mud_status": mud_status,
    }
    if yaml_ref:
        data["mud_refs"] = {"yaml": yaml_ref}
    yaml_body: str = yaml.dump(data, allow_unicode=True, sort_keys=False)
    return "---\n" + yaml_body + "---\n\n"


def dev_section(
    status: str, yaml_ref: str | None = None, core: str | None = None
) -> str:
    """Блок «Для разработчиков»."""
    yaml_cell = f"`{yaml_ref}`" if yaml_ref else "—"
    core_cell = f"`{core}`" if core else "—"
    return (
        "## Для разработчиков\n\n"
        "| Аспект | Значение |\n"
        "|--------|----------|\n"
        f"| Статус | {status} |\n"
        f"| YAML | {yaml_cell} |\n"
        f"| Core | {core_cell} |\n"
    )


def write_file(path: Path, content: str) -> None:
    """Записывает markdown-файл."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def extract_by_heading(
    text: str, heading: str, all_headings: list[str]
) -> str:
    """Извлекает подраздел по заголовку КАПС до следующего заголовка."""
    pattern = re.compile(rf"(?m)^{re.escape(heading)}\s*$")
    match = pattern.search(text)
    if not match:
        return text
    start = match.start()
    end = len(text)
    for other in all_headings:
        if other == heading:
            continue
        other_pat = re.compile(rf"(?m)^{re.escape(other)}\s*$")
        other_match = other_pat.search(text, match.end())
        if other_match and other_match.start() < end:
            end = other_match.start()
    return text[start:end].strip()


def generate_entity_file(
    entity: EntityRef,
    *,
    subdir: str,
    chapter: int,
    part: int,
    tags: list[str],
    core: str | None = None,
    pdf: Path,
) -> Path:
    """Генерирует файл сущности (раса/класс/предыстория)."""
    text = extract_pages(pdf, entity.pages[0], entity.pages[1])
    if subdir == "races" and entity.id in RACE_HEADINGS:
        chapter_text = extract_pages(pdf, 17, 44)
        text = extract_by_heading(
            chapter_text,
            RACE_HEADINGS[entity.id],
            list(RACE_HEADINGS.values()),
        )
    elif subdir == "classes" and entity.id in CLASS_HEADINGS:
        chapter_text = extract_pages(pdf, 45, 120)
        text = extract_by_heading(
            chapter_text,
            CLASS_HEADINGS[entity.id],
            list(CLASS_HEADINGS.values()),
        )
    write_section(subdir, entity.id, text)
    title = entity.ru_name
    body = summarize_section(text, max_bullets=14)
    content = (
        frontmatter(
            phb_chapter=chapter,
            phb_section=title,
            phb_pages=entity.pages,
            phb_part=part,
            entity_id=entity.id,
            tags=tags,
            mud_status=entity.mud_status,
            yaml_ref=entity.yaml_ref,
        )
        + f"# {title}\n\n"
        f"> Источник: PHB, стр. {entity.pages[0]}–{entity.pages[1]}. "
        "Пересказ правил, не дословная копия PHB.\n\n"
        "## Для игроков\n\n"
        f"{body}\n"
        f"{dev_section(entity.mud_status, entity.yaml_ref, core)}\n"
    )
    path = RULES_DIR / subdir / f"{entity.id}.md"
    write_file(path, content)
    return path


def generate_spell_file(spell: SpellEntry, pdf_pages: tuple[int, int]) -> Path:
    """Генерирует карточку заклинания."""
    slug = spell_slug(spell.name_ru)
    level_prefix = "cantrip" if spell.level == 0 else f"level-{spell.level}"
    filename = f"{level_prefix}-{slug}.md"
    school_en = SCHOOL_RU_TO_EN.get(spell.school_ru, spell.school_ru)
    effect = "\n".join(f"- {b}" for b in to_bullets(spell.body, max_items=8))
    higher = ""
    if spell.higher_levels:
        higher = f"\n### На больших уровнях\n\n{spell.higher_levels}\n"
    level_label = "Заговор" if spell.level == 0 else f"{spell.level} уровень"
    content = (
        frontmatter(
            phb_chapter=11,
            phb_section=spell.name_ru.title(),
            phb_pages=pdf_pages,
            phb_part=3,
            entity_id=slug,
            tags=["spell", school_en, f"level-{spell.level}"],
            mud_status="planned",
        )
        + f"# {spell.name_ru.title()}\n\n"
        "> Источник: PHB, гл. 11. Пересказ правил.\n\n"
        "## Параметры\n\n"
        f"| Параметр | Значение |\n|----------|----------|\n"
        f"| Уровень | {level_label} |\n"
        f"| Школа | {spell.school_ru.title()} (`{school_en}`) |\n"
        f"| Время | {spell.casting_time} |\n"
        f"| Дистанция | {spell.range_} |\n"
        f"| Компоненты | {spell.components} |\n"
        f"| Длительность | {spell.duration} |\n\n"
        "## Эффект\n\n"
        f"{effect or '_См. PHB PDF._'}\n"
        f"{higher}"
        f"{dev_section('planned')}\n"
    )
    path = RULES_DIR / "spells" / filename
    write_file(path, content)
    return path


def generate_chapter_overview(
    ch: dict[str, object], pdf: Path, extra_links: str = ""
) -> Path:
    """Генерирует или дополняет обзорную главу."""
    pages_raw = ch["pages"]
    assert isinstance(pages_raw, tuple)
    pages: tuple[int, int] = pages_raw
    text = extract_pages(pdf, pages[0], pages[1])
    ch_id = str(ch["id"])
    write_section("chapters", ch_id, text)
    body = summarize_section(text, max_bullets=12)
    file_name = str(ch["file"])
    path = RULES_DIR / file_name
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    dev_match = re.search(r"## Для разработчиков.*", existing, re.DOTALL)
    dev_block = (
        dev_match.group(0) if dev_match else dev_section(str(ch["mud_status"]))
    )
    content = (
        frontmatter(
            phb_chapter=int(str(ch["chapter"])),
            phb_section=str(ch["ru"]),
            phb_pages=pages,
            phb_part=int(str(ch["part"])),
            entity_id=ch_id,
            tags=["chapter"],
            mud_status=str(ch["mud_status"]),
        )
        + f"# {ch['ru']}\n\n"
        f"> Источник: PHB, стр. {pages[0]}–{pages[1]}. "
        "Пересказ правил, не дословная копия PHB.\n\n"
        f"{extra_links}"
        "## Для игроков\n\n"
        f"{body}\n"
        f"{dev_block}\n"
    )
    write_file(path, content)
    return path


def build_entity_links(entities: tuple[EntityRef, ...], subdir: str) -> str:
    """Таблица ссылок на детальные файлы."""
    lines = [
        "## Детальные карточки\n\n",
        "| ID | Название | Файл | Статус MUD |\n",
        "|----|----------|------|------------|\n",
    ]
    for e in entities:
        link = f"[{e.id}.md]({subdir}/{e.id}.md)"
        lines.append(f"| `{e.id}` | {e.ru_name} | {link} | {e.mud_status} |\n")
    return "".join(lines) + "\n"


def generate_spell_indexes(spells: list[SpellEntry]) -> None:
    """Генерирует индексы заклинаний по уровню и школе."""
    by_level: dict[int, list[SpellEntry]] = {}
    by_school: dict[str, list[SpellEntry]] = {}
    for sp in spells:
        by_level.setdefault(sp.level, []).append(sp)
        by_school.setdefault(sp.school_ru, []).append(sp)
    level_lines = ["# Индекс заклинаний по уровню\n\n"]
    for lvl in sorted(by_level):
        label = "Заговоры" if lvl == 0 else f"Уровень {lvl}"
        level_lines.append(f"## {label}\n\n")
        for sp in sorted(by_level[lvl], key=lambda s: s.name_ru):
            slug = spell_slug(sp.name_ru)
            prefix = "cantrip" if lvl == 0 else f"level-{lvl}"
            level_lines.append(
                f"- [{sp.name_ru.title()}]({prefix}-{slug}.md) (`{slug}`)\n"
            )
        level_lines.append("\n")
    write_file(
        RULES_DIR / "spells" / "_index-by-level.md", "".join(level_lines)
    )
    school_lines = ["# Индекс заклинаний по школе\n\n"]
    for school in sorted(by_school):
        school_lines.append(f"## {school.title()}\n\n")
        for sp in sorted(by_school[school], key=lambda s: s.name_ru):
            slug = spell_slug(sp.name_ru)
            prefix = "cantrip" if sp.level == 0 else f"level-{sp.level}"
            school_lines.append(
                f"- [{sp.name_ru.title()}]({prefix}-{slug}.md) (`{slug}`)\n"
            )
        school_lines.append("\n")
    write_file(
        RULES_DIR / "spells" / "_index-by-school.md", "".join(school_lines)
    )


def generate_glossaries(pdf: Path) -> None:
    """Генерирует словари из стр. 313–320."""
    text = extract_pages(pdf, 313, 320)
    write_section("reference", "glossaries", text)
    ru_en_lines = [
        "# Англо-русский словарь PHB\n\n",
        "> Источник: PHB, стр. 313–317.\n\n",
    ]
    en_ru_lines = [
        "# Русско-английский словарь PHB\n\n",
        "> Источник: PHB, стр. 317–320.\n\n",
    ]
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("АНГЛО") or line.startswith("РУССКО"):
            continue
        if "—" in line or "–" in line:
            sep = "—" if "—" in line else "–"
            parts = [p.strip() for p in line.split(sep, 1)]
            if len(parts) == 2:
                ru_en_lines.append(f"- {parts[0]} — {parts[1]}\n")
                en_ru_lines.append(f"- {parts[1]} — {parts[0]}\n")
    write_file(RULES_DIR / "glossaries" / "ru-en.md", "".join(ru_en_lines))
    write_file(RULES_DIR / "glossaries" / "en-ru.md", "".join(en_ru_lines))


def build_toc_yaml(generated: list[dict[str, object]]) -> None:
    """Записывает toc.yaml."""
    toc = {"source": "docs/PHB_ D&D_2023 RUS.pdf", "entries": generated}
    write_file(
        RULES_DIR / "toc.yaml",
        yaml.dump(toc, allow_unicode=True, sort_keys=False),
    )


def generate_all(pdf: Path | None = None) -> dict[str, int]:
    """Генерирует весь справочник."""
    pdf_file = pdf_path(pdf)
    counts = {
        "races": 0,
        "classes": 0,
        "backgrounds": 0,
        "spells": 0,
        "appendices": 0,
        "chapters": 0,
    }
    toc_entries: list[dict[str, object]] = []

    core_map = {
        "dwarf": "core/races.py",
        "elf": "core/races.py",
        "human": "core/races.py",
        "half_orc": "core/races.py",
        "fighter": "core/classes.py",
        "rogue": "core/classes.py",
        "cleric": "core/classes.py",
        "bard": "core/classes.py",
    }

    for race in RACES:
        generate_entity_file(
            race,
            subdir="races",
            chapter=2,
            part=1,
            tags=["race"],
            core=core_map.get(race.id),
            pdf=pdf_file,
        )
        counts["races"] += 1
        toc_entries.append(
            {
                "id": race.id,
                "file": f"races/{race.id}.md",
                "pages": list(race.pages),
            }
        )

    for cls in CLASSES:
        generate_entity_file(
            cls,
            subdir="classes",
            chapter=3,
            part=1,
            tags=["class"],
            core=core_map.get(cls.id),
            pdf=pdf_file,
        )
        counts["classes"] += 1
        toc_entries.append(
            {
                "id": cls.id,
                "file": f"classes/{cls.id}.md",
                "pages": list(cls.pages),
            }
        )

    for bg in BACKGROUNDS:
        generate_entity_file(
            bg,
            subdir="backgrounds",
            chapter=4,
            part=1,
            tags=["background"],
            core="core/backgrounds.py",
            pdf=pdf_file,
        )
        counts["backgrounds"] += 1
        toc_entries.append(
            {
                "id": bg.id,
                "file": f"backgrounds/{bg.id}.md",
                "pages": list(bg.pages),
            }
        )

    for app in APPENDICES:
        text = extract_pages(pdf_file, app.pages[0], app.pages[1])
        write_section("appendices", app.id, text)
        body = summarize_section(text, max_bullets=15)
        content = (
            frontmatter(
                phb_chapter=0,
                phb_section=app.ru_name,
                phb_pages=app.pages,
                phb_part=0,
                entity_id=app.id,
                tags=["appendix"],
                mud_status=app.mud_status,
            )
            + f"# {app.ru_name}\n\n"
            f"> Источник: PHB, стр. {app.pages[0]}–{app.pages[1]}.\n\n"
            "## Для игроков\n\n"
            f"{body}\n"
            f"{dev_section(app.mud_status)}\n"
        )
        write_file(RULES_DIR / "appendices" / f"{app.id}.md", content)
        counts["appendices"] += 1
        toc_entries.append(
            {
                "id": app.id,
                "file": f"appendices/{app.id}.md",
                "pages": list(app.pages),
            }
        )

    spell_text = extract_pages(pdf_file, 211, 289)
    write_section("spells", "all", spell_text)
    spells = merge_spells(
        parse_spells(spell_text), parse_spells_fallback(spell_text)
    )
    seen: set[str] = set()
    for sp in spells:
        slug = spell_slug(sp.name_ru)
        if slug in seen:
            continue
        seen.add(slug)
        generate_spell_file(sp, (211, 289))
        counts["spells"] += 1
    generate_spell_indexes(spells)
    generate_glossaries(pdf_file)

    for ch in CHAPTERS:
        file_name = str(ch["file"])
        if file_name in CHAPTER_PRESERVE and (RULES_DIR / file_name).is_file():
            counts["chapters"] += 1
            toc_entries.append(
                {
                    "id": ch["id"],
                    "file": ch["file"],
                    "pages": list(ch["pages"]),
                }
            )
            continue
        extra = ""
        if ch["file"] == "02-races.md":
            extra = build_entity_links(RACES, "races")
        elif ch["file"] == "03-classes.md":
            extra = build_entity_links(CLASSES, "classes")
        elif ch["file"] == "04-backgrounds.md":
            extra = build_entity_links(BACKGROUNDS, "backgrounds")
        elif ch["file"] == "06-individual-options.md":
            extra = (
                "## Разделы\n\n"
                "- [Мультиклассирование](06-multiclass.md)\n"
                "- [Черты](06-feats.md)\n\n"
            )
        elif ch["file"] == "11-spells.md":
            extra = (
                "## Индексы\n\n"
                "- [По уровню](spells/_index-by-level.md)\n"
                "- [По школе](spells/_index-by-school.md)\n\n"
                f"Всего карточек: **{counts['spells']}**.\n\n"
            )
        elif ch["file"] == "appendices.md":
            extra = build_entity_links(APPENDICES, "appendices")
        generate_chapter_overview(ch, pdf_file, extra)
        counts["chapters"] += 1
        toc_entries.append(
            {"id": ch["id"], "file": ch["file"], "pages": list(ch["pages"])}
        )

    build_toc_yaml(toc_entries)

    # Удаляем устаревший объединённый файл
    old_spells = RULES_DIR / "10-spells.md"
    if old_spells.exists():
        old_spells.unlink()

    return counts


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Генерация docs/rules/ из PHB PDF"
    )
    parser.add_argument(
        "--pdf", type=Path, default=None, help="Путь к PHB PDF"
    )
    args = parser.parse_args()
    try:
        counts = generate_all(args.pdf)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1
    total = sum(counts.values())
    print(f"Generated {total} files: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
