# Changelog — dnd_mud

## [Unreleased]

### Changed
- Rules refactor: `dnd-mud-workflow.mdc` (git + verify overrides), `dnd-mud-python.mdc` (3.12 + KISS); `AGENTS.md` — оркестрация; global rules slim (`00-global`, `01-operations`, `user-protocols`)
- Rules DRY: git workflow проекта — канон [`.cursor/rules/dnd-mud-workflow.mdc`](../.cursor/rules/dnd-mud-workflow.mdc); global `01-operations` — Task cycle, Cursor modes, commit policy
- Review-политика: локальный subagent (`dnd-mud-review`); GitHub PR Bugbot не используется — `dnd-mud-workflow.mdc`, skills, `DEVELOPMENT.md`

### Removed
- `.cursor/rules/dnd-mud-git.mdc`, `dnd-mud-verify.mdc`, `dnd-mud-python-312.mdc`, `dnd-mud-python-simple.mdc` — объединены в workflow/python

### Removed
- `database/_future/` — дубли активных каталогов
- `mods/_examples/example_mod.yaml` — устаревший manifest
- `core/combat.py`, `core/checks.py` и их тесты (Phase 2 stubs)
- Legacy-парсер `feature_to_grants` и блоки `features:` в активных YAML (только `grants[]`)
- `ui/menus/character_flow.py` — flow перенесён в `_creation_steps.py`
- `core/feats_grants.py` — логика перенесена в `core/feats.py`

### Added
- Документация: фильтрация черт по владениям (класс/раса/подкласс) — [`docs/rules/06-feats.md`](rules/06-feats.md) §«Фильтрация списка»
- `core/feat_visibility.py` — контекст выбора черт (`build_feat_selection_context`) и скрытие без новых владений (`feat_visible_for_selection`)
- `core/io.save_json`, `core/io.merge_unique` — единый JSON I/O и merge списков
- `core/progression.process_pending_level_ups` — headless level-up engine с ASI callback
- `core/classes.get_class_dict` — публичный доступ к сырым данным класса
- `ui/menus/_display/_labels._label_from_catalog` — lookup подписей из каталога
- Фикстуры `human_race_with_subraces`, `subrace_strings` в `tests/conftest.py`
- `core/grant_mechanics.py` — общий парсер proficiency-токенов из grant dict
- `ui/menus/_common._read_numbered_choice` — DRY ввод номера после кастомного рендера
- Тест `test_print_race_info_shows_grants` в `tests/test_display.py`

### Changed
- YAML races/classes/feats — grants-only; классовые умения — `class_features[]`
- `show_create_character_flow` — в `ui/menus/_creation_steps.py`; `_CreationState.start_level` property
- `core/asi.py`, `core/proficiencies.py`, `core/skills.py` — `get_class_dict` вместо `_load_classes_yaml`
- Тесты: 261 → 249 (удалены combat/checks); `test_dice.py` — monkeypatch вместо MagicMock

- `ui/menus/feats._resolve_feat_subchoices` — читает `grants[]` вместо legacy `features[]`
- `ui/menus/_display/_race.py` — экран подрасы читает `grants[]` вместо legacy `features[]`
- `core/progression.process_pending_level_ups` — UI-хук `on_level_up`; `level_up.py` — thin wrapper
- `_CreationState.save_kwargs()` — единый маппинг в `save_character`
- `ui/menus/_selectors.py` — `_read_numbered_choice` для ввода выбора
- `list_feats_for_selection` — третья группа `hidden` (черты без новых владений; показ в конце списка)
- Экраны расы/подрасы/предыстории — локализованный вывод `grants[]` (`ui/menus/_display/_race.py`, `_background.py`, `_labels.py`; ключи в `database/strings/`)
- Документация: убраны ссылки на Phase 2 stubs (`combat`, `checks`, `_future`)
- Тесты: 249 → 250 → 288

### Fixed
- `Character.from_dict()` — fallback на legacy-ключ `"class"` при загрузке старых сейвов (запись — только `class_id`)
- `variant_human` — grant `language` (choice из common) в `database/races/races.yaml`
- `_pick_skills_or_tools` — пул инструментов с учётом категориальных tool-токенов (`has_tool_proficiency`)
- `feat_visible_for_selection` — choice `skill_proficiency` / `tool_proficiency` скрываются при исчерпанном пуле

### Changed
- Рефакторинг техдолга: `core/hp_bonuses.py` (разрыв цикла races↔feats); `class_name` → `class_id` (JSON-сейвы только `class_id`)
- Декомпозиция: `ui/menus/_display/` (пакет), `core/feats_loader.py` + grants в `core/feats.py`, `ui/menus/_creation_steps.py` + `_selectors.py`
- `ui/menus/_deps.py` — re-export из расширенного `core/character.py` (seam для тестов сохранён)
- Удалены legacy re-export в `character_flow.py`; запись JSON — только `class_id` (чтение старых `"class"` — см. Fixed)
- Документация синхронизирована: `ARCHITECTURE`, `API`, `DEVELOPMENT`, scenario runner

### Added
- Тесты: `test_subclass_trainer`, `test_display`, расширен `test_main` (выход из меню)

## [Unreleased — prior]

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
