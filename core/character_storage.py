"""Сохранение и загрузка персонажей в JSON."""

import json
from datetime import UTC, datetime
from pathlib import Path

from core.levels import clamp_level
from core.models import Character
from core.progression import max_hp_for_level
from core.slug import make_save_slug
from core.stats import STANDARD_ARRAY, generate_stats_standard_array
from core.subclasses import start_level_for_difficulty
from core.types import GameDifficulty, StatMap


def starting_max_hp(
    class_id: str,
    stats: StatMap,
    difficulty: GameDifficulty = "normal",
) -> int:
    """Максимум хитов на 1 уровне с учётом режима сложности."""
    return max_hp_for_level(class_id, stats, 1, difficulty)


def save_character(
    name: str,
    race_id: str,
    class_id: str,
    difficulty: GameDifficulty = "normal",
    subrace_id: str | None = None,
    stats: StatMap | None = None,
    subclass_id: str | None = None,
    languages: list[str] | None = None,
    background_id: str | None = None,
    skills: list[str] | None = None,
    skill_expertise: list[str] | None = None,
    tool_expertise: list[str] | None = None,
    weapon_proficiencies: list[str] | None = None,
    armor_proficiencies: list[str] | None = None,
    tool_proficiencies: list[str] | None = None,
    feat_ids: list[str] | None = None,
    level: int | None = None,
    class_features_applied: bool = False,
) -> Character:
    """Создать нового персонажа и сохранить в JSON."""
    if stats is None:
        stats = generate_stats_standard_array(
            list(STANDARD_ARRAY), race_id, subrace_id
        )

    if level is None:
        level = start_level_for_difficulty(difficulty)
    level = clamp_level(level)

    hp = max_hp_for_level(class_id, stats, level, difficulty)

    character = Character(
        name=name,
        race=race_id,
        class_name=class_id,
        level=level,
        stats=stats,
        current_hp=hp,
        max_hp=hp,
        experience=0,
        difficulty=difficulty,
        subrace=subrace_id,
        subclass_id=subclass_id,
        languages=list(languages) if languages else [],
        background_id=background_id,
        skills=list(skills) if skills else [],
        skill_expertise=list(skill_expertise) if skill_expertise else [],
        tool_expertise=list(tool_expertise) if tool_expertise else [],
        weapon_proficiencies=(
            list(weapon_proficiencies) if weapon_proficiencies else []
        ),
        armor_proficiencies=(
            list(armor_proficiencies) if armor_proficiencies else []
        ),
        tool_proficiencies=(
            list(tool_proficiencies) if tool_proficiencies else []
        ),
        feat_ids=list(feat_ids) if feat_ids else [],
        class_features_applied=class_features_applied,
        save_slug=_unique_save_slug(name),
        created_at=datetime.now(UTC).isoformat(),
    )

    _save_character_file(character)

    return character


def update_character(character: Character) -> None:
    """Обновить существующего персонажа в JSON."""
    character.level = clamp_level(character.level)
    _save_character_file(character)


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


def _character_created_at_timestamp(character: Character, path: Path) -> float:
    """Метка времени создания: из JSON или mtime для старых сохранений."""
    if character.created_at:
        try:
            return datetime.fromisoformat(character.created_at).timestamp()
        except ValueError:
            pass
    return path.stat().st_mtime


def load_characters() -> list[Character]:
    """Загрузить список всех сохранённых персонажей (старые → новые)."""
    if not CHARACTERS_DIR.exists():
        return []

    entries: list[tuple[float, Character]] = []
    for path in CHARACTERS_DIR.glob("*.json"):
        character = _load_character_file(path)
        if character is not None:
            entries.append(
                (_character_created_at_timestamp(character, path), character)
            )

    entries.sort(key=lambda item: item[0])
    return [character for _, character in entries]


def delete_character(save_slug: str) -> bool:
    """Удалить JSON-файл персонажа. False, если файла нет."""
    path = _character_file_path(save_slug)
    if not path.exists():
        return False
    path.unlink()
    return True


def delete_all_characters() -> int:
    """Удалить всех персонажей. Возвращает число удалённых файлов."""
    if not CHARACTERS_DIR.exists():
        return 0

    deleted = 0
    for path in CHARACTERS_DIR.glob("*.json"):
        path.unlink()
        deleted += 1
    return deleted
