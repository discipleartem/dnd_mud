# Backlog — dnd_mud

> Выполненное фиксируется только в [CHANGELOG.md](CHANGELOG.md). Этот файл — **открытые** задачи.

## Pre-Alpha (открыто)

_Нет открытых задач Pre-Alpha._

## Phase 2 (запланировано)

Не backlog рефакторинга — см. [MUD_PRD.md](MUD_PRD.md) §«Нереализованная механика D&D 5e» и [DATA_SCHEMA.md](DATA_SCHEMA.md) §«Запланировано (Phase 2+)».

- Game engine: бой, комнаты, полная параметризация по режиму (скелет `core/game_engine.py` и проверки — есть)
- Инвентарь, стартовое снаряжение, ongoing-требования черт — **реализовано** (см. CHANGELOG)

_Закрыто в refactor:_ автосохранение/загрузка сессии (`saves/sessions/`, `load_game`), mod gating, terminal wrap.

## Жизненный цикл

1. Новая задача → строка в таблице Pre-Alpha.
2. Задача закрыта → **удалить** из этого файла → запись в `CHANGELOG.md` (`[Unreleased]` или релиз).
