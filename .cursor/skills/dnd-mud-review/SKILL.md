---
name: dnd-mud-review
description: >-
  Локальный readonly review diff vs base: task-ветка → dev, ветка dev → main;
  light (оркестратор) или full (bugbot subagent). После verify, до push/PR/merge.
  При Major/Blocker — предложить dnd-mud-fix-plan. GitHub PR Bugbot не используется.
---

# dnd_mud — review (light | full)

Канон-политика: [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Verify / review · [`AGENTS.md`](../../AGENTS.md).

**Verify** (`make verify-scope` локально; `make verify` в CI) — runtime. **Review** — readonly diff + чеклист; не дублирует pytest.

## Когда выполнять

После skill [`dnd-mud-verify`](../dnd-mud-verify/SKILL.md), **до** push/PR/merge:

| Действие | Base branch | Ветка для review | Diff |
|----------|-------------|------------------|------|
| `git push` task-ветки | `dev` | текущая task-ветка | `origin/dev...HEAD` |
| `gh pr create --base dev` | `dev` | head PR / task-ветка | `origin/dev...HEAD` |
| Review на ветке **`dev`** | **`main`** | `dev` | **`origin/main...HEAD`** |

Release `dev` → `main`: review **не обязателен** — см. [`dnd-mud-release`](../dnd-mud-release/SKILL.md).

## Определение base branch

Перед review: `git fetch origin`, затем:

```bash
git branch --show-current
```

| Текущая ветка | Base branch | Команда diff |
|---------------|-------------|--------------|
| `dev` | **`main`** | `git diff origin/main...HEAD` |
| task-ветка (не `main`, не `dev`) | `dev` | `git diff origin/dev...HEAD` |
| `main` | — | review не типичен; только по явному запросу |

**На `dev`:** сравнивать с `main`, не с `dev` (иначе diff пустой или бессмысленный).

## Когда пропустить

- Только docs / `.cursor/rules` / `AGENTS.md` — без изменений кода и данных
- Пользователь явно просит push/PR/merge **без** review
- Повторный review: только после fix **blocker** findings (максимум один повтор — light re-check)

## Выбор режима review

Перед review: `git fetch origin`, определить base (§**Определение base branch**), **снять метрики diff** (не опираться на числа из docs — suite и diff меняются):

```bash
git diff --shortstat origin/<base>...HEAD
git diff --name-only origin/<base>...HEAD
```

При необходимости указать число тестов в ответе: `pytest --collect-only -q` (из `.venv`).

Для **task-ветки** перед full review: `git rebase origin/dev`. На **`dev`** rebase на `origin/dev` не нужен; убедиться, что `origin/main` актуален (`git fetch origin`).

| Условие | Режим |
|---------|-------|
| Только `docs/`, `.cursor/rules`, `AGENTS.md` | **Пропуск** |
| Пользователь явно просит «полный review» / «bugbot» | **Full** |
| Diff **не** затрагивает `core/`, `database/`, `mods/`, `ui/`, `main.py`; узкий scope по `--shortstat` / `--name-only` (преимущественно docs, rules, skills, infra/tests без продуктового кода) | **Light** |
| Иначе | **Full** |

## Предусловия

- [ ] Verify пройден
- [ ] Рабочее дерево чистое (для финального review — сначала commit)
- [ ] Перед **full** на task-ветке: `git fetch origin && git rebase origin/dev`
- [ ] Перед **full** на **`dev`**: `git fetch origin` (base = `main`, rebase не на `dev`)

## Алгоритм light review (оркестратор)

Без subagent и без Task tool.

1. Определить **base branch** (§**Определение base branch**): task-ветка → `dev`, **`dev` → `main`**.
2. `git diff --stat origin/<base>...HEAD` и `git diff origin/<base>...HEAD`.
3. Прочитать **только** файлы из diff.
4. Чеклист (4 пункта): correctness; git hygiene & secrets; docs drift (если менялось поведение); tests — meaningful gaps only.
5. Сводка по §**Формат ответа**; при Blocker/Major — предложить [`dnd-mud-fix-plan`](../dnd-mud-fix-plan/SKILL.md).
6. Оркестратор **не** правит код, пока пользователь не попросил fix.

## Алгоритм full review (bugbot subagent)

1. Определить **base branch** (§**Определение base branch**): task-ветка → `dev`, **`dev` → `main`**.
2. `git fetch origin`; на task-ветке — `git rebase origin/dev` (на `dev` — не rebase на себя).
3. `git diff --stat origin/<base>...HEAD` — убедиться, что diff не пуст.
4. Запустить **ровно один** subagent `bugbot` ([`review-bugbot`](~/.cursor/skills-cursor/review-bugbot/SKILL.md)):
   - `readonly: true`, `run_in_background: false`, `description: "Bugbot"`, `subagent_type: "bugbot"`
5. Prompt subagent:

```text
Full Repository Path: <absolute repository path>
Diff: branch changes
Base Branch: <main|dev — по §Определение base branch>
Custom Instructions: <текст из §dnd_mud checklist ниже>
```

6. Сводка по §**Формат ответа**; при Blocker/Major — предложить [`dnd-mud-fix-plan`](../dnd-mud-fix-plan/SKILL.md).
7. Оркестратор **не** правит код, пока пользователь не попросил fix.

**При ошибке bugbot или пустом diff:** **не** использовать `Diff: natural language`. Сообщить пользователю; исправить git-состояние (`fetch`, clean tree, rebase) и повторить **один** раз с `branch changes`.

## Light re-check (после fix Blocker)

Без subagent:

1. `git diff` по файлам из Location в findings (или `git diff origin/<base>...HEAD` если много файлов).
2. Проверить, что Blocker устранены; Major — по запросу.
3. Full bugbot — только по явному запросу пользователя.

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

Указать режим: **Light** или **Full** и **base branch** (`dev` или `main`).

**1. Findings** — Blocker, Major, Minor:

| Severity | Location | Finding |
|----------|----------|---------|
| … | `file:line` | … |

**2. Nit (опционально)** — отдельная таблица, если есть.

## После review

| Findings | Действие |
|----------|----------|
| Blocker | fix-plan → fix → verify → **light re-check** (не full bugbot по умолчанию) |
| Major | fix-plan (предложить) → fix по запросу |
| Minor/Nit only | push/PR — по запросу |
| No issues | push/PR — по политике сессии |
