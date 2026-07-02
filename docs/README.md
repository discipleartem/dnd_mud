# Документация dnd_mud

Индекс проектной документации. Правила D&D 5e — отдельный каталог [`rules/`](rules/).

## Для кого

| Аудитория | С чего начать |
|-----------|---------------|
| Игрок / обзор PHB | [`DND_RULES.md`](DND_RULES.md) → [`rules/chapters/`](rules/chapters/) |
| Разработчик кода | [`DEVELOPMENT.md`](DEVELOPMENT.md) → [`ARCHITECTURE.md`](ARCHITECTURE.md) → [`API.md`](API.md) |
| Агент (Cursor) | [`AGENTS.md`](../AGENTS.md) → [`rules/README.md`](rules/README.md) → [`rules/_index/lookup.yaml`](rules/_index/lookup.yaml) |
| Продукт / UI-flow | [`MUD_PRD.md`](MUD_PRD.md) |
| Данные YAML | [`DATA_SCHEMA.md`](DATA_SCHEMA.md) |

## Файлы верхнего уровня

| Файл | Назначение |
|------|------------|
| [`DND_RULES.md`](DND_RULES.md) | Оглавление PHB, глоссарий, режимы сложности; ссылки на `rules/` |
| [`MUD_PRD.md`](MUD_PRD.md) | Требования к UI, flow создания персонажа, scope Pre-Alpha |
| [`API.md`](API.md) | Публичные функции `core/` и контракты |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Слои UI / core / data, потоки данных |
| [`DATA_SCHEMA.md`](DATA_SCHEMA.md) | Схема YAML: grants, расы, классы, инвентарь |
| [`DEVELOPMENT.md`](DEVELOPMENT.md) | Установка, команды, git, тесты |
| [`BACKLOG.md`](BACKLOG.md) | Отложенные задачи и идеи |
| [`CHANGELOG.md`](CHANGELOG.md) | История изменений |

## Справочник правил (`rules/`)

Layout **`agent-v2`**. Точка входа для поиска — [`rules/_index/lookup.yaml`](rules/_index/lookup.yaml).

```text
docs/rules/
  README.md           # guide для агентов
  toc.yaml            # каталог PHB
  chapters/           # обзорные главы 00–11
  entities/           # races, classes, backgrounds, spells, feats
  reference/          # appendices, glossaries
  _index/             # lookup.yaml, entities.yaml, spells.yaml
  _templates/         # шаблон frontmatter
```

| Действие | Где |
|----------|-----|
| Найти правило по RU-названию | `lookup.yaml` → `by_alias` → `quick` / `file` |
| Обновить пересказ из PDF | Блоки `<!-- phb:auto:* -->` в `.md`; процедура — [`rules/README.md`](rules/README.md) |
| Пересобрать индексы | `python scripts/build_rules_index.py` |

**Канон механики:** локальный `docs/PHB_ D&D_2023 RUS.pdf` (не в git). При расхождении: PDF > `rules/` > веб.

## Связанные файлы вне `docs/`

| Файл | Назначение |
|------|------------|
| [`AGENTS.md`](../AGENTS.md) | Agent-loop, поиск правил, skills |
| [`.cursor/rules/00-project.mdc`](../.cursor/rules/00-project.mdc) | Stack, команды, доступ к PHB PDF |
