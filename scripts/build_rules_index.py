#!/usr/bin/env python3
"""Сборка и нормализация индексов docs/rules/; заклинания — из локального PHB PDF."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml
from phb_spell_parse import (
    DEFAULT_PDF,
    effect_to_bullets,
    extract_pdf_text,
    load_spells_index,
    map_parsed_to_ids,
    parse_spell_descriptions,
)
from rules_class_data import (
    CLASS_MUD_STATUS,
    CLASS_PAGES,
    CLASS_PHB,
    CLASS_TITLES,
)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
RULES_DIR = ROOT / "docs" / "rules"
INDEX_LAYOUT = "agent-v2"
PHB_SECTION = "Правила (PHB)"
MUD_SECTION = "Реализация в MUD"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_AUTO_BLOCK_RE = re.compile(
    r"<!-- phb:auto:(?P<name>[\w-]+) -->(?P<body>.*?)<!-- /phb:auto:\1 -->",
    re.DOTALL,
)
_MUD_BLOCK_RE = re.compile(
    r"<!-- mud:implementation -->(?P<body>.*?)<!-- /mud:implementation -->",
    re.DOTALL,
)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1)) or {}
    return (data if isinstance(data, dict) else {}), text[match.end() :]


def format_frontmatter(data: dict[str, Any]) -> str:
    return (
        f"---\n{yaml.dump(data, allow_unicode=True, sort_keys=False)}---\n\n"
    )


def bullets_from_text(text: str) -> str:
    lines: list[str] = []
    for raw in text.replace("•", "\n").splitlines():
        line = raw.strip()
        if not line or line == "•":
            continue
        if not line.startswith("- "):
            line = f"- {line}"
        lines.append(line)
    return "\n".join(lines) + ("\n" if lines else "")


def load_feats() -> dict[str, dict[str, Any]]:
    path = ROOT / "database" / "progression" / "feats.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    feats = data.get("feats", {})
    return feats if isinstance(feats, dict) else {}


def load_backgrounds() -> dict[str, dict[str, Any]]:
    path = ROOT / "database" / "backgrounds" / "backgrounds.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    bgs = data.get("backgrounds", {})
    return bgs if isinstance(bgs, dict) else {}


SKILL_RU: dict[str, str] = {
    "acrobatics": "Акробатика",
    "animal_handling": "Уход за животными",
    "arcana": "Магия",
    "athletics": "Атлетика",
    "deception": "Обман",
    "history": "История",
    "insight": "Проницательность",
    "intimidation": "Запугивание",
    "investigation": "Анализ",
    "medicine": "Медицина",
    "nature": "Природа",
    "perception": "Внимательность",
    "performance": "Выступление",
    "persuasion": "Убеждение",
    "religion": "Религия",
    "sleight_of_hand": "Ловкость рук",
    "stealth": "Скрытность",
    "survival": "Выживание",
}

TOOL_RU: dict[str, str] = {
    "disguise_kit": "набор для грима",
    "forgery_kit": "набор для подделки",
    "gaming_set": "игровой набор",
    "land_vehicles": "наземный транспорт",
    "water_vehicles": "водный транспорт",
    "navigators_tools": "инструменты навигатора",
    "thieves_tools": "инструменты вора",
    "herbalism_kit": "набор травника",
    "artisan_tools": "инструменты ремесленника",
    "musical_instrument": "музыкальный инструмент",
}


RACE_CARDS: dict[str, dict[str, str]] = {
    "dwarf": {
        "title": "Дварф",
        "quick": (
            "Телосложение +2; тёмное зрение 60 фт.; устойчивость к яду; "
            "боевые топоры/молоты; инструменты ремесленника"
        ),
        "summary": (
            "### Увеличение характеристик\n\n- Телосложение +2.\n\n"
            "### Размер\n\n- Средний.\n\n"
            "### Скорость\n\n"
            "- 25 футов; скорость не снижается от тяжёлых доспехов.\n\n"
            "### Тёмное зрение\n\n- 60 футов (тусклый свет и темнота, оттенки серого).\n\n"
            "### Дварфская устойчивость\n\n"
            "- Преимущество на спасброски от яда; сопротивление урону ядом.\n\n"
            "### Дварфская боевая тренировка\n\n"
            "- Владение боевым топором, ручным топором, лёгким и боевым молотом.\n\n"
            "### Владение инструментами\n\n"
            "- Инструменты кузнеца, пивовара или каменщика на выбор.\n\n"
            "### Знание камня\n\n"
            "- Удвоенный бонус мастерства к Истории, связанной с происхождением каменной кладки.\n\n"
            "### Языки\n\n- Общий и дварфский.\n\n"
            "### Подрасы\n\n"
            "- **Горный дварф:** Сила +2; владение лёгкими и средними доспехами.\n"
            "- **Холмовой дварф:** Мудрость +1; дварфская выдержка (+1 к макс. хитам и +1 хит за уровень).\n"
        ),
        "mud_status": "partial",
    },
    "elf": {
        "title": "Эльф",
        "quick": "Ловкость +2; тёмное зрение 60 фт.; Внимательность; наследие фей; транс 4 ч",
        "summary": (
            "### Увеличение характеристик\n\n- Ловкость +2.\n\n"
            "### Размер\n\n- Средний.\n\n"
            "### Скорость\n\n- 30 футов.\n\n"
            "### Тёмное зрение\n\n- 60 футов (тусклый свет и темнота, оттенки серого).\n\n"
            "### Обострённые чувства\n\n- Владение навыком Внимательность.\n\n"
            "### Наследие фей\n\n"
            "- Преимущество на спасброски от очарования; невосприимчивость к магическому сну.\n\n"
            "### Транс\n\n"
            "- 4 часа медитации вместо сна; эффект как у 8 часов сна.\n\n"
            "### Языки\n\n- Общий и эльфийский.\n\n"
            "### Подрасы\n\n"
            "- **Высший эльф:** Интеллект +1; владение длинным мечом, рапирой, "
            "коротким мечом, длинным и коротким луком; заговор из списка волшебника; "
            "дополнительный язык.\n"
            "- **Лесной эльф:** Мудрость +1; скорость 35 футов; те же владения оружием; "
            "маскировка в природе (за укрытием от существ, которых вы не видите).\n"
            "- **Дроу:** Харизма +1; тёмное зрение 120 фт.; чувствительность к солнцу "
            "(помеха на атаки и Внимательность на виду); магия дроу; владение рапирой, "
            "коротким мечом, ручным арбалетом.\n"
        ),
        "mud_status": "partial",
    },
    "halfling": {
        "title": "Полурослик",
        "quick": "Ловкость +2; размер Маленький; скорость 25 фт.; везунчик; храбрость",
        "summary": (
            "### Увеличение характеристик\n\n- Ловкость +2.\n\n"
            "### Размер\n\n- Маленький.\n\n"
            "### Скорость\n\n- 25 футов.\n\n"
            "### Везунчик\n\n"
            "- При «1» на к20 атаки/проверки/спасброска — переброс (обязательно новый результат).\n\n"
            "### Храбрость\n\n- Преимущество на спасброски от испуга.\n\n"
            "### Языки\n\n- Общий и язык полуросликов.\n\n"
            "### Подрасы\n\n"
            "- **Легконогий:** Харизма +1; скрытность за существом Среднего или крупнее.\n"
            "- **Крепкий:** Телосложение +1; сопротивление яду; преимущество на спасброски от яда.\n"
        ),
        "mud_status": "planned",
    },
    "human": {
        "title": "Человек",
        "quick": "Стандарт: все характеристики +1; вариант: +1 к двум, навык, черта, язык",
        "summary": (
            "### Стандартный человек\n\n"
            "- Все характеристики +1.\n"
            "- Размер: Средний; скорость 30 футов.\n"
            "- Языки: общий + один на выбор.\n\n"
            "### Вариант человека (опциональное правило PHB)\n\n"
            "- +1 к двум разным характеристикам на выбор.\n"
            "- Владение одним навыком на выбор.\n"
            "- Одна черта на выбор (требования черты должны выполняться).\n"
            "- Один дополнительный язык.\n"
        ),
        "mud_status": "partial",
    },
    "dragonborn": {
        "title": "Драконорождённый",
        "quick": (
            "Сила +2, Харизма +1; оружие дыхания (2к6→5к6); "
            "сопротивление по родословной"
        ),
        "summary": (
            "### Увеличение характеристик\n\n- Сила +2, Харизма +1.\n\n"
            "### Размер\n\n- Средний.\n\n"
            "### Скорость\n\n- 30 футов.\n\n"
            "### Наследие драконов\n\n"
            "- Родословная из таблицы PHB: вид урона, форма выдоха (конус 15 фт. или "
            "линия 5×30 фт.) и тип спасброска (Телосложение или Ловкость).\n\n"
            "### Оружие дыхания\n\n"
            "- Действием — разрушительный выдох в зоне по родословной.\n"
            "- Сл спасброска = 8 + мод. Телосложения + бонус мастерства.\n"
            "- Провал — 2к6 урона (3к6 на 6 ур., 4к6 на 11, 5к6 на 16); успех — половина.\n"
            "- 1 раз до короткого или долгого отдыха.\n\n"
            "### Сопротивление урону\n\n- Сопротивление типу урона выбранной родословной.\n\n"
            "### Языки\n\n- Общий и драконий.\n"
        ),
        "mud_status": "planned",
    },
    "gnome": {
        "title": "Гном",
        "quick": "Интеллект +2; размер Маленький; тёмное зрение; хитрость гнома",
        "summary": (
            "### Увеличение характеристик\n\n- Интеллект +2.\n\n"
            "### Размер\n\n- Маленький.\n\n"
            "### Скорость\n\n- 25 футов.\n\n"
            "### Тёмное зрение\n\n- 60 футов.\n\n"
            "### Хитрость гнома\n\n"
            "- Преимущество на спасброски Интеллекта, Мудрости и Харизмы против магии.\n\n"
            "### Языки\n\n- Общий и гномий.\n\n"
            "### Подрасы\n\n"
            "- **Лесной гном:** Ловкость +1; заговор *малая иллюзия* (Интеллект); "
            "*разговор с животными* 1/день.\n"
            "- **Скальный гном:** Телосложение +1; мастерство в Истории/Магии/Природе "
            "при проверках, связанных с механизмами; миниатюрные механические игрушки "
            "(ремесло, не боевой урон).\n"
        ),
        "mud_status": "planned",
    },
    "half_elf": {
        "title": "Полуэльф",
        "quick": "Харизма +2; +1 к двум характеристикам; тёмное зрение; наследие фей; 2 навыка",
        "summary": (
            "### Увеличение характеристик\n\n"
            "- Харизма +2; +1 к двум другим характеристикам на выбор.\n\n"
            "### Размер\n\n- Средний.\n\n"
            "### Скорость\n\n- 30 футов.\n\n"
            "### Тёмное зрение\n\n- 60 футов.\n\n"
            "### Наследие фей\n\n"
            "- Преимущество на спасброски от очарования; невосприимчивость к магическому сну.\n\n"
            "### Универсальность\n\n- Владение двумя навыками на выбор.\n\n"
            "### Языки\n\n- Общий, эльфийский и ещё один на выбор.\n"
        ),
        "mud_status": "planned",
    },
    "half_orc": {
        "title": "Полуорк",
        "quick": "Сила +2, Телосложение +1; тёмное зрение; неукротимость; свирепые атаки",
        "summary": (
            "### Увеличение характеристик\n\n- Сила +2, Телосложение +1.\n\n"
            "### Размер\n\n- Средний.\n\n"
            "### Скорость\n\n- 30 футов.\n\n"
            "### Тёмное зрение\n\n- 60 футов.\n\n"
            "### Неукротимость\n\n"
            "- При снижении до 0 хитов, но не убит — можно остаться с 1 хитом (1/долгий отдых).\n\n"
            "### Свирепые атаки\n\n"
            "- При критическом попадании рукопашной атакой — один дополнительный куб урона оружия.\n\n"
            "### Языки\n\n- Общий и орочий.\n"
        ),
        "mud_status": "partial",
    },
    "tiefling": {
        "title": "Тифлинг",
        "quick": "Интеллект +1, Харизма +2; тёмное зрение; сопротивление огню; дьявольское наследие",
        "summary": (
            "### Увеличение характеристик\n\n- Интеллект +1, Харизма +2.\n\n"
            "### Размер\n\n- Средний.\n\n"
            "### Скорость\n\n- 30 футов.\n\n"
            "### Тёмное зрение\n\n- 60 футов.\n\n"
            "### Адское сопротивление\n\n- Сопротивление урону огнём.\n\n"
            "### Дьявольское наследие\n\n"
            "- Заговор *чудотворство* (базовая характеристика — Харизма).\n"
            "- С 3 уровня — *адское возмездие* (2 ур.) 1/долгий отдых.\n"
            "- С 5 уровня — *тьма* 1/долгий отдых.\n\n"
            "### Языки\n\n- Общий и инфернальный.\n"
        ),
        "mud_status": "planned",
    },
}


def write_race_card(race_id: str, card: dict[str, str]) -> None:
    path = RULES_DIR / "entities" / "races" / f"{race_id}.md"
    pages_map = {
        "dwarf": [18, 20],
        "elf": [21, 25],
        "halfling": [26, 28],
        "human": [29, 31],
        "dragonborn": [32, 34],
        "gnome": [35, 37],
        "half_elf": [38, 39],
        "half_orc": [40, 41],
        "tiefling": [42, 43],
    }
    pages = pages_map.get(race_id, [17, 44])
    mud_status = card["mud_status"]
    fm: dict[str, Any] = {
        "phb_chapter": 2,
        "phb_section": card["title"],
        "phb_pages": pages,
        "phb_part": 1,
        "id": race_id,
        "type": "race",
        "tags": ["race"],
        "mud_status": mud_status,
        "quick": card["quick"],
    }
    if mud_status == "partial":
        fm["mud_refs"] = {"yaml": f"database/races/races.yaml#{race_id}"}
    yaml_line = (
        f"`database/races/races.yaml#{race_id}`"
        if mud_status == "partial"
        else "—"
    )
    mud_inner = (
        "| Аспект | Значение |\n|--------|----------|\n"
        f"| Статус | {mud_status} |\n"
        f"| YAML | {yaml_line} |\n"
        "| Core | `core/races.py` |\n"
    )
    content = (
        format_frontmatter(fm)
        + f"# {card['title']}\n\n"
        + f"> Источник: PHB, стр. {pages[0]}–{pages[1]}. Только механика.\n\n"
        + f"## {PHB_SECTION}\n\n"
        + f"<!-- phb:auto:summary -->\n{card['summary']}<!-- /phb:auto:summary -->\n\n"
        + f"## {MUD_SECTION}\n\n"
        + f"<!-- mud:implementation -->\n{mud_inner}<!-- /mud:implementation -->\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sync_all_race_cards() -> int:
    for race_id, card in RACE_CARDS.items():
        write_race_card(race_id, card)
    return len(RACE_CARDS)


def format_background_grants(grants: list[Any]) -> tuple[str, str]:
    skills: list[str] = []
    tools: list[str] = []
    for grant in grants:
        if not isinstance(grant, dict):
            continue
        gtype = grant.get("type")
        if gtype == "skill_proficiency":
            for sk in grant.get("skills", []) or []:
                skills.append(SKILL_RU.get(str(sk), str(sk)))
        elif gtype == "tool_proficiency":
            if grant.get("choice"):
                pool = grant.get("pool", "any")
                count = grant.get("count", 1)
                tools.append(f"{count} на выбор ({pool})")
            else:
                for tool in grant.get("tools", []) or []:
                    tools.append(TOOL_RU.get(str(tool), str(tool)))
    skills_block = (
        "### Навыки\n\n" + "\n".join(f"- {s}" for s in skills) + "\n\n"
        if skills
        else ""
    )
    tools_block = (
        "### Инструменты\n\n" + "\n".join(f"- {t}" for t in tools) + "\n\n"
        if tools
        else ""
    )
    return skills_block, tools_block


def sync_background_file(
    path: Path, bg_id: str, payload: dict[str, Any]
) -> None:
    name = str((payload.get("name") or {}).get("ru", bg_id))
    pages = [121, 142]
    feature = payload.get("feature") or {}
    feat_name = str((feature.get("name") or {}).get("ru", "—"))
    feat_desc = str((feature.get("description") or {}).get("ru", "")).strip()
    equipment = (payload.get("equipment") or {}).get("ru") or []
    grants = payload.get("grants") or []
    skills_block, tools_block = format_background_grants(
        grants if isinstance(grants, list) else []
    )
    lang_lines: list[str] = []
    for grant in grants if isinstance(grants, list) else []:
        if isinstance(grant, dict) and grant.get("type") == "language":
            count = grant.get("count", 1)
            pool = grant.get("pool", "common")
            lang_lines.append(f"- {count} язык(а) на выбор (пул: {pool})")
    lang_block = (
        "### Языки\n\n" + "\n".join(lang_lines) + "\n\n" if lang_lines else ""
    )
    equip_block = (
        "### Снаряжение\n\n"
        + "\n".join(f"- {item}" for item in equipment)
        + "\n\n"
        if equipment
        else ""
    )
    feature_block = (
        f"### Умение: {feat_name}\n\n- {feat_desc}\n\n" if feat_desc else ""
    )
    summary = (
        skills_block + lang_block + tools_block + equip_block + feature_block
    )
    quick_parts: list[str] = []
    if skills_block:
        quick_parts.append(
            ", ".join(
                line[2:]
                for line in skills_block.splitlines()
                if line.startswith("- ")
            )
        )
    if feat_name != "—":
        quick_parts.append(f"умение: {feat_name}")
    quick = "; ".join(quick_parts) if quick_parts else name

    if path.is_file():
        fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    else:
        fm = {}
    fm.update(
        {
            "phb_chapter": 4,
            "phb_section": name,
            "phb_pages": pages,
            "phb_part": 1,
            "id": bg_id,
            "type": "background",
            "tags": ["background"],
            "mud_status": fm.get("mud_status", "partial"),
            "quick": quick,
            "mud_refs": fm.get(
                "mud_refs",
                {"yaml": f"database/backgrounds/backgrounds.yaml#{bg_id}"},
            ),
        }
    )
    mud_inner = (
        "| Аспект | Значение |\n|--------|----------|\n"
        f"| Статус | {fm.get('mud_status', 'partial')} |\n"
        f"| YAML | `database/backgrounds/backgrounds.yaml#{bg_id}` |\n"
        "| Core | `core/backgrounds.py` |\n"
    )
    content = (
        format_frontmatter(fm)
        + f"# {name}\n\n"
        + "> Источник: PHB, гл. 4. Только механика (навыки, снаряжение, умение).\n\n"
        + f"## {PHB_SECTION}\n\n"
        + f"<!-- phb:auto:summary -->\n{summary}<!-- /phb:auto:summary -->\n\n"
        + f"## {MUD_SECTION}\n\n"
        + f"<!-- mud:implementation -->\n{mud_inner}<!-- /mud:implementation -->\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sync_all_backgrounds() -> int:
    backgrounds = load_backgrounds()
    for bg_id, payload in backgrounds.items():
        path = RULES_DIR / "entities" / "backgrounds" / f"{bg_id}.md"
        sync_background_file(path, bg_id, payload)
    return len(backgrounds)


def simplify_chapter_races() -> None:
    path = RULES_DIR / "chapters" / "02-races.md"
    if not path.is_file():
        return
    fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    links_match = re.search(
        r"<!-- phb:auto:links -->.*?<!-- /phb:auto:links -->",
        body,
        re.DOTALL,
    )
    links_block = links_match.group(0) if links_match else ""
    mud_match = _MUD_BLOCK_RE.search(body)
    mud_inner = mud_match.group("body").strip() if mud_match else ""
    summary = (
        "### Общие правила\n\n"
        "- Раса задаёт увеличение характеристик, размер, скорость, языки и расовые особенности.\n"
        "- Подрасы — в карточках `entities/races/` (таблица ниже).\n"
        "- **Без лора:** в справочнике только механика PHB; описания внешности, "
        "культуры и мировоззрения — в PDF, не здесь.\n"
    )
    content = (
        format_frontmatter(fm)
        + "# Расы\n\n"
        + "> Источник: PHB, стр. 17–44. Индекс рас.\n\n"
        + links_block
        + "\n\n"
        + f"## {PHB_SECTION}\n\n"
        + f"<!-- phb:auto:summary -->\n{summary}<!-- /phb:auto:summary -->\n\n"
        + f"## {MUD_SECTION}\n\n"
        + f"<!-- mud:implementation -->\n{mud_inner}\n<!-- /mud:implementation -->\n"
    )
    path.write_text(content, encoding="utf-8")


def simplify_chapter_backgrounds() -> None:
    path = RULES_DIR / "chapters" / "04-backgrounds.md"
    if not path.is_file():
        return
    fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    links_match = re.search(
        r"<!-- phb:auto:links -->.*?<!-- /phb:auto:links -->",
        body,
        re.DOTALL,
    )
    links_block = links_match.group(0) if links_match else ""
    mud_match = _MUD_BLOCK_RE.search(body)
    mud_inner = mud_match.group("body").strip() if mud_match else ""
    summary = (
        "### Предыстории PHB\n\n"
        "- Каждая предыстория: владение навыками, языками/инструментами, "
        "стартовое снаряжение и умение (feature).\n"
        "- Детали — в карточках `entities/backgrounds/` (таблица ниже).\n\n"
        "### Не в справочнике (ролевой отыгрыш)\n\n"
        "- Таблицы черт личности, идеалов, привязанностей, слабостей и правило "
        "«Вдохновение» — для DM; в MUD не реализованы.\n"
    )
    content = (
        format_frontmatter(fm)
        + "# Личность и предыстория\n\n"
        + "> Источник: PHB, стр. 121–142. Индекс предысторий.\n\n"
        + links_block
        + "\n\n"
        + f"## {PHB_SECTION}\n\n"
        + f"<!-- phb:auto:summary -->\n{summary}<!-- /phb:auto:summary -->\n\n"
        + f"## {MUD_SECTION}\n\n"
        + f"<!-- mud:implementation -->\n{mud_inner}\n<!-- /mud:implementation -->\n"
    )
    path.write_text(content, encoding="utf-8")


def write_class_card(class_id: str, summary: str, quick: str) -> None:
    path = RULES_DIR / "entities" / "classes" / f"{class_id}.md"
    pages = CLASS_PAGES.get(class_id, [45, 120])
    title = CLASS_TITLES.get(class_id, class_id)
    mud_status = CLASS_MUD_STATUS.get(class_id, "planned")
    fm: dict[str, Any] = {
        "phb_chapter": 3,
        "phb_section": title,
        "phb_pages": pages,
        "phb_part": 1,
        "id": class_id,
        "type": "class",
        "tags": ["class"],
        "mud_status": mud_status,
        "quick": quick,
    }
    if mud_status == "partial":
        fm["mud_refs"] = {"yaml": f"database/classes/classes.yaml#{class_id}"}
    yaml_line = (
        f"`database/classes/classes.yaml#{class_id}`"
        if mud_status == "partial"
        else "—"
    )
    mud_inner = (
        "| Аспект | Значение |\n|--------|----------|\n"
        f"| Статус | {mud_status} |\n"
        f"| YAML | {yaml_line} |\n"
        "| Core | `core/classes.py`, `core/subclasses.py` |\n"
    )
    content = (
        format_frontmatter(fm)
        + f"# {title}\n\n"
        + f"> Источник: PHB, стр. {pages[0]}–{pages[1]}. Только механика.\n\n"
        + f"## {PHB_SECTION}\n\n"
        + f"<!-- phb:auto:summary -->\n{summary}<!-- /phb:auto:summary -->\n\n"
        + f"## {MUD_SECTION}\n\n"
        + f"<!-- mud:implementation -->\n{mud_inner}<!-- /mud:implementation -->\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sync_all_class_cards() -> int:
    for class_id in sorted(CLASS_PHB):
        phb = CLASS_PHB[class_id]
        write_class_card(class_id, phb["summary"], phb["quick"])
    return len(CLASS_PHB)


def _simplify_chapter_with_links(
    path: Path,
    title: str,
    source_note: str,
    summary: str,
    heading: str | None = None,
) -> None:
    if not path.is_file():
        return
    fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    links_match = re.search(
        r"<!-- phb:auto:links -->.*?<!-- /phb:auto:links -->",
        body,
        re.DOTALL,
    )
    links_block = links_match.group(0) if links_match else ""
    links_prefix = f"{links_block}\n\n" if links_block else ""
    mud_match = _MUD_BLOCK_RE.search(body)
    mud_inner = mud_match.group("body").strip() if mud_match else ""
    h = heading or title
    content = (
        format_frontmatter(fm)
        + f"# {h}\n\n"
        + f"> {source_note}\n\n"
        + links_prefix
        + f"## {PHB_SECTION}\n\n"
        + f"<!-- phb:auto:summary -->\n{summary}<!-- /phb:auto:summary -->\n\n"
        + f"## {MUD_SECTION}\n\n"
        + f"<!-- mud:implementation -->\n{mud_inner}\n<!-- /mud:implementation -->\n"
    )
    path.write_text(content, encoding="utf-8")


def simplify_chapter_introduction() -> None:
    summary = (
        "### Роль кубов\n\n"
        "- Для исходов с риском неудачи — бросок d20 + модификаторы против Сл.\n"
        "- Преимущество / помеха: два d20, лучший / худший.\n"
        "- Другие кости — урон, исцеление, случайные таблицы.\n\n"
        "### Структура игры\n\n"
        "- Мастер описывает ситуацию; игроки объявляют действия персонажей.\n"
        "- Три типа активности: **исследование** (проверки, перемещение), "
        "**социальное взаимодействие** (проверки Харизмы и др.), "
        "**сражение** (инициатива, раунды, действия).\n"
        "- Подробнее: [07-ability-scores.md](07-ability-scores.md), [09-combat.md](09-combat.md).\n\n"
        "### Не в справочнике\n\n"
        "- Советы по отыгрышу, примеры NPC и атмосферные описания — в PDF PHB.\n"
    )
    _simplify_chapter_with_links(
        RULES_DIR / "chapters" / "00-introduction.md",
        "Введение",
        "Источник: PHB, стр. 5–9. Механика кубов и структура игры.",
        summary,
    )


def simplify_chapter_character_creation() -> None:
    summary = (
        "### Шаги PHB\n\n"
        "1. Выбор расы и подрасы.\n"
        "2. Выбор класса.\n"
        "3. Определение значений характеристик.\n"
        "4. Описание персонажа (имя, внешность — ролевой слой, не механика).\n"
        "5. Выбор предыстории.\n"
        "6. Снаряжение (класс + предыстория).\n\n"
        "### Характеристики\n\n"
        "- **Стандартный массив:** 15, 14, 13, 12, 10, 8.\n"
        "- **Распределение очков:** бюджет 27 (стоимость значений 8–15 по таблице PHB).\n"
        "- **Случайный:** 4d6, отбросить низший, шесть раз; распределить по характеристикам.\n"
        "- Расовые бонусы применяются после распределения.\n\n"
        "### Ссылки\n\n"
        "- Расы: [02-races.md](02-races.md) · Классы: [03-classes.md](03-classes.md) · "
        "Предыстории: [04-backgrounds.md](04-backgrounds.md).\n"
    )
    _simplify_chapter_with_links(
        RULES_DIR / "chapters" / "01-character-creation.md",
        "Глава 1: Создание персонажа",
        "Источник: PHB, стр. 11–16. Порядок создания и методы характеристик.",
        summary,
        heading="Глава 1: Создание персонажа",
    )


def simplify_chapter_classes() -> None:
    summary = (
        "### Общие правила\n\n"
        "- Класс задаёт кость хитов, владения, спасброски, умения по уровням и "
        "момент выбора подкласса (обычно 3 ур.).\n"
        "- Мультиклассирование — опциональное правило PHB (см. [06-multiclass.md](06-multiclass.md)); "
        "в MUD **запрещено**.\n"
        "- Механика каждого класса — в карточках `entities/classes/` (таблица ниже).\n"
    )
    _simplify_chapter_with_links(
        RULES_DIR / "chapters" / "03-classes.md",
        "Классы",
        "Источник: PHB, стр. 45–120. Индекс классов.",
        summary,
    )


def simplify_chapter_subclasses() -> None:
    summary = (
        "### Подклассы (архетипы)\n\n"
        "- Подкласс выбирается на уровне, указанном в классе (чаще всего 2–3).\n"
        "- Даёт дополнительные умения на фиксированных уровнях.\n"
        "- Детали — в карточке класса (`### Подклассы`) и в `database/classes/classes.yaml` "
        "для классов в ядре MUD.\n\n"
        "### В MUD\n\n"
        "- Выбор подкласса при создании зависит от режима сложности — см. "
        "`mud:implementation` в [01-character-creation.md](01-character-creation.md).\n"
    )
    _simplify_chapter_with_links(
        RULES_DIR / "chapters" / "03-subclasses.md",
        "Подклассы",
        "Источник: PHB, гл. 3. Механика архетипов.",
        summary,
    )


ABILITY_RU: dict[str, str] = {
    "strength": "Сила",
    "dexterity": "Ловкость",
    "constitution": "Телосложение",
    "intelligence": "Интеллект",
    "wisdom": "Мудрость",
    "charisma": "Харизма",
}


def feat_requirement_text(payload: dict[str, Any]) -> str | None:
    reqs = payload.get("requirements")
    if not isinstance(reqs, list) or not reqs:
        return None
    main_parts: list[str] = []
    alt_parts: list[str] = []
    for req in reqs:
        if not isinstance(req, dict):
            continue
        rtype = req.get("type")
        if rtype == "armor_proficiency":
            armors = req.get("armors", [])
            part = f"владение {', '.join(str(a) for a in armors)} доспехами"
        elif rtype == "ability_score":
            ab_key = str(req.get("target") or req.get("ability", ""))
            ab = ABILITY_RU.get(ab_key, ab_key or "?")
            val = req.get("value", req.get("minimum", "?"))
            part = f"{ab} {val}+"
        elif rtype == "spellcasting":
            part = "способность накладывать заклинания"
        else:
            part = str(rtype)
        if req.get("alternative"):
            alt_parts.append(part)
        else:
            main_parts.append(part)
    parts = main_parts
    if alt_parts:
        parts.append(" или ".join(alt_parts))
    return "; ".join(parts) if parts else "См. feats.yaml"


def sync_feat_file(path: Path, feat_id: str, payload: dict[str, Any]) -> bool:
    name = str(payload.get("name", feat_id))
    req = feat_requirement_text(payload)
    req_row = req if req else "—"
    params = (
        "| Параметр | Значение |\n|----------|----------|\n"
        f"| Требование | {req_row} |"
    )
    body_src = str(
        payload.get("description_full") or payload.get("description") or ""
    )
    effect = bullets_from_text(body_src) or "_См. PHB PDF._\n"
    quick = str(payload.get("description", "")).strip()

    if path.is_file():
        fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    else:
        fm = {}
    fm.update(
        {
            "phb_chapter": 6,
            "phb_section": name,
            "phb_pages": [166, 172],
            "phb_part": 1,
            "id": feat_id,
            "type": "feat",
            "tags": ["feat"],
            "mud_status": fm.get("mud_status", "partial"),
            "quick": quick,
            "mud_refs": fm.get(
                "mud_refs",
                {"yaml": f"database/progression/feats.yaml#{feat_id}"},
            ),
        }
    )
    mud_inner = (
        "| Аспект | Значение |\n|--------|----------|\n"
        "| Статус | partial |\n"
        f"| YAML | `database/progression/feats.yaml#{feat_id}` |\n"
        "| Core | `core/feats.py` |\n"
    )
    content = (
        format_frontmatter(fm)
        + f"# {name}\n\n"
        + "> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.\n\n"
        + "## Параметры\n\n"
        + f"<!-- phb:auto:parameters -->\n{params}\n<!-- /phb:auto:parameters -->\n\n"
        + "## Эффект\n\n"
        + f"<!-- phb:auto:effect -->\n{effect}<!-- /phb:auto:effect -->\n\n"
        + f"## {MUD_SECTION}\n\n"
        + f"<!-- mud:implementation -->\n{mud_inner}<!-- /mud:implementation -->\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def fix_spell_higher_levels(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    hl_start = text.find("<!-- phb:auto:higher-levels -->")
    mud_start = text.find("<!-- mud:implementation -->")
    mud_end = text.find("<!-- /mud:implementation -->")
    if hl_start < 0 or mud_start < 0 or mud_end < 0:
        return False
    if not (mud_start < hl_start < mud_end):
        return False
    hl_match = re.search(
        r"<!-- phb:auto:higher-levels -->.*?<!-- /phb:auto:higher-levels -->",
        text,
        re.DOTALL,
    )
    if not hl_match:
        return False
    hl_block = hl_match.group(0)
    mud_match = _MUD_BLOCK_RE.search(text)
    if not mud_match:
        return False
    mud_inner = mud_match.group("body").replace(hl_block, "").strip()
    text_wo_hl = text.replace(hl_block, "", 1)
    mud_match2 = _MUD_BLOCK_RE.search(text_wo_hl)
    if not mud_match2:
        return False
    before_mud = text_wo_hl[: mud_match2.start()].rstrip()
    before_mud = re.sub(
        rf"\n## {re.escape(MUD_SECTION)}\s*$",
        "",
        before_mud,
    )
    text_fixed = (
        before_mud
        + "\n\n## На больших уровнях\n\n"
        + hl_block
        + "\n\n## "
        + MUD_SECTION
        + "\n\n<!-- mud:implementation -->\n"
        + mud_inner
        + "\n<!-- /mud:implementation -->\n"
    )
    path.write_text(text_fixed, encoding="utf-8")
    return True


def extract_quick_from_md(path: Path) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    quick = fm.get("quick")
    if isinstance(quick, str) and quick.strip():
        return quick.strip()
    lore_markers = (
        "мировоззрен",
        "поговорк",
        "легенд",
        "истори",
        "культур",
        "внешност",
        "идеал",
        "привязанност",
        "слабост",
        "отыгрыш",
        "физическ опис",
    )
    mechanical: list[str] = []
    for block in _AUTO_BLOCK_RE.finditer(body):
        for line in block.group("body").splitlines():
            stripped = line.strip()
            if not stripped.startswith("- "):
                continue
            content = stripped[2:]
            lower = content.lower()
            if any(m in lower for m in lore_markers):
                continue
            if any(
                k in lower
                for k in (
                    "увелич",
                    "бонус",
                    "владен",
                    "скорост",
                    "сопротивл",
                    "преимуществ",
                    "урон",
                    "спасбро",
                    "хит",
                    "заговор",
                    "заклинан",
                    "дыхан",
                    "тёмн",
                    "темн",
                    "размер",
                    "язык",
                    "навык",
                    "умение",
                    "снаряжен",
                    "инструмент",
                )
            ):
                mechanical.append(content[:160])
            if len(mechanical) >= 2:
                break
        if mechanical:
            return "; ".join(mechanical)
    return str(fm.get("phb_section", fm.get("id", "")))


def fix_spell_duplicate_mud_header(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"## {re.escape(MUD_SECTION)}\s*\n+(?=## На больших уровнях)",
    )
    new_text, n = pattern.subn("", text)
    if n:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def _spell_level_tag(level: int | str) -> str:
    if level == 0 or level == "0":
        return "cantrip"
    return f"level-{level}"


def sync_spell_from_phb(
    path: Path,
    spell_id: str,
    index_meta: dict[str, Any],
    phb: dict[str, Any],
) -> None:
    school_match = re.search(r"`(\w+)`", str(phb.get("school_label", "")))
    school = (
        school_match.group(1) if school_match else index_meta.get("school", "")
    )
    level = phb["level"]
    title = str(phb.get("title") or index_meta.get("ru", spell_id))
    params = (
        "| Параметр | Значение |\n|----------|----------|\n"
        f"| Уровень | {phb['level_label']} |\n"
        f"| Школа | {phb['school_label']} |\n"
        f"| Время | {phb['casting_time']} |\n"
        f"| Дистанция | {phb['range']} |\n"
        f"| Компоненты | {phb['components']} |\n"
        f"| Длительность | {phb['duration']} |"
    )
    effect = effect_to_bullets(phb.get("effect_lines") or [])
    higher = phb.get("higher_levels")
    if path.is_file():
        fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    else:
        fm = {}
    tags = ["spell"]
    if school:
        tags.append(str(school))
    tags.append(_spell_level_tag(level))
    fm.update(
        {
            "phb_chapter": 11,
            "phb_section": title,
            "phb_pages": [211, 289],
            "phb_part": 3,
            "id": spell_id,
            "type": "spell",
            "tags": tags,
            "mud_status": fm.get("mud_status", "planned"),
        }
    )
    mud_inner = (
        "| Аспект | Значение |\n|--------|----------|\n"
        f"| Статус | {fm.get('mud_status', 'planned')} |\n"
        "| YAML | — |\n"
        "| Core | — |\n"
    )
    higher_block = ""
    if higher:
        higher_block = (
            "## На больших уровнях\n\n"
            f"<!-- phb:auto:higher-levels -->\n{higher}\n"
            "<!-- /phb:auto:higher-levels -->\n\n"
        )
    content = (
        format_frontmatter(fm)
        + f"# {title}\n\n"
        + "> Источник: PHB, гл. 11. Пересказ правил, не дословная копия PHB.\n\n"
        + "## Параметры\n\n"
        + f"<!-- phb:auto:parameters -->\n{params}\n<!-- /phb:auto:parameters -->\n\n"
        + "## Эффект\n\n"
        + f"<!-- phb:auto:effect -->\n{effect}<!-- /phb:auto:effect -->\n\n"
        + higher_block
        + f"## {MUD_SECTION}\n\n"
        + f"<!-- mud:implementation -->\n{mud_inner}<!-- /mud:implementation -->\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sync_all_spells_from_phb() -> int:
    if not DEFAULT_PDF.is_file():
        return 0
    text = extract_pdf_text()
    parsed = parse_spell_descriptions(text)
    index = load_spells_index(RULES_DIR)
    mapped = map_parsed_to_ids(parsed, index)
    for spell_id, phb in mapped.items():
        meta = index.get(spell_id, {})
        if not isinstance(meta, dict):
            continue
        path = RULES_DIR / "entities" / "spells" / f"{spell_id}.md"
        sync_spell_from_phb(path, spell_id, meta, phb)
    return len(mapped)


def build_lookup() -> dict[str, Any]:
    entities_path = RULES_DIR / "_index" / "entities.yaml"
    spells_path = RULES_DIR / "_index" / "spells.yaml"
    entities_data = (
        yaml.safe_load(entities_path.read_text(encoding="utf-8")) or {}
    )
    spells_data = yaml.safe_load(spells_path.read_text(encoding="utf-8")) or {}
    entities: dict[str, Any] = entities_data.get("entities", {})
    spells: dict[str, Any] = spells_data.get("spells", {})

    by_id: dict[str, Any] = {}
    by_alias: dict[str, str] = {}

    for entity_id, meta in entities.items():
        if not isinstance(meta, dict):
            continue
        file_rel = str(meta.get("file", ""))
        path = RULES_DIR / file_rel
        quick = extract_quick_from_md(path)
        entry = {
            "type": meta.get("type"),
            "ru": meta.get("ru"),
            "en": meta.get("en", entity_id),
            "file": file_rel,
            "pages": meta.get("pages"),
            "mud_status": meta.get("mud_status"),
            "quick": quick,
        }
        by_id[entity_id] = entry
        for alias in meta.get("aliases", []) or []:
            by_alias[str(alias).lower()] = entity_id
        by_alias[str(entity_id).lower()] = entity_id
        if meta.get("ru"):
            by_alias[str(meta["ru"]).lower()] = entity_id

    for spell_id, meta in spells.items():
        if not isinstance(meta, dict):
            continue
        file_rel = str(meta.get("file", ""))
        path = RULES_DIR / file_rel
        quick = extract_quick_from_md(path)
        entry = {
            "type": "spell",
            "ru": meta.get("ru"),
            "en": spell_id,
            "file": file_rel,
            "level": meta.get("level"),
            "school": meta.get("school"),
            "mud_status": "planned",
            "quick": quick,
        }
        by_id[spell_id] = entry
        for alias in meta.get("aliases", []) or []:
            by_alias[str(alias).lower()] = spell_id
        by_alias[str(spell_id).lower()] = spell_id
        if meta.get("ru"):
            by_alias[str(meta["ru"]).lower()] = spell_id

    summaries = {
        k: v.get("quick", "") for k, v in by_id.items() if v.get("quick")
    }

    return {
        "layout": INDEX_LAYOUT,
        "by_id": by_id,
        "by_alias": by_alias,
        "summaries": summaries,
    }


def simplify_chapter_feats() -> None:
    path = RULES_DIR / "chapters" / "06-feats.md"
    if not path.is_file():
        return
    fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    links_match = re.search(
        r"<!-- phb:auto:links -->.*?<!-- /phb:auto:links -->",
        body,
        re.DOTALL,
    )
    links_block = links_match.group(0) if links_match else ""
    summary = (
        "### Общие правила\n\n"
        "- Черты — опциональная замена умения «Улучшение характеристик» на некоторых уровнях.\n"
        "- Каждую черту можно взять **один раз**, если в описании не указано иное.\n"
        "- Требования черты проверяются **в момент выбора**; при их потере эффект не работает.\n"
        "- Механика каждой черты — в карточках `entities/feats/` (таблица ниже).\n"
    )
    mud_inner = (
        "| Аспект | Значение |\n|--------|----------|\n"
        f"| Статус | {fm.get('mud_status', 'partial')} |\n"
        "| YAML | `database/progression/feats.yaml` |\n"
        "| Core | `core/feats.py`, `core/feat_requirements.py` |\n"
        "| UI | `ui/menus/feats/` |\n"
        "| Детали | `docs/API.md` §core.feats |\n\n"
        "### Фильтрация списка\n\n"
        "`list_feats_for_selection` возвращает три группы:\n\n"
        "| Группа | Условие | UI |\n"
        "|--------|---------|----|\n"
        "| **eligible** | Требования выполнены и черта даёт **новые** владения | Выбираемые |\n"
        "| **blocked** | Требования не выполнены | Показ с причиной, не выбираются |\n"
        "| **hidden** | Требования OK, но владения уже есть (раса/класс/другие черты) | "
        "Секция «Скрыто» в конце списка |\n\n"
        "Уже взятые черты не возвращаются.\n\n"
        "### Запланировано (Phase 2)\n\n"
        "- Постоянная проверка требований в runtime: `feat_is_active`, "
        "`active_feat_ids`, `feat_requirement_context_from_character`.\n"
        "- Потеря требований (смена доспехов и т.п.) отключает эффект черты.\n"
    )
    content = (
        format_frontmatter(fm)
        + "# Черты\n\n"
        + "> Источник: PHB, стр. 166–172. Пересказ правил.\n\n"
        + links_block
        + "\n\n"
        + f"## {PHB_SECTION}\n\n"
        + f"<!-- phb:auto:summary -->\n{summary}<!-- /phb:auto:summary -->\n\n"
        + f"## {MUD_SECTION}\n\n"
        + f"<!-- mud:implementation -->\n{mud_inner}<!-- /mud:implementation -->\n"
    )
    path.write_text(content, encoding="utf-8")


def update_toc_agent_entry() -> None:
    toc_path = RULES_DIR / "toc.yaml"
    toc = yaml.safe_load(toc_path.read_text(encoding="utf-8")) or {}
    toc["layout"] = INDEX_LAYOUT
    toc["agent_entry"] = {
        "readme": "README.md",
        "lookup": "_index/lookup.yaml",
        "entities_index": "_index/entities.yaml",
        "spells_index": "_index/spells.yaml",
        "spell_by_level": "_index/spells/by-level.md",
        "spell_by_school": "_index/spells/by-school.md",
    }
    toc_path.write_text(
        yaml.dump(toc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def main() -> int:
    counts = {
        "feats": 0,
        "spells_synced": 0,
        "spells_fixed": 0,
        "races": 0,
        "backgrounds": 0,
        "classes": 0,
    }
    feats = load_feats()
    for feat_id, payload in feats.items():
        path = RULES_DIR / "entities" / "feats" / f"{feat_id}.md"
        sync_feat_file(path, feat_id, payload)
        counts["feats"] += 1

    counts["races"] = sync_all_race_cards()
    counts["backgrounds"] = sync_all_backgrounds()
    counts["classes"] = sync_all_class_cards()

    counts["spells_synced"] = sync_all_spells_from_phb()

    for spell_path in (RULES_DIR / "entities" / "spells").glob("*.md"):
        if fix_spell_higher_levels(spell_path):
            counts["spells_fixed"] += 1
        if fix_spell_duplicate_mud_header(spell_path):
            counts["spells_fixed"] += 1

    simplify_chapter_introduction()
    simplify_chapter_character_creation()
    simplify_chapter_races()
    simplify_chapter_classes()
    simplify_chapter_subclasses()
    simplify_chapter_backgrounds()
    simplify_chapter_feats()
    lookup = build_lookup()
    index_dir = RULES_DIR / "_index"
    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / "lookup.yaml").write_text(
        yaml.dump(lookup, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    summaries_only = {
        "layout": INDEX_LAYOUT,
        "summaries": lookup["summaries"],
    }
    (index_dir / "summaries.yaml").write_text(
        yaml.dump(summaries_only, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    for name in ("entities.yaml", "spells.yaml", "aliases.yaml"):
        p = index_dir / name
        if p.is_file():
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            data["layout"] = INDEX_LAYOUT
            p.write_text(
                yaml.dump(data, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )

    update_toc_agent_entry()
    print(f"build_rules_index: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
