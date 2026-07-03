---
description: dnd_mud — git/verify/review overrides (console MUD); delta к global
alwaysApply: true
---

# dnd_mud — workflow

База: global Git · Task cycle · Commits. Оркестрация: [`AGENTS.md`](../../AGENTS.md). Человекочитаемо: [`docs/DEVELOPMENT.md`](../../docs/DEVELOPMENT.md) §Git Workflow.

Console MUD — browser forbidden. Переопределяет browser-automation.

## Overrides (delta)

| Global | dnd_mud |
|--------|---------|
| Agent напрямую — git-flow не обязателен | **git-старт обязателен** для правок кода/docs/git |
| Browser verify | На task-ветке агент **не** запускает full verify — только pre-commit `verify-changed`; полный прогон **один раз** в workflow [`dnd-mud-review`](../workflows/dnd-mud-review.md) |
| Push по запросу | auto-commit подзадач; Plan → Build → Agent — push обязателен |
| Ветки `merged/*` | **только локально** — никогда push/upstream/PR на `origin` (§Ветки merged/*) |

**Git scope:** не коммитить `.coverage`, `saves/`.

## Git

**Git-старт:** Task cycle ш.1. Если `main` впереди `dev`:

```bash
git merge origin/main && git push origin dev
```

(Полный `make verify-scope` на `dev` — по запросу или CI; не часть цикла агента на task-ветке.)

**Parallel dev:** после `rebase`/`merge origin/dev` и после конфликта — commit в task-ветке; **не** запускать `make verify-scope` до финального [`dnd-mud-review`](../workflows/dnd-mud-review.md).

```bash
git fetch origin && git rebase origin/dev
# конфликт: git add <files> && git rebase --continue
# push после rebase на remote: --force-with-lease (только своя ветка)
```

| Подход | Когда |
|--------|-------|
| `git rebase origin/dev` | По умолчанию |
| `git merge origin/dev` | Ветка расшарена; force-push — согласовать |

### Несколько веток по плану (Plan / Agent)

**Обязательно**, если план перечисляет **N отдельных PR / фаз / подзадач** — создать **не меньше N part-веток** (по одной на каждый PR), а не реализовывать весь план на одной ветке.

**`main` и `dev` не трогать** в ходе задачи: только task-ветки от `origin/dev`.

| Роль | Ветка | Когда |
|------|-------|-------|
| Интеграционная | `feat/<slug>` | git-старт задачи (slug из плана или темы) |
| Один PR плана | имя из плана или `feat/<slug>-<part>` | **каждый** `### PR-N` / фаза / delivery unit |

#### Шаг 0 — инвентаризация веток (до первой правки кода)

Перед реализацией агент **обязан**:

1. Прочитать план и составить **таблицу веток**: PR-N → имя ветки → scope (файлы/цель).
2. Имена — из заголовков плана, напр. `### PR-1: \`chore/docs-tooling-sync\`` → ветка `chore/docs-tooling-sync`.
3. Если имя в плане нет — `feat/<slug>-<kebab-part>` (напр. `feat/full-refactor-phase1-foundation`).
4. Зафиксировать **ожидаемое число** part-веток `N` (все `### PR-*`, включая optional, если они в плане как отдельные PR).
5. Создать интеграционную `feat/<slug>`; **не** начинать код на `dev` / одной «общей» ветке вместо N part-веток.

Пример (план «17 PR»): `N = 17` → 17 part-веток + 1 интеграционная, а не `feat/refactor-phase1-foundation` со всем diff.

#### Алгоритм реализации

1. **Git-старт** — `git fetch origin`, sync `main`/`dev`, **`git checkout -b feat/<slug>`** от `dev`.
2. **На каждый PR плана** (строго по порядку плана, если есть зависимости):
   ```bash
   git checkout feat/<slug>
   git checkout -b <branch-from-plan>   # напр. chore/docs-tooling-sync
   ```
   - Реализация **только** scope этого PR.
   - **Commit** (≥1) на part-ветке.
   - **Запрещено** переходить к PR-(N+1), пока PR-N не закоммичен на своей ветке.
3. **После всех N part-веток** — слить каждую в интеграционную (**до** docs финализации / review / PR).
   **Merge и удаление — атомарная пара:** сразу после успешного `--no-ff` merge part-ветка **удаляется** (`git branch -d`). Слитая part-ветка без префикса `merged/` не остаётся.
   ```bash
   TASK=feat/<slug>
   git fetch origin
   git checkout "${TASK}" && git rebase origin/dev
   for PART in chore/docs-tooling-sync refactor/save-migrations ...; do
     git merge --no-ff "${PART}" -m "merge(${PART}): into ${TASK}"
     git branch -d "${PART}"    # ОБЯЗАТЕЛЬНО: сразу после успешного merge
   done
   make branch-cleanup CLEANUP_BASE="${TASK}"   # резерв: удалить все слитые в ${TASK} part-ветки одной командой
   ```
4. **Финализация** — только на **`feat/<slug>`**: docs-after-task → commit → review → push/PR → `merged/…`.

#### Проверка перед «задача завершена»

```bash
# Ожидаемое N — из таблицы шага 0; part-ветки уже слиты, но reflog/merge commits видны:
git log --oneline feat/<slug> | head -20
git branch --list 'feat/*' 'chore/*' 'refactor/*' 'fix/*'   # незаархивированные part-ветки
```

**Чистка part-веток** (после merge всех part в `feat/<slug>`; при финализации — после rename в `merged/*`): `make branch-cleanup` — `git branch -d` всех веток, слитых в `CLEANUP_BASE` (по умолчанию `dev`; в контексте §2b, до merge в `dev` — `CLEANUP_BASE=feat/<slug>`); `merged/*`, `main`, `dev` не трогает. Не оставлять слитые part-ветки без префикса `merged/`.

| Критерий | OK | Нарушение (стоп) |
|----------|-----|------------------|
| Part-веток создано и закоммичено | ≥ N (по плану) | Вся работа на 1 ветке при плане с N PR |
| Слияние в `feat/<slug>` | все part слиты `--no-ff` | review/PR с незакрытых part-веток |
| Текущая ветка для review/PR | `feat/<slug>` | part-ветка, `main`, `dev` |
| Commits на part-ветках | есть до merge | один большой uncommitted diff |
| Слитые part-ветки после задачи | удалены (`make branch-cleanup`) | остались `feat/*`/`refactor/*` без `merged/` |

Задача **не завершена**, пока: (a) не созданы все N part-веток по плану; (b) не слиты в `feat/<slug>`; (c) review не на интеграционной.

| Запрещено | Разрешено |
|-----------|-----------|
| План на 17 PR → 1 ветка + весь diff | 17 part-веток → merge → `feat/<slug>` |
| Правки/коммиты на `main`, `dev` | `feat/<slug>`, part-ветки из плана |
| «Сделаю всё, потом разобью на ветки» | Ветка + commit **перед** следующим PR |
| Пропуск `git checkout -b` между PR плана | Одна `feat/<slug>`, если план **явно** одноветочный (1 PR) |

**Одноветочный план** (один PR, без списка `### PR-1…N`) — достаточно одной `feat/<slug>`.

Устаревший пример merge (одна part-ветка):

```bash
TASK=feat/my-task
git fetch origin
git checkout "${TASK}" && git rebase origin/dev
git merge --no-ff "feat/my-task-a"
git push -u origin "${TASK}"         # после rebase: --force-with-lease
git push origin --delete feat/my-task-a
```

### Ветки `merged/*` (только локально)

Любая ветка с префиксом `merged/` — **локальный архив** завершённой task-ветки. На `origin` таких ref **не должно быть**.

| Запрещено | Разрешено |
|-----------|-----------|
| `git push origin merged/…`, `git push -u origin merged/…` | `git branch -m task merged/…` после squash merge |
| PR / `gh pr create` с head `merged/…` | Хранить локально для истории коммитов задачи |
| Upstream `origin/merged/…` | `git branch --unset-upstream` на `merged/*` |

Если на `origin` остались legacy `merged/*` — удалить: `git push origin --delete merged/<name>` (не переносить локальный архив на remote).

### PR task → `dev` (по запросу)

Триггеры: «сделай PR», push task → `dev`. **Policy** — ниже; **процедура** — workflow [`dnd-mud-git-pr`](../workflows/dnd-mud-git-pr.md).

**Rename (обязательно):** только **после squash merge** в `dev` — см. §Ветки `merged/*`. Локально: task → `merged/<исходное-имя>`; remote task-ветку удалить.

| Когда merge | Действие |
|-------------|----------|
| PR уже `MERGED` | Rename в том же turn |
| Ещё нет | URL PR + напомнить rename; по «смержил» — rename без уточнений |

| Статус | Пример |
|--------|--------|
| В работе / PR открыт | `feat/character-stats-menu` |
| Завершена (локально) | `merged/feat/character-stats-menu` |

`main` и `dev` не переименовывать. Префикс `merged/` не дублировать.

Release `dev` → `main`: workflow [`dnd-mud-release`](../workflows/dnd-mud-release.md). Sync `dev`←`main`: personal skill `git-dev-main-sync`.

## Verify / review (policy)

**Канон политики** — этот раздел. Команды — [`dnd-mud-verify/reference.md`](../workflows/dnd-mud-verify/reference.md). Процедуры — workflows в [`.devin/workflows/`](../workflows/README.md).

| Workflow | Процедура |
|----------|-----------|
| [`dnd-mud-docs-after-task`](../workflows/dnd-mud-docs-after-task.md) | docs + commit финализации |
| [`dnd-mud-review`](../workflows/dnd-mud-review.md) | verify-scope + light/full review (**один раз**) |
| [`dnd-mud-fix-plan`](../workflows/dnd-mud-fix-plan.md) | план после Blocker/Major |
| [`dnd-mud-git-pr`](../workflows/dnd-mud-git-pr.md) | push / PR / rename `merged/*` |

### На task-ветке (агент)

| Разрешено | Запрещено агенту вручную |
|-----------|---------------------------|
| `make verify-changed` — **только** через pre-commit при commit | `make test`, `make test-fast`, `make check`, `make verify`, `make verify-scope` |
| Промежуточные commits подзадач | Повторный `dnd-mud-review` без Blocker-fix |
| | `pytest` на всём suite «для проверки» между подзадачами |

### Конец task-ветки (один раз)

После всех подзадач, [`dnd-mud-docs-after-task`](../workflows/dnd-mud-docs-after-task.md) и commit финализации — workflow [`dnd-mud-review`](../workflows/dnd-mud-review.md) **до** push/PR:

1. `make verify-scope` (+ smoke `python main.py` при UI в diff) — если diff затрагивает код/данные
2. light или full readonly review diff vs `origin/dev`

**Не выполнять** между подзадачами, после каждого commit, в середине docs-only правок.

### Пропуск verify-scope

Если diff **только** `docs/`, `.devin/rules`, `AGENTS.md`, workflows — без `core/`, `database/`, `mods/`, `ui/`, `main.py`, `tests/`: шаг verify в review **пропустить**. Review для таких задач — опционален.

### Повторный review

| Ситуация | Действие |
|----------|----------|
| Blocker после review | fix → commits (`verify-changed` only) → **light re-check** (без повторного `verify-scope`, если fix точечный) — §Light re-check в review workflow |
| Повторный full bugbot | Только по явному запросу пользователя |
| Push/PR без review | Только по явному запросу пользователя |

**Review обязателен** один раз на task-ветку с кодом/данными. Bugbot subagent — только **full**. GitHub PR Bugbot — **нет**.

Verify ≠ review. Полный pytest/lint на PR — CI ([`ci.yml`](../../.github/workflows/ci.yml)).

## Динамические метрики

Не хардкодить точное число тестов, файлов diff или строк — получать из команд:

| Метрика | Команда |
|---------|---------|
| Число тестов | `pytest --collect-only -q` |
| Объём diff | `git diff --shortstat origin/<base>...HEAD` |
| Файлы в diff | `git diff --name-only origin/<base>...HEAD` |
