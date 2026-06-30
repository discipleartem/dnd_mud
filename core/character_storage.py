"""Сохранение и загрузка персонажей в JSON."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.io import load_json, save_json
from core.levels import clamp_level
from core.models import Character
from core.progression import max_hp_for_level
from core.slug import make_save_slug
from core.stats import STANDARD_ARRAY, generate_stats_standard_array
from core.subclasses import start_level_for_difficulty
from core.types import GameDifficulty, StatMap

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
    feat_choices: dict[str, dict[str, Any]] | None = None,
    asi_choices: dict[str, str] | None = None,
    level: int | None = None,
    class_features_applied: bool = False,
    apply_feat_stat_bonuses: bool = True,
) -> Character:
    """Создать нового персонажа и сохранить в JSON.

    ``apply_feat_stat_bonuses=False`` — если ``stats`` уже содержат бонусы
    черт (flow создания после ``select_creation_feats``).
    """
    if stats is None:
        stats = generate_stats_standard_array(
            list(STANDARD_ARRAY), race_id, subrace_id
        )
    if feat_ids:
        from core.character_builder import (
            merge_expertise_with_feats,
            merge_languages_with_feats,
        )
        from core.feats import apply_feats_to_stats

        if apply_feat_stat_bonuses:
            stats = apply_feats_to_stats(stats, feat_ids, feat_choices)
        languages = merge_languages_with_feats(
            languages, feat_ids, feat_choices
        )
        skill_expertise = merge_expertise_with_feats(
            skill_expertise, feat_ids, feat_choices
        )

    if level is None:
        level = start_level_for_difficulty(difficulty)
    level = clamp_level(level)

    need_grants = (
        weapon_proficiencies is None
        or armor_proficiencies is None
        or tool_proficiencies is None
        or skills is None
    )
    if need_grants:
        from core.character_builder import resolve_creation_grants

        grants = resolve_creation_grants(
            race_id,
            subrace_id,
            class_id,
            background_id,
            subclass_id,
            level,
            feat_ids=feat_ids,
            feat_choices=feat_choices,
            include_feat_languages=False,
        )
        if weapon_proficiencies is None:
            weapon_proficiencies = list(grants.weapon_tokens)
        if armor_proficiencies is None:
            armor_proficiencies = list(grants.armor_tokens)
        if tool_proficiencies is None:
            tool_proficiencies = list(grants.tool_tokens)
        if skills is None:
            skills = list(grants.skill_ids)

    hp = max_hp_for_level(
        class_id,
        stats,
        level,
        difficulty,
        race_id,
        subrace_id,
        feat_ids,
    )

    character = Character(
        name=name,
        race=race_id,
        class_id=class_id,
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
        feat_choices=dict(feat_choices) if feat_choices else {},
        asi_choices=dict(asi_choices) if asi_choices else {},
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
