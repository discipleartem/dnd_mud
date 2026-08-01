# Agent rules — dnd_mud

**Канон:** [`00-project.mdc`](.cursor/rules/00-project.mdc) · [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) · global [`00-global.mdc`](~/.cursor/rules/00-global.mdc)

**Приоритет:** [`user-rules-minimal.md`](~/.cursor/docs/user-rules-minimal.md) §Иерархия

## Поиск правил D&D (PHB)

**Не использовать память модели.** Канон — [`00-project.mdc`](.cursor/rules/00-project.mdc) §D&D 5e.

```
lookup.yaml (by_alias|by_id) → quick → file → (если мало) веб PHB 2014/SRD 5.1 → обновить rules + lookup
```

| Шаг | Действие |
|-----|----------|
| 1a | [`docs/rules/_index/lookup.yaml`](docs/rules/_index/lookup.yaml): `by_alias` (RU/EN/slug) → `id` |
| 1b | `by_id[id].quick` — достаточно ли для ответа? |
| 1c | иначе открыть `by_id[id].file` |
| 1d | статус MUD — [`docs/DND_RULES.md`](docs/DND_RULES.md); оглавление для людей — [`docs/rules/INDEX.md`](docs/rules/INDEX.md) |
| 2 | веб: PHB **2014** / SRD 5.1 (**не** 2024+); затем обновить карточку + `quick`/`aliases` + `lookup.yaml` вручную |

Guide: [`docs/rules/README.md`](docs/rules/README.md). Конфликт: официальные 5e до 2024 > `docs/rules/`.

## Agent-loop

```
[инвентаризация N PR из плана] → git-старт (feat/<slug>) → [part-ветка × N: checkout -b → scope → commit]* → merge all (--no-ff) + branch-cleanup → feat/<slug> → [dead-code post-refactor? 1×] → docs → review → [fix-plan?] → [dead-code pre-PR-dev 1×] → push/PR → merged/…
```

Dead code — [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Dead code · субагент [`dead-code-cleaner`](~/.cursor/agents/dead-code-cleaner.md).

**КРИТИЧЕСКОЕ ПРАВИЛО:** Git-старт ОБЯЗАТЕЛЕН перед ЛЮБОЙ реализацией кода. Не начинать правки на `dev`, `main` или без sync с `origin/dev`.

Part-ветки: **1 PR плана = 1 ветка** — skill [`dnd-mud-multi-branch`](.cursor/skills/dnd-mud-multi-branch/SKILL.md). Docs — [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md). Skills index — [`.cursor/skills/README.md`](.cursor/skills/README.md).

| Режим | Delta vs [`task-cycle.mdc`](~/.cursor/rules/task-cycle.mdc) |
|-------|---------------------------------------------------------------------|
| Agent напрямую | **git-старт обязателен**; push по запросу |
| Plan → Build → Agent | push обязателен |

## Steps

| # | Шаг | Канон |
|---|-----|-------|
| 0 | Инвентаризация веток из плана | [`dnd-mud-multi-branch`](.cursor/skills/dnd-mud-multi-branch/SKILL.md) §Шаг 0 |
| 1 | Git-старт | [`task-cycle.mdc`](~/.cursor/rules/task-cycle.mdc) ш.1 · [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) |
| 2 | Реализация part | [`dnd-mud-multi-branch`](.cursor/skills/dnd-mud-multi-branch/SKILL.md) |
| 2b–2c | Merge part → `feat/<slug>` + cleanup | тот же skill |
| 2d | Dead code **post-refactor** (если задача = рефакторинг) | [`dead-code-cleaner`](~/.cursor/agents/dead-code-cleaner.md) **1×** · [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Dead code |
| 3–4 | Docs + commit финализации | [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) |
| 5 | Review (включает `verify-scope`) | [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) |
| 6 | Fix plan | [`dnd-mud-fix-plan`](.cursor/skills/dnd-mud-fix-plan/SKILL.md) |
| 7 | Dead code **pre-PR-dev** | [`dead-code-cleaner`](~/.cursor/agents/dead-code-cleaner.md) **1×** перед первым PR → `dev` |
| 8–9 | Push / PR / rename → `merged/*` | [`dnd-mud-git-pr`](.cursor/skills/dnd-mud-git-pr/SKILL.md) |
| 10 | Release | [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md) |
