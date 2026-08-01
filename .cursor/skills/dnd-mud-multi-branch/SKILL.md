---
name: dnd-mud-multi-branch
description: >-
  Процедура N part-веток по плану: inventory, checkout, commit, merge --no-ff,
  branch-cleanup. Policy — dnd-mud-workflow §Multi-branch. Читать при плане с N PR.
---

# dnd_mud — multi-branch (N PR → N part)

**Policy:** [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Multi-branch.  
**Git-старт интеграции:** [`task-cycle.mdc`](~/.cursor/rules/task-cycle.mdc) ш.1 → `feat/<slug>` от `origin/dev`.

## Шаг 0 — инвентаризация (до первой правки кода)

1. Прочитать план → таблица: PR-N → имя ветки → scope.
2. Имена из заголовков плана (`### PR-1: \`chore/…\`` → `chore/…`).
3. Если имени нет — `feat/<slug>-<kebab-part>`.
4. Зафиксировать **N** = число `### PR-*` (или фаз delivery).
5. Убедиться, что интеграционная `feat/<slug>` создана; **не** кодить на `dev` / одной «общей» ветке вместо N part.

Пример: план «17 PR» → 17 part + 1 интеграционная.

## Алгоритм реализации

1. **Git-старт** (если ещё нет `feat/<slug>`): `git fetch origin` → sync `dev` → `git checkout -b feat/<slug>`.
2. **На каждый PR плана** (по порядку зависимостей):

```bash
git checkout feat/<slug>
git checkout -b <branch-from-plan>   # напр. chore/docs-tooling-sync
```

- Реализация **только** scope этого PR.
- **Commit** (≥1) на part-ветке.
- **Запрещено** переходить к PR-(N+1), пока PR-N не закоммичен на своей ветке.
- Part-ветки создаются **от** `feat/<slug>`, не друг от друга.

3. **После всех N part** — слить в интеграционную (**до** docs / review / PR). Merge и удаление — атомарная пара:

```bash
TASK=feat/<slug>
git fetch origin
git checkout "${TASK}" && git rebase origin/dev
for PART in chore/part-a chore/part-b ...; do
  git merge --no-ff "${PART}" -m "merge(${PART}): into ${TASK}"
  git branch -d "${PART}"
done
make branch-cleanup CLEANUP_BASE="${TASK}"
```

4. **Финализация** только на **`feat/<slug>`**: docs-after-task → review → push/PR → `merged/…`.

## Проверка перед «задача завершена»

```bash
git log --oneline feat/<slug> | head -20
git branch --list 'feat/*' 'chore/*' 'refactor/*' 'fix/*'
```

| Критерий | OK | Нарушение |
|----------|-----|-----------|
| Part созданы и закоммичены | ≥ N | весь diff на 1 ветке |
| Слиты в `feat/<slug>` | все `--no-ff` | review с part-ветки |
| Слитые part удалены | `branch -d` / `make branch-cleanup` | висят без `merged/` |

Одноветочный план (без списка PR-1…N) — skill не нужен; достаточно одной `feat/<slug>`.
