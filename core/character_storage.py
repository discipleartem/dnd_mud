"""Сохранение и загрузка персонажей в JSON."""

import json
from pathlib import Path

from core.classes import get_class_hit_dice
from core.dice import ability_modifier
from core.models import Character
from core.slug import make_save_slug
from core.stats import (
    STANDARD_ARRAY,
    STAT_NAMES,
    apply_racial_bonuses_to_stats,
)


def save_character(
    name: str,
    race_id: str,
    class_id: str,
    difficulty: str = "normal",
    subrace_id: str | None = None,
    stats: dict[str, int] | None = None,
) -> Character:
    """Создать нового персонажа и сохранить в JSON."""
    if stats is None:
        stats = dict(zip(STAT_NAMES, STANDARD_ARRAY, strict=False))
        stats = apply_racial_bonuses_to_stats(stats, race_id, subrace_id)

    hit_dice = get_class_hit_dice(class_id)
    con_mod = ability_modifier(stats.get("constitution", 10))
    hp = hit_dice + con_mod

    character = Character(
        name=name,
        race=race_id,
        class_name=class_id,
        level=1,
        stats=stats,
        current_hp=hp,
        experience=0,
        difficulty=difficulty,
        subrace=subrace_id,
        save_slug=_unique_save_slug(name),
    )

    _save_character_file(character)

    return character


SAVES_DIR = Path("saves")
CHARACTERS_DIR = SAVES_DIR / "characters"
CHARACTERS_SCHEMA_VERSION = 1


def _existing_save_slugs() -> set[str]:
    """Собрать save_slug из имён файлов и содержимого JSON."""
    slugs: set[str] = set()
    if not CHARACTERS_DIR.exists():
        return slugs

    for path in CHARACTERS_DIR.glob("*.json"):
        slugs.add(path.stem)
        character = _load_character_file(path)
        if character is not None and character.save_slug:
            slugs.add(character.save_slug)
    return slugs


def _unique_save_slug(name: str) -> str:
    """Уникальный save_slug для нового персонажа."""
    base = make_save_slug(name)
    existing = _existing_save_slugs()
    if base not in existing:
        return base

    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _character_file_path(save_slug: str) -> Path:
    """Путь к JSON-файлу персонажа."""
    return CHARACTERS_DIR / f"{save_slug}.json"


def _save_character_file(character: Character) -> None:
    """Сохранить одного персонажа в отдельный JSON-файл."""
    if not character.save_slug:
        raise ValueError("У персонажа должен быть save_slug")

    CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": CHARACTERS_SCHEMA_VERSION,
        **character.to_dict(),
    }
    path = _character_file_path(character.save_slug)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_character_file(path: Path) -> Character | None:
    """Загрузить одного персонажа из JSON-файла."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or not data.get("name"):
            return None

        character = Character.from_dict(data)
        if not character.save_slug:
            character.save_slug = path.stem
        return character
    except (json.JSONDecodeError, OSError):
        return None


def load_characters() -> list[Character]:
    """Загрузить список всех сохранённых персонажей."""
    if not CHARACTERS_DIR.exists():
        return []

    characters: list[Character] = []
    for path in sorted(CHARACTERS_DIR.glob("*.json")):
        character = _load_character_file(path)
        if character is not None:
            characters.append(character)

    characters.sort(key=lambda c: c.name.lower())
    return characters
