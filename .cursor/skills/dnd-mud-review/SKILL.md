---
name: dnd-mud-review
description: >-
  Один раз в конце task-ветки: make verify-scope (+ smoke UI), затем readonly
  review diff vs dev (light или full bugbot). Политика — dnd-mud-workflow
  §Verify/review. Не запускать между подзадачами. После Blocker — fix-plan.
---

# dnd_mud — review (light | full)

Политика: [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Verify / review. Команды verify: [`dnd-mud-verify/reference.md`](../dnd-mud-verify/reference.md).

## Когда выполнять

После **всех** подзадач, [`dnd-mud-docs-after-task`](../dnd-mud-docs-after-task/SKILL.md) и commit финализации, **до** push/PR:

| Действие | Base | Diff |
|----------|------|------|
| Завершение task-ветки | `dev` | `origin/dev...HEAD` |
| Review на ветке **`dev`** | **`main`** | `origin/main...HEAD` |

Release `dev` → `main`: review **не обязателен** — [`dnd-mud-release`](../dnd-mud-release/SKILL.md).

## Предусловия

- [ ] План с N PR: созданы и закоммичены **≥ N part-веток** (не один общий diff); таблица PR→ветка — [`dnd-mud-multi-branch`](../dnd-mud-multi-branch/SKILL.md) §Шаг 0
- [ ] Все part-ветки **слиты** `--no-ff` в интеграционную `feat/<slug>` ([`dnd-mud-multi-branch`](../dnd-mud-multi-branch/SKILL.md))
- [ ] Текущая ветка — `feat/<slug>`, не part-ветка и не `main`/`dev`
- [ ] `dnd-mud-docs-after-task` выполнен (если была реализация кода/данных)
- [ ] Рабочее дерево чистое
- [ ] На task-ветке: `git rebase origin/dev` (на `dev` — fetch `origin/main`)

## Определение base branch

```bash
git fetch origin
git branch --show-current
```

| Текущая ветка | Base | Diff |
|---------------|------|------|
| task-ветка | `dev` | `git diff origin/dev...HEAD` |
| `dev` | `main` | `git diff origin/main...HEAD` |

## Шаг 0 — verify

1. Если diff затрагивает код/данные (`core/`, `database/`, `mods/`, `ui/`, `main.py`, `tests/`):
   - `make verify-scope` (из `.venv`) — см. [reference.md](../dnd-mud-verify/reference.md)
   - при UI в diff — smoke `python main.py`
2. Если только docs/rules — пропустить (workflow §Пропуск verify-scope).

## Выбор режима review

```bash
git diff --shortstat origin/<base>...HEAD
git diff --name-only origin/<base>...HEAD
```

| Условие | Режим |
|---------|-------|
| Пользователь просит «полный review» / «bugbot» | **Full** |
| Diff не затрагивает `core/`, `database/`, `mods/`, `ui/`, `main.py`; узкий scope (docs, rules, skills) | **Light** |
| Иначе | **Full** |

## Алгоритм light review

После шага 0:

1. `git diff --stat origin/<base>...HEAD` и выборочно `git diff`
2. Прочитать **только** файлы из diff
3. Чеклист: correctness; git hygiene; docs drift; tests — meaningful gaps only
4. Сводка по [template-findings.md](template-findings.md); Blocker/Major → [`dnd-mud-fix-plan`](../dnd-mud-fix-plan/SKILL.md)
5. **Не** править код без запроса

## Алгоритм full review (bugbot subagent)

После шага 0:

1. `git diff --stat origin/<base>...HEAD` — diff не пуст
2. **Ровно один** subagent `bugbot` (`readonly: true`, `description: "Bugbot"`)
3. Prompt: `Diff: branch changes`, `Base Branch: <dev|main>`, Custom Instructions — [checklist-full.md](checklist-full.md)
4. Сводка по [template-findings.md](template-findings.md); Blocker/Major → fix-plan

**Ошибка bugbot:** один retry с `branch changes`; не `Diff: natural language`.

## Light re-check (после fix Blocker)

Без subagent, **без** повторного `make verify-scope` (если fix только в файлах из findings):

1. `git diff` по исправленным файлам
2. Blocker устранены
3. Full bugbot — только по запросу

Формат ответа и действия после review: [template-findings.md](template-findings.md).
