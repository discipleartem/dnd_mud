---
name: dnd-mud-review
description: >-
  Локальный readonly review (Cursor bugbot subagent) diff vs dev/main с чеклистом
  dnd_mud. После verify, до push/PR/merge. При Major/Blocker — предложить
  dnd-mud-fix-plan. GitHub PR Bugbot не используется.
---

# dnd_mud — review (локальный subagent)

Канон-политика: [`AGENTS.md`](../../AGENTS.md) §6.5 · verify ≠ review ([`dnd-mud-verify.mdc`](../../rules/dnd-mud-verify.mdc)).

**Verify** (`make test`) — runtime. **Review** — readonly diff + чеклист проекта; не дублирует pytest.

## Политика Bugbot

| Канал | Статус |
|-------|--------|
| **Локальный** subagent `bugbot` в Cursor Agent (skill [`review-bugbot`](~/.cursor/skills-cursor/review-bugbot/SKILL.md)) | **Да** — единственный review-канал |
| **GitHub PR Bugbot** (авто-review на push, `.cursor/BUGBOT.md`) | **Нет** — не включать в dashboard, файл не вести |

- `.cursor/rules/*.mdc` — только для Agent/IDE при разработке; PR Bugbot их не читает.
- **Один** локальный review **в конце task-ветки** (не после каждого коммита, не в середине задачи).
- Повтор — **только** после fix **blocker** findings (максимум один повтор).
- Не вызывать `/review-bugbot` вне skill-loop без явного запроса пользователя.

## Когда выполнять (обязательно)

После skill [`dnd-mud-verify`](../dnd-mud-verify/SKILL.md) (или эквивалентного verify), **до**:

| Действие | Base Branch | Ветка для review |
|----------|-------------|------------------|
| `git push` task-ветки | `dev` | текущая task-ветка |
| `gh pr create --base dev` | `dev` | head PR / task-ветка |
| `git merge` task → `dev` (локально) | `dev` | merging branch |
| `gh pr create --base main` (release) | `main` | `dev` |
| `git push origin dev` перед release PR | `main` | `dev` |

Запуск skill (`/dnd-mud-review`) или шаг 6.5 в Agent-loop = явный триггер review перед push/PR/merge.

## Когда пропустить

- Только docs / `.cursor/rules` / `AGENTS.md` / workflows — **без** изменений кода и данных (`database/`, `mods/`)
- Пользователь явно просит push/PR/merge **без** review
- Повторный review после fix: только если были **blocker** findings (см. §После review)

## Предусловия

- [ ] Коммиты подзадач сделаны
- [ ] Docs обновлены (skill `dnd-mud-docs-after-task` или пропуск по правилам)
- [ ] Verify пройден (`make test` / `make check` / smoke — по условиям)
- [ ] Рабочее дерево чистое (или только ожидаемые незакоммиченные правки — тогда `Diff: uncommitted changes` не использовать для финального review; сначала commit)

## Алгоритм (оркестратор)

1. Определить **Base Branch** по таблице выше (`dev` по умолчанию для task-веток).
2. Убедиться, что review-ветка checkout локально (`git branch --show-current`).
3. Запустить **ровно один** subagent `bugbot` (канон: skill [`review-bugbot`](~/.cursor/skills-cursor/review-bugbot/SKILL.md)):
   - `readonly: true`
   - `run_in_background: false`
   - `description: "Bugbot"`
   - `subagent_type: "bugbot"`
4. Prompt subagent (форма обязательна):

```text
Full Repository Path: <absolute repository path>
Diff: branch changes
Base Branch: dev
Custom Instructions: <текст из §dnd_mud checklist ниже>
```

Для release заменить `Base Branch: dev` → `Base Branch: main` и checkout `dev`.

5. После subagent — сводка по §**Формат ответа** (основная таблица + отдельная Nit).
6. По таблице findings — **findings → следующий skill** (§После review); при Blocker/Major **предложить** [`dnd-mud-fix-plan`](../dnd-mud-fix-plan/SKILL.md).
7. Решение (fix / push — только по запросу или явному «исправь blockers»):
   - **Blocker** → предложить fix-plan → fix → commit → verify → **один** повтор review
   - **Major** (без Blocker) → предложить fix-plan; push/PR — по запросу после fix или defer
   - **Только Minor/Nit** → зафиксировать в ответе; fix-plan опционально (Minor); push/PR — по запросу
   - **No issues** → push / PR / merge по политике сессии

Оркестратор **не** правит код по findings, пока пользователь или loop не перешли к fix (кроме явного «исправь blockers» / «исправь по плану»).

## dnd_mud checklist (Custom Instructions)

Скопировать в `Custom Instructions` subagent (адаптировать base branch в тексте при release):

```text
Reviewer for dnd_mud console MUD (Python 3.12). Readonly code review of branch changes vs base branch.

Scope: only files in the diff; ignore .coverage, saves/.

Checklist (report findings with severity Blocker / Major / Minor / Nit):

1. Correctness & regressions — logic bugs, edge cases, broken loaders, grant/subrace/mod_loader consistency if YAML or core/ touched.
2. Project simplicity — dnd-mud-python-simple: no over-abstraction, KISS, match surrounding code style.
3. Tests — meaningful gaps only (do not re-run pytest); missing tests for new behavior in core/ or database/.
4. Types & imports — if core/ changed, flag missing type hints or obvious mypy/ruff issues.
5. Data & mods — database/**/*.yaml, mods/**: grants schema per docs/DATA_SCHEMA.md, legacy compatibility, localization {ru,en} where applicable.
6. UI — ui/, `_creation_steps`: localization keys, menu flow regressions.
7. Docs sync — if behavior/API/data changed, docs/ (API, ARCHITECTURE, DATA_SCHEMA, CHANGELOG) should reflect it; flag drift.
8. Git hygiene — unrelated files, secrets, committed artifacts (.coverage, saves/).
9. Security — only if auth, file paths, or user input parsing changed; otherwise skip.

Output: two blocks — (1) compact table Blocker/Major/Minor only, columns Severity | Location (file:line) | Finding, sorted by severity; (2) if any Nit — separate subsection «Nit (опционально)» with table Location (file:line) | Finding (no Severity column). Do not mix Nit into the main table.
Blocker = would fail in production or breaks tests/docs contract. Do not suggest browser verification.
Language: findings in Russian; file paths and identifiers in English.
```

## Формат ответа (оркестратор)

После subagent или ручного fallback — **два блока** (Nit **не** в основной таблице):

**1. Findings** — только Blocker, Major, Minor:

| Severity | Location | Finding |
|----------|----------|---------|
| … | `file:line` | … |

Сортировка: Blocker → Major → Minor. Если issues нет — одна строка: «Blocker/Major/Minor: нет».

**2. Nit (опционально)** — отдельная таблица (только если есть Nit):

| Location | Finding |
|----------|---------|
| `file:line` | … |

Если Nit нет — блок не выводить или одна строка: «Nit: нет».

При manual review: разнести Nit из общего списка в блок 2 до вывода пользователю.

## После review

### Findings → следующий skill

| Findings | Следующий skill | Примечание |
|----------|-----------------|------------|
| Нет issues | push / PR — по запросу | fix-plan не нужен |
| Только Nit | — | Не предлагать fix-plan |
| Minor (без Major/Blocker) | [`dnd-mud-fix-plan`](../dnd-mud-fix-plan/SKILL.md) — **опционально** | Одна строка в ответе review |
| Major | **`dnd-mud-fix-plan`** — предложить | Затем fix в Agent по запросу |
| Blocker | **`dnd-mud-fix-plan`** — предложить | Затем fix → verify → один повтор review |
| Subagent failed | retry / manual review | Затем та же таблица по severity |
| Empty diff | — | Проверить ветку и base |

### Исходы и действия

| Исход | Действие |
|-------|----------|
| Blockers | fix-plan (предложить) → `fix: …` commit(s) → verify → один повтор `dnd-mud-review` |
| Major без Blocker | fix-plan (предложить) → fix по запросу → verify |
| Только Minor/Nit | Сообщить пользователю (Nit — отдельной таблицей §Формат ответа); push/PR — по запросу |
| Subagent failed | См. retry в `review-bugbot`; затем `Diff: natural language` как last resort |
| Empty diff | Сообщить «нет diff для review»; проверить ветку и base |

### Agent-loop (после review)

```
… → verify → review → [fix-plan?] → fix (Agent) → verify → review (если blockers) → push
                      ↑
              Major+ или /dnd-mud-fix-plan
```

Канон: [`AGENTS.md`](../../AGENTS.md) §6.6.

## Связь с release

Release PR `dev` → `main`: review **до** `gh pr create --base main` с `Base Branch: main`, ветка `dev`. Затем skill [`dnd-mud-release`](../dnd-mud-release/SKILL.md) (trial merge, `make test`, PR).

Sync `main` → `dev`: review опционален; обязателен `make test` (skill `git-dev-main-sync`).
