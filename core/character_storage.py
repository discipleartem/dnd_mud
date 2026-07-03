"""Сохранение и загрузка персонажей в JSON."""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from core.character_build import build_new_character as _build_new_character
from core.character_migrate import (
    CHARACTERS_SCHEMA_VERSION,
    migrate_character_data,
)
from core.io import load_json, save_json
from core.levels import clamp_level
from core.models import Character
from core.slug import make_save_slug
from core.types import CharacterClass, GameDifficulty, StatMap

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoadCharactersResult:
    """Результат загрузки персонажей и предупреждений о битых сейвах."""

    characters: tuple[Character, ...]
    corrupt_save_warnings: tuple[str, ...] = ()

    @classmethod
    def empty(cls) -> "LoadCharactersResult":
        """Пустой результат без персонажей и предупреждений."""
        return cls(characters=())


def _corrupt_label_from_data(data: dict[str, Any], path: Path) -> str:
    """Имя персонажа из JSON или save_slug, если имя недоступно."""
    name = data.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return path.stem


def _try_load_character_file(
    path: Path,
) -> tuple[Character | None, str | None]:
    """Загрузить персонажа; при битом сейве — (None, подпись)."""
    if not path.exists():
        return None, None
    try:
        if path.stat().st_size == 0:
            return None, path.stem
        data = load_json(path)
        data = migrate_character_data(data)
        if not data.get("name"):
            return None, path.stem
        try:
            character = Character.from_dict(data)
        except (ValueError, TypeError):
            return None, _corrupt_label_from_data(data, path)
        if not character.save_slug:
            character.save_slug = path.stem
        return character, None
    except OSError:
        return None, path.stem


def build_new_character(
    name: str,
    race_id: str,
    class_id: str | CharacterClass,
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
    background_tool_picks: list[str] | None = None,
    feat_ids: list[str] | None = None,
    feat_choices: dict[str, dict[str, Any]] | None = None,
    asi_choices: dict[str, str] | None = None,
    save_proficiencies: list[str] | None = None,
    inventory: list[dict[str, Any]] | None = None,
    equipment_choices: dict[str, str] | None = None,
    level: int | None = None,
    class_features_applied: bool = False,
    apply_feat_stat_bonuses: bool = True,
) -> Character:
    """Собрать нового персонажа без записи на диск."""
    return _build_new_character(
        name=name,
        race_id=race_id,
        class_id=class_id,
        difficulty=difficulty,
        subrace_id=subrace_id,
        stats=stats,
        subclass_id=subclass_id,
        languages=languages,
        background_id=background_id,
        skills=skills,
        skill_expertise=skill_expertise,
        tool_expertise=tool_expertise,
        weapon_proficiencies=weapon_proficiencies,
        armor_proficiencies=armor_proficiencies,
        tool_proficiencies=tool_proficiencies,
        background_tool_picks=background_tool_picks,
        feat_ids=feat_ids,
        feat_choices=feat_choices,
        asi_choices=asi_choices,
        save_proficiencies=save_proficiencies,
        inventory=inventory,
        equipment_choices=equipment_choices,
        level=level,
        class_features_applied=class_features_applied,
        apply_feat_stat_bonuses=apply_feat_stat_bonuses,
        unique_save_slug=_unique_save_slug,
    )


def persist_character(character: Character) -> Character:
    """Записать персонажа на диск."""
    _save_character_file(character)
    return character


def save_character(
    name: str,
    race_id: str,
    class_id: str | CharacterClass,
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
    background_tool_picks: list[str] | None = None,
    feat_ids: list[str] | None = None,
    feat_choices: dict[str, dict[str, Any]] | None = None,
    asi_choices: dict[str, str] | None = None,
    save_proficiencies: list[str] | None = None,
    inventory: list[dict[str, Any]] | None = None,
    equipment_choices: dict[str, str] | None = None,
    level: int | None = None,
    class_features_applied: bool = False,
    apply_feat_stat_bonuses: bool = True,
) -> Character:
    """Создать нового персонажа и сохранить в JSON."""
    return persist_character(
        build_new_character(
            name=name,
            race_id=race_id,
            class_id=class_id,
            difficulty=difficulty,
            subrace_id=subrace_id,
            stats=stats,
            subclass_id=subclass_id,
            languages=languages,
            background_id=background_id,
            skills=skills,
            skill_expertise=skill_expertise,
            tool_expertise=tool_expertise,
            weapon_proficiencies=weapon_proficiencies,
            armor_proficiencies=armor_proficiencies,
            tool_proficiencies=tool_proficiencies,
            background_tool_picks=background_tool_picks,
            feat_ids=feat_ids,
            feat_choices=feat_choices,
            asi_choices=asi_choices,
            save_proficiencies=save_proficiencies,
            inventory=inventory,
            equipment_choices=equipment_choices,
            level=level,
            class_features_applied=class_features_applied,
            apply_feat_stat_bonuses=apply_feat_stat_bonuses,
        )
    )


def update_character(character: Character) -> None:
    """Обновить существующего персонажа в JSON."""
    character.level = clamp_level(character.level)
    _save_character_file(character)


SAVES_DIR = Path("saves")
CHARACTERS_DIR = SAVES_DIR / "characters"


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
    path = _character_file_path(character.save_slug)
    save_json(
        path,
        {
            "schema_version": CHARACTERS_SCHEMA_VERSION,
            **character.to_dict(),
        },
    )


def _load_character_file(path: Path) -> Character | None:
    """Загрузить одного персонажа из JSON-файла."""
    character, _corrupt_label = _try_load_character_file(path)
    return character


def _character_created_at_timestamp(character: Character, path: Path) -> float:
    """Метка времени создания: из JSON или mtime для старых сохранений."""
    if character.created_at:
        try:
            return datetime.fromisoformat(character.created_at).timestamp()
        except ValueError:
            pass
    return path.stat().st_mtime


def load_characters() -> LoadCharactersResult:
    """Загрузить всех сохранённых персонажей (старые → новые) и битые сейвы."""
    if not CHARACTERS_DIR.exists():
        return LoadCharactersResult.empty()

    entries: list[tuple[float, Character]] = []
    corrupt_labels: list[str] = []
    for path in CHARACTERS_DIR.glob("*.json"):
        character, corrupt_label = _try_load_character_file(path)
        if character is not None:
            entries.append(
                (_character_created_at_timestamp(character, path), character)
            )
        elif corrupt_label is not None:
            logger.warning("Битый файл сохранения персонажа: %s", path)
            corrupt_labels.append(corrupt_label)

    entries.sort(key=lambda item: item[0])
    return LoadCharactersResult(
        characters=tuple(character for _, character in entries),
        corrupt_save_warnings=tuple(corrupt_labels),
    )


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
