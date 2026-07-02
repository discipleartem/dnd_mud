# Справочник правил — guide для агентов

**Layout:** `agent-v2` · **Источник механики:** локальный PHB (`docs/*PHB*.pdf`).

## Политика контента

**Только актуальная механика PHB** — без лора, флавора, историй, мировоззрения, таблиц личности и дословных цитат.

| Включать | Исключать |
|----------|-----------|
| Увеличения характеристик, скорость, размер | Описания культуры, внешности, «характера расы» |
| Владения, сопротивления, особые действия | Идеалы, привязанности, слабости, примеры NPC |
| Параметры заклинаний и эффекты | Поэтические вступления из PDF |
| Требования и эффекты черт | Дублирование текста PHB «для атмосферы» |

При обновлении из PDF агент переносит **структурированный пересказ механики** в `<!-- phb:auto:* -->` и краткий `quick` в frontmatter. Лор — только в PDF.

Актуализация пересказа в `docs/rules/` — **вручную агентами** из PDF для точечных правок; массовая синхронизация — `scripts/build_rules_index.py` (заклинания из PDF, feats из YAML, расы/классы из скриптов).

## Быстрый старт (агент)

| Шаг | Действие |
|-----|----------|
| 1 | Открыть [`_index/lookup.yaml`](_index/lookup.yaml) |
| 2 | Найти сущность: `by_alias` (RU/EN/slug) → `id`, или сразу `by_id` |
| 3 | Прочитать `quick` — краткая механика без открытия файла |
| 4 | При необходимости деталей — `file` из записи `by_id` |
| 5 | В файле: правила PHB → `<!-- phb:auto:* -->`; MUD → `<!-- mud:* -->` + [`docs/API.md`](../API.md) |
| 6 | Неполно / нет в справочнике → PDF по `phb_pages` в frontmatter или `pages` в `toc.yaml` |

**Не использовать память модели.** При конфликте: PDF > `docs/rules/` > веб.

## Точки входа

| Приоритет | Файл | Назначение |
|-----------|------|------------|
| **1** | [`_index/lookup.yaml`](_index/lookup.yaml) | Единый индекс: `by_id`, `by_alias`, `summaries` |
| 2 | [`toc.yaml`](toc.yaml) | Каталог PHB: `id`, `type`, `file`, `pages`, `mud_status` |
| 3 | [`_index/entities.yaml`](_index/entities.yaml) | Сущности и главы (без заклинаний) |
| 4 | [`_index/spells.yaml`](_index/spells.yaml) | Заклинания по EN-slug |
| 5 | [`_index/spells/by-level.md`](_index/spells/by-level.md) | Группировка по уровню |
| 6 | [`_index/spells/by-school.md`](_index/spells/by-school.md) | Группировка по школе |

Устаревшие для прямого чтения (пересобираются скриптом): [`aliases.yaml`](_index/aliases.yaml), [`summaries.yaml`](_index/summaries.yaml) — дублируют части `lookup.yaml`.

## Структура каталога

```text
docs/rules/
  chapters/           # обзорные главы PHB
  entities/           # races/, classes/, backgrounds/, spells/, feats/
  reference/          # appendices/, glossaries/
  _index/             # lookup.yaml + вспомогательные индексы
  _templates/         # шаблон frontmatter
```

## Структура файла

### Главы, расы, классы, предыстории, черты

1. **Frontmatter** — `id`, `type`, `phb_*`, `mud_status`, опционально `quick` (краткая механика для индекса)
2. **`## Правила (PHB)`** — `<!-- phb:auto:… -->`
3. **`## Реализация в MUD`** — `<!-- mud:implementation -->`

### Заклинания

1. Frontmatter + опционально `quick`
2. `## Параметры` → `phb:auto:parameters`
3. `## Эффект` → `phb:auto:effect`
4. `## На больших уровнях` → `phb:auto:higher-levels` (если есть)
5. `## Реализация в MUD` → `mud:implementation`

## Актуализация из PDF (агент)

Процедура доступа к PDF — [`.cursor/rules/00-project.mdc`](../../.cursor/rules/00-project.mdc) §D&D 5e.

1. Найти раздел в PDF (`phb_pages` в frontmatter или `toc.yaml`).
2. Обновить **только** блоки `<!-- phb:auto:* -->` — структурированный пересказ механики (не дословная копия).
3. Добавить или обновить `quick` в frontmatter (1–2 предложения механики, без флавора).
4. При новой сущности — файл по [`_templates/frontmatter-template.md`](_templates/frontmatter-template.md); запись в `toc.yaml` и `_index/entities.yaml` или `_index/spells.yaml`.
5. Запустить нормализацию индексов:

```bash
.venv/bin/python scripts/build_rules_index.py
```

6. **Не** затирать `mud:*`, `mud_status`, `mud_refs` без запроса.

## Что делает `build_rules_index.py`

| Действие | Описание |
|----------|----------|
| Карточки рас | Канон PHB — `RACE_CARDS` в `build_rules_index.py` (сверка с PDF) |
| Карточки предысторий | Механика из `database/backgrounds/backgrounds.yaml` |
| Карточки классов | Канон PHB — `scripts/rules_class_data.py` (`CLASS_PHB`); YAML — только `mud_refs` |
| Заклинания | Парсинг `docs/*PHB*.pdf` (`phb_spell_parse.py`) → `entities/spells/*.md` |
| Карточки feats | Синхронизация `entities/feats/*.md` из `database/progression/feats.yaml` |
| Главы | `00`–`04`, `06-feats` — краткий индекс без лора |
| `lookup.yaml` | Сборка `by_id`, `by_alias`, `summaries` из индексов и `quick` |
| Layout | Проставление `layout: agent-v2` в индексах и `toc.yaml` |
