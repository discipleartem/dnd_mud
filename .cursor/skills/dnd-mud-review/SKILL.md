---
name: dnd-mud-review
description: >-
  Один раз в конце task-ветки: make verify-scope (+ smoke UI), затем readonly
  review diff vs dev (light или full bugbot). Не запускать между подзадачами.
  После Major/Blocker — dnd-mud-fix-plan. GitHub PR Bugbot не используется.
---

# dnd_mud — review (light | full)

Канон-политика: [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Verify / review · [`AGENTS.md`](../../AGENTS.md).

**Единственная точка полного verify на task-ветке:** этот skill. Агент **не** запускает `make verify-scope` / `make test` / `make check` вне review.

## Когда выполнять (один раз)

После **всех** подзадач и основной задачи, skill [`dnd-mud-docs-after-task`](../dnd-mud-docs-after-task/SKILL.md) и commit финализации, **до** push/PR/merge:

| Действие | Base branch | Diff |
|----------|-------------|------|
| Завершение task-ветки | `dev` | `origin/dev...HEAD` |
| `git push` / `gh pr create --base dev` | `dev` | `origin/dev...HEAD` |
| Review на ветке **`dev`** | **`main`** | `origin/main...HEAD` |

Release `dev` → `main`: review **не обязателен** — [`dnd-mud-release`](../dnd-mud-release/SKILL.md).

**Не выполнять** между подзадачами, после каждого commit, после docs-only правки в середине задачи.

## Когда пропустить

- Задача **только** `docs/` / `.cursor/rules` / `AGENTS.md` без кода и данных — review опционален
- Пользователь явно просит push/PR **без** review
- **Повторный** full review: только по явному запросу; после Blocker-fix — §Light re-check

## Определение base branch

```bash
git fetch origin
git branch --show-current
```

| Текущая ветка | Base | Diff |
|---------------|------|------|
| task-ветка | `dev` | `git diff origin/dev...HEAD` |
| `dev` | `main` | `git diff origin/main...HEAD` |

## Предусловия

- [ ] Все подзадачи завершены; вспомогательные ветки слиты ([`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Несколько веток)
- [ ] `dnd-mud-docs-after-task` выполнен (если была реализация кода/данных)
- [ ] Рабочее дерево чистое
- [ ] На task-ветке: `git rebase origin/dev` (на `dev` — fetch `origin/main`)

## Алгоритм (общий — начало)

**Шаг 0 — verify (один раз на task-ветку):**

1. Если diff затрагивает код/данные (`core/`, `database/`, `mods/`, `ui/`, `main.py`, `tests/`):
   - `make verify-scope` (из `.venv`)
   - при UI в diff — smoke `python main.py` (затронутое меню)
2. Если только docs/rules — шаг 0 пропустить.

**Шаг 1+ — readonly review** (light или full ниже).

Справочник команд verify: [`dnd-mud-verify`](../dnd-mud-verify/SKILL.md).

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

## Алгоритм light review (оркестратор)

После шага 0 (verify):

1. `git diff --stat origin/<base>...HEAD` и выборочно `git diff`
2. Прочитать **только** файлы из diff
3. Чеклист: correctness; git hygiene; docs drift; tests — meaningful gaps only
4. Сводка по §**Формат ответа**; Blocker/Major → [`dnd-mud-fix-plan`](../dnd-mud-fix-plan/SKILL.md)
5. **Не** править код без запроса

## Алгоритм full review (bugbot subagent)

После шага 0 (verify):

1. `git diff --stat origin/<base>...HEAD` — diff не пуст
2. **Ровно один** subagent `bugbot` (`readonly: true`, `description: "Bugbot"`)
3. Prompt: `Diff: branch changes`, `Base Branch: <dev|main>`, Custom Instructions — §checklist ниже
4. Сводка; Blocker/Major → fix-plan

**Ошибка bugbot:** один retry с `branch changes`; не `Diff: natural language`.

## Light re-check (после fix Blocker)

Без subagent, **без** повторного `make verify-scope` (если fix только в файлах из findings):

1. `git diff` по исправленным файлам
2. Blocker устранены
3. Full bugbot — только по запросу

## dnd_mud checklist (Custom Instructions для full review)

```text
Reviewer for dnd_mud console MUD (Python 3.12). Readonly code review of branch changes vs base branch.

Scope: only files in the diff; ignore .coverage, saves/.

Checklist (report findings with severity Blocker / Major / Minor / Nit):

1. Correctness & regressions — logic bugs, edge cases, broken loaders, grant/subrace/mod_loader consistency if YAML or core/ touched; KISS, match surrounding style; flag missing type hints in core/ only if obvious.
2. Tests — meaningful gaps only (do not re-run pytest); missing tests for new behavior in core/ or database/.
3. Data & mods — only if database/ or mods/ in diff: grants schema per docs/DATA_SCHEMA.md, legacy compatibility, localization {ru,en}.
4. UI & localization — only if ui/ in diff: localization keys, menu flow regressions.
5. Git hygiene & secrets — unrelated files, .coverage, saves/, credentials.

Output: two blocks — (1) compact table Blocker/Major/Minor only, columns Severity | Location (file:line) | Finding; (2) if any Nit — separate subsection «Nit (опционально)» with table Location | Finding.
Blocker = would fail in production or breaks tests/docs contract. Do not suggest browser verification.
Language: findings in Russian; file paths and identifiers in English.
```

## Формат ответа (оркестратор)

Указать: **Light** или **Full**, **base branch**, результат **verify-scope** (pass/skip).

### Findings

| Severity | Location | Finding |
|----------|----------|---------|
| … | `file:line` | … |

### Nit (опционально)

| Location | Finding |
|----------|---------|
| … | … |

## После review

| Findings | Действие |
|----------|----------|
| Blocker | fix-plan → fix (только `verify-changed` на commits) → light re-check |
| Major | fix-plan по запросу |
| Minor/Nit only | push/PR — по запросу |
| No issues | push/PR — по запросу |
