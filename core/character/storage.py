"""Сохранение и загрузка персонажей в JSON."""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from core.character.migrate import (
    CHARACTERS_SCHEMA_VERSION,
    migrate_character_data,
)
from core.character.models import Character
from core.constants import clamp_level
from core.platform.io import load_json, save_json

logger = logging.getLogger(__name__)

_CYRILLIC_TO_LATIN: dict[str, str] = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
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


def _transliterate(text: str) -> str:
    """Транслитерировать кириллицу в латиницу."""
    result: list[str] = []
    for char in text:
        lower = char.lower()
        if lower in _CYRILLIC_TO_LATIN:
            mapped = _CYRILLIC_TO_LATIN[lower]
            if char.isupper() and mapped:
                mapped = mapped[0].upper() + mapped[1:]
            result.append(mapped)
        else:
            result.append(char)
    return "".join(result)


def make_save_slug(name: str) -> str:
    """Построить slug из имени персонажа."""
    transliterated = _transliterate(name).lower()
    slug = re.sub(r"[^a-z0-9]+", "_", transliterated)
    slug = slug.strip("_")
    return slug or "character"


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


def try_load_character_file(
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


def persist_character(character: Character) -> Character:
    """Записать персонажа на диск."""
    _save_character_file(character)
    return character


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


def unique_save_slug(name: str) -> str:
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
    character, _corrupt_label = try_load_character_file(path)
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
        character, corrupt_label = try_load_character_file(path)
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
