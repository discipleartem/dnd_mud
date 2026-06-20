# Changelog — dnd_mud

## [Unreleased]

### Added
- Интерактивная генерация характеристик в создании персонажа (standard array, point-buy, 4d6, HardCore)
- Локализация экрана генерации характеристик (en/ru)
- Unit-тест `generate_stats_random` (регрессия API)

### Fixed
- TypeError при случайной и HardCore генерации характеристик (`difficulty=` в вызове `generate_stats_random`)
- Doc drift: settings, phantom modules, legacy APIs синхронизированы с кодом

### Changed
- Документация синхронизирована с кодом: `core/difficulty.py`, flow «Новая игра» без выбора сложности, 54 теста в 11 файлах, Phase 2 в `database/_future/`, фильтр приключений в UI
- Персонажи сохраняются в отдельных файлах `saves/characters/{save_slug}.json`
- Документация: режимы сложности игры (Normal / HardCore / planned Easy), акцент HardCore, разведение game mode vs content tier в adventures.yaml (MUD_PRD §3.2.1, API, ARCHITECTURE, DEVELOPMENT, README)
- Документация: flow создания персонажа (характеристики → класс), детализация генерации характеристик (MUD_PRD §3.4.5, API, ARCHITECTURE, DEVELOPMENT, README)
- Реорганизация `database/`: справочники в подпапках (`races/`, `classes/`, `content/`, `core/`)
- Mutable state переведён на JSON: `database/core/settings.json`, `saves/characters/*.json`
- Полная переработка `docs/API.md`; синхронизированы README, DEVELOPMENT, MUD_PRD, ARCHITECTURE, AGENTS.md

### Removed
- Устаревшие плоские пути (`database/races.yaml`, `database/settings.yaml` и др.)
- `database/progression/characters.yaml` (заменён на per-file saves)
- Монолитный `saves/characters.json` (заменён per-file saves; авто-миграции нет)
- `generate_stats_hardcore()` (дублировала UI-путь HardCore)
- `mod_allows_difficulty()`, `VALID_GAME_DIFFICULTIES` (mod loader не реализован)
- Модель `settings.json` → `difficulty` (режим только в `Character.difficulty`)
- Orphan-строки локализации: `mods.*`, `name_exists`, `not_implemented`
