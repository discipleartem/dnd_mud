# Changelog — dnd_mud

## [Unreleased]

### Changed
- Rules DRY: `AGENTS.md` — оркестрация; `dnd-mud-verify.mdc` — overrides + ссылки на skills; `00-project.mdc` — stack/index без дубля skills
- Человек: подрасы `standard` и `variant_human`; убраны `allow_base_race_choice` / `base_choice_name`
- Полуорк: одна подраса `half_orc` (автовыбор в UI)
- Выбор подрасы: всегда из `subraces`; fallback `human` + `subrace: null` → `standard`

### Added
- Skill `dnd-mud-review`: readonly Bugbot review vs `dev`/`main` после verify, до push / PR / merge; шаг 6.5 в `AGENTS.md`
- YAML schema: [`docs/DATA_SCHEMA.md`](DATA_SCHEMA.md) — `grants[]`, единые `subraces`, mod overlay, Phase 2+ backlog
- `core/grants.py` — нормализация grants и legacy `features`/`mechanics`
- `core/mod_loader.py`, `database/core/mods_state.json`, пример `mods/dragonborn_pack/`
- `grants[]` во всех предысториях (`backgrounds.yaml`)
- Тесты: `test_grants.py`, `test_mod_loader.py`
- Flow создания: шаги **языки** (раса/подраса) и **предыстория** (до класса); 13 PHB backgrounds
- `database/core/languages.yaml`, `database/backgrounds/backgrounds.yaml`
- `core/languages.py`, `core/backgrounds.py`; поля `Character.languages`, `Character.background_id`
- UI: `ui/menus/languages.py`, `ui/menus/backgrounds.py`
- Правило: экзотические языки только при `pool: exotic` / `pool: any` в YAML
- Тесты: `test_languages.py`, `test_backgrounds.py`
- Левелап: `grant_experience` / `apply_level_up` / `run_pending_level_ups`; экран повышения уровня в сценариях
- Выбор подкласса по режимам сложности (`easy` / `normal` / `hardcore`); UI класса и подкласса по образцу расы/подрасы
- Режим «Лёгкая» (`easy`): старт с 3 уровня, обязательный подкласс
- `MAX_CHARACTER_LEVEL = 10`, прогрессия XP (`core/progression.py`), `core/subclasses.py`, `core/scenario.py`
- NPC-наставник: меню персонажей (`subclass_trainer`), действие `subclass_training` в сценариях
- `subclass_choice_level` в `classes.yaml`; поле `subclass_id` в `Character`
- Тесты: `test_subclasses`, `test_progression`, `test_scenario`; расширены `test_character`
- Черты PHB: каталог `feats.yaml`, `core/feats.py`, `core/asi.py`; шаг черт при создании (variant human); ASI или черта при левелапе
- Поля `Character.feat_ids`, `feat_choices`, `asi_choices`; UI `feats.py`, `asi.py`

### Fixed
- Владения: выбор инструментов (`choice: true`) больше не начисляет все варианты пула сразу (дварф)
- КД щита: +2 по PHB даётся без владения; помеха за невладение — через `armor_wearing_penalty`
- §11 PRD: HP 1 уровня `max(1, …)`, поле `max_hp`, потолок характеристик 20, `min_level` и gating приключений, CON → «Телосложение» в ru, README (bard)
- Черты: двойное применение бонусов к характеристикам при создании (`save_character` + `apply_feat_stat_bonuses`)
- Черты: гранты (владения, навыки, языки) при взятии на левелапе через `apply_feat_grants_to_character`

### Changed
- DRY/KISS: `_deps` импортирует leaf-модули core; один проход gating приключений; `_run_numbered_menu` / `_run_stats_confirm_loop` вместо дублирования; `stats/__init__` — только публичный API
- Рефакторинг типов Python 3.12: `core/types.py` (PEP 695 `StatMap`, `StringsDict`, `GameDifficulty`; PEP 692 `RuntimeSettings`), `match/case` в главном меню и flow создания персонажа
- Асимметричный gating: HardCore-персонаж доступен на приключениях без требования HardCore; недоступные — с причиной в UI
- `adventures.yaml`: `min_level`, `allowed_game_difficulties`, `hardcore_only` для tutorial и lost_mine

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
