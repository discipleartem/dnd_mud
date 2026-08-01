# Документация dnd_mud

Индекс проектной документации. Правила D&D 5e — отдельный каталог [`rules/`](rules/).

## Для кого

| Аудитория | С чего начать |
|-----------|---------------|
| Игрок / обзор PHB | [`rules/INDEX.md`](rules/INDEX.md) → [`DND_RULES.md`](DND_RULES.md) (статус MUD) |
| Разработчик кода | [`DEVELOPMENT.md`](DEVELOPMENT.md) → [`ARCHITECTURE.md`](ARCHITECTURE.md) → [`API.md`](API.md) |
| Агент (Cursor) | [`AGENTS.md`](../AGENTS.md) → [`rules/_index/lookup.yaml`](rules/_index/lookup.yaml) (`quick`) → [`rules/README.md`](rules/README.md) |
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

Layout **`agent-v2`**. Точка входа для поиска — [`rules/_index/lookup.yaml`](rules/_index/lookup.yaml). Только механика PHB (без лора и без MUD-блоков в карточках).

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
| Обновить пересказ механики | Markdown-карточка + `quick`/`aliases`; guide — [`rules/README.md`](rules/README.md) |
| Обновить индексы | Вручную: `toc.yaml`, `_index/*.yaml`, `lookup.yaml` |

**Канон механики:** PHB **2014** / SRD 5.1 (не редакция 2024). При расхождении: официальные правила 5e до 2024 > `rules/`. Статус MUD — [`DND_RULES.md`](DND_RULES.md).

## Связанные файлы вне `docs/`

| Файл | Назначение |
|------|------------|
| [`AGENTS.md`](../AGENTS.md) | Agent-loop, поиск правил, skills |
| [`.cursor/rules/00-project.mdc`](../.cursor/rules/00-project.mdc) | Stack, команды, алгоритм поиска правил D&D |
