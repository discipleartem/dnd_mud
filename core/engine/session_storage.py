"""Сохранение и загрузка сессий приключений."""

import contextlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.catalogs.adventure import Adventure
from core.character.models import Character
from core.character.storage import CHARACTERS_DIR, try_load_character_file
from core.platform.io import load_json, save_json
from core.types import GameDifficulty

SESSIONS_SCHEMA_VERSION = 1
SESSIONS_DIR = Path("saves") / "sessions"


@dataclass
class SessionSnapshot:
    """Снимок сессии для JSON."""

    save_slug: str
    character_save_slug: str
    adventure_id: str
    current_node_id: str | None
    difficulty: GameDifficulty
    flags: dict[str, Any] = field(default_factory=dict)
    script_file: str = ""
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Сериализация в JSON."""
        data: dict[str, Any] = {
            "save_slug": self.save_slug,
            "character_save_slug": self.character_save_slug,
            "adventure_id": self.adventure_id,
            "current_node_id": self.current_node_id,
            "difficulty": self.difficulty,
            "flags": self.flags,
            "script_file": self.script_file,
        }
        if self.updated_at:
            data["updated_at"] = self.updated_at
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionSnapshot":
        """Десериализация из JSON."""
        return cls(
            save_slug=str(data.get("save_slug", "")),
            character_save_slug=str(data.get("character_save_slug", "")),
            adventure_id=str(data.get("adventure_id", "")),
            current_node_id=(
                str(data["current_node_id"])
                if data.get("current_node_id") is not None
                else None
            ),
            difficulty=_parse_difficulty(data.get("difficulty", "normal")),
            flags=(
                dict(data.get("flags", {}))
                if isinstance(data.get("flags"), dict)
                else {}
            ),
            script_file=str(data.get("script_file", "")),
            updated_at=(
                str(data["updated_at"])
                if data.get("updated_at") is not None
                else None
            ),
        )


def _parse_difficulty(raw: object) -> GameDifficulty:
    if raw == "hardcore":
        return "hardcore"
    if raw == "easy":
        return "easy"
    return "normal"


def _session_path(save_slug: str) -> Path:
    return SESSIONS_DIR / f"{save_slug}.json"


def list_sessions() -> list[SessionSnapshot]:
    """Все сохранённые сессии (старые → новые)."""
    if not SESSIONS_DIR.exists():
        return []
    entries: list[tuple[float, SessionSnapshot]] = []
    for path in SESSIONS_DIR.glob("*.json"):
        try:
            data = load_json(path)
            snapshot = SessionSnapshot.from_dict(data)
            if not snapshot.save_slug:
                snapshot = SessionSnapshot.from_dict(
                    {**data, "save_slug": path.stem}
                )
            ts = path.stat().st_mtime
            if snapshot.updated_at:
                with contextlib.suppress(ValueError):
                    ts = datetime.fromisoformat(
                        snapshot.updated_at
                    ).timestamp()
            entries.append((ts, snapshot))
        except OSError:
            continue
    entries.sort(key=lambda item: item[0])
    return [snapshot for _, snapshot in entries]


def save_session(snapshot: SessionSnapshot) -> None:
    """Сохранить снимок сессии."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    payload = snapshot.to_dict()
    payload["schema_version"] = SESSIONS_SCHEMA_VERSION
    payload["updated_at"] = datetime.now(UTC).isoformat()
    save_json(_session_path(snapshot.save_slug), payload)


def load_session(save_slug: str) -> SessionSnapshot | None:
    """Загрузить снимок сессии."""
    path = _session_path(save_slug)
    if not path.exists():
        return None
    try:
        data = load_json(path)
        return SessionSnapshot.from_dict(data)
    except OSError:
        return None


def delete_session(save_slug: str) -> bool:
    """Удалить файл сессии."""
    path = _session_path(save_slug)
    if not path.exists():
        return False
    path.unlink()
    return True


def load_character_for_session(
    snapshot: SessionSnapshot,
    characters_dir: Path | None = None,
) -> Character | None:
    """Загрузить персонажа сессии из ``saves/characters/``."""
    base = characters_dir if characters_dir is not None else CHARACTERS_DIR
    path = base / f"{snapshot.character_save_slug}.json"
    character, _corrupt = try_load_character_file(path)
    return character


def find_adventure(
    adventures: list[Adventure], adventure_id: str
) -> Adventure | None:
    """Найти приключение по id."""
    for adventure in adventures:
        if adventure.id == adventure_id:
            return adventure
    return None
