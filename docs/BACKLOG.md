# Backlog — dnd_mud

> Выполненное фиксируется только в [CHANGELOG.md](CHANGELOG.md). Этот файл — **открытые** задачи.

## Pre-Alpha (открыто)

| ID | Задача | Ссылки |
|----|--------|--------|
| `load-game` | Flow «Загрузить игру»: список сейвов → загрузка состояния | [MUD_PRD.md](MUD_PRD.md) §3.2, §10 |
| `terminal-wrap` | Перенос текста при изменении ширины терминала | [MUD_PRD.md](MUD_PRD.md) §10 |
| `mod-gating` | `requires_game_difficulty` в manifest модов | [MUD_PRD.md](MUD_PRD.md) §5.4, [DEVELOPMENT.md](DEVELOPMENT.md) |
| `mod-menu` | Отдельный пункт меню «Модификации» (опционально) | [DEVELOPMENT.md](DEVELOPMENT.md) |
| `mod-runtime` | Перезагрузка каталогов при смене модов без перезапуска интерпретатора | [DEVELOPMENT.md](DEVELOPMENT.md) |

## Phase 2 (запланировано)

Не backlog рефакторинга — см. [MUD_PRD.md](MUD_PRD.md) §«Нереализованная механика D&D 5e» и [DATA_SCHEMA.md](DATA_SCHEMA.md) §«Запланировано (Phase 2+)».

- Game engine (комнаты, проверки, бой)
- Автосохранение / загрузка сессии приключения
- Инвентарь, стартовое снаряжение, ongoing-требования черт

## Жизненный цикл

1. Новая задача → строка в таблице Pre-Alpha.
2. Задача закрыта → **удалить** из этого файла → запись в `CHANGELOG.md` (`[Unreleased]` или релиз).
