# Changelog — dnd_mud

## [Unreleased]

### Added
- Интерактивная генерация характеристик в создании персонажа (standard array, point-buy, 4d6, HardCore)
- Локализация экрана генерации характеристик (en/ru)
- Unit-тест `generate_stats_random` (регрессия API)

### Fixed
- TypeError при случайной и HardCore генерации характеристик (`difficulty=` в вызове `generate_stats_random`)

### Changed
- Документация: режимы сложности игры (Normal / HardCore / planned Easy), акцент HardCore, разведение game mode vs content tier в adventures.yaml (MUD_PRD §3.2.1, API, ARCHITECTURE, DEVELOPMENT, README)
- Документация: flow создания персонажа (характеристики → класс), детализация генерации характеристик (MUD_PRD §3.4.5, API, ARCHITECTURE, DEVELOPMENT, README)
- Реорганизация `database/`: справочники в подпапках (`races/`, `classes/`, `content/`, `core/`, `equipment/`, `progression/`)
- Mutable state переведён на JSON: `database/core/settings.json`, `saves/characters.json`
- Полная переработка `docs/API.md`; синхронизированы README, DEVELOPMENT, MUD_PRD, ARCHITECTURE, AGENTS.md

### Removed
- Устаревшие плоские пути (`database/races.yaml`, `database/settings.yaml` и др.)
- `database/progression/characters.yaml` (заменён на `saves/characters.json`)
