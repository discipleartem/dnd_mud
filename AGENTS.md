# Agent rules — dnd_mud

**Канон:** [`00-project.mdc`](.cursor/rules/00-project.mdc) · [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) · global [`00-global.mdc`](~/.cursor/rules/00-global.mdc)

**Приоритет:** [`user-rules-minimal.md`](~/.cursor/docs/user-rules-minimal.md) §Иерархия

## Поиск правил D&D (PHB)

Канон процедуры — [`00-project.mdc`](.cursor/rules/00-project.mdc) §D&D 5e — источник истины и поиск правил. Guide: [`docs/rules/README.md`](docs/rules/README.md).

1. **`docs/rules/_index/lookup.yaml`** — `by_alias` / `by_id` → `quick` и `file`; детали — `phb:auto` в markdown
2. **`docs/PHB_ D&D_2023 RUS.pdf`** — если в справочнике нет или неполно (`phb_pages` в frontmatter)
3. **Веб** — D&D 5e (PHB 2014 / до редакции 2024), только если шаги 1–2 не дали ответа

Для MUD — `mud:*` в файле + `docs/API.md`. Не использовать память модели. При конфликте: PDF > `docs/rules/` > веб.

### Актуализация справочника из PDF

PDF парсят только агенты. После правок — `python scripts/build_rules_index.py` (нормализация индексов, не PDF).

1. Читает нужный раздел PDF (процедура доступа — `00-project.mdc`).
2. Обновляет `<!-- phb:auto:* -->` и `quick` в frontmatter; при новых сущностях — `toc.yaml`, `_index/entities.yaml` / `_index/spells.yaml`.
3. Сохраняет `mud:*` и `mud_status` / `mud_refs` без изменений, если задача не про реализацию MUD.
4. Запускает `scripts/build_rules_index.py`.

Подробнее: [`docs/rules/README.md`](docs/rules/README.md).

## Agent-loop

```
git-старт (feat/<slug>) → [инвентаризация N PR из плана] → [part-ветка × N: checkout -b → scope → commit]* → merge all (--no-ff) + branch-cleanup → feat/<slug> → docs → review → [fix-plan?] → push/PR → merged/…
```

Part-ветки: **1 PR плана = 1 ветка**; N PR → N веток — [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Несколько веток. **`main` / `dev` не трогать**. Docs — [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) перед commit финализации.

| Режим | Delta vs [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) |
|-------|---------------------------------------------------------------------|
| Agent напрямую | **git-старт обязателен**; push по запросу |
| Plan → Build → Agent | push обязателен |

Git/verify/review/rename — [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) (policy) · skills — [`.cursor/skills/README.md`](.cursor/skills/README.md). Global Task cycle — [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle.

## Skills

| Skill | Когда |
|-------|-------|
| [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) | После реализации, **перед** commit финализации |
| [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md) | Справочник команд ([reference.md](.cursor/skills/dnd-mud-verify/reference.md)); policy — workflow |
| [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) | **Один раз** в конце task-ветки: `verify-scope` + readonly review |
| [`dnd-mud-fix-plan`](.cursor/skills/dnd-mud-fix-plan/SKILL.md) | Major/Blocker после review |
| [`dnd-mud-git-pr`](.cursor/skills/dnd-mud-git-pr/SKILL.md) | Push / PR task → `dev` / rename `merged/*` (по запросу) |
| [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md) | PR `dev` → `main` |

Personal: `git-dev-main-sync` (`~/.cursor/skills/git-dev-main-sync/`).

## Steps

| # | Шаг | Канон |
|---|-----|-------|
| 0 | Инвентаризация веток из плана | Таблица PR → имя ветки; **N** = число `### PR-*` (или фаз delivery); до кода — [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Шаг 0 |
| 1 | Git-старт | `feat/<slug>` от `dev`; [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle ш.1 |
| 2 | Реализация | **Каждый PR** — `git checkout -b <branch>` → scope → commit; не следующий PR без commit на текущей part-ветке |
| 2b | Слияние N part → `feat/<slug>` | После **всех** PR плана; каждая part сразу `git branch -d` после `--no-ff` merge; `main`/`dev` не трогать |
| 2c | Чистка слитых part-веток | `make branch-cleanup` (или `git branch -d` в цикле 2b); не оставлять `feat/*`/`refactor/*` без `merged/` |
| 3–4 | Docs + commit финализации | skill [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) |
| 5 | Review (включает `verify-scope`) | skill [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) — **один раз** |
| 6 | Fix plan | skill [`dnd-mud-fix-plan`](.cursor/skills/dnd-mud-fix-plan/SKILL.md) |
| 7–8 | Push / PR / rename → `merged/*` (локально) | skill [`dnd-mud-git-pr`](.cursor/skills/dnd-mud-git-pr/SKILL.md); policy — [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) |
| 9 | Release | skill [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md) |
