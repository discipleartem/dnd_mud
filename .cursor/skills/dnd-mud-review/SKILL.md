---
name: dnd-mud-review
description: >-
  Readonly Bugbot review of branch diff vs dev (or main for release) with dnd_mud
  checklist. Use after verify, before push, gh pr create, or git merge that
  integrates code.
---

# dnd_mud — review (Reviewer / Bugbot)

Канон-политика: [`AGENTS.md`](../../AGENTS.md) §6.5 · verify ≠ review ([`dnd-mud-verify.mdc`](../../rules/dnd-mud-verify.mdc)).

**Verify** (`make test`) — runtime. **Review** — readonly diff + чеклист проекта; не дублирует pytest.

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

5. После subagent — сводка по формату `review-bugbot` (таблица Severity | Location | Finding).
6. Решение:
   - **Blocker** → fix → commit → verify → **один** повтор review (только blockers)
   - **Non-blocker** → зафиксировать в ответе; push/PR по запросу пользователя
   - **No issues** → push / PR / merge по политике сессии

Оркестратор **не** правит код по findings, пока пользователь или loop не перешли к fix (кроме явного «исправь blockers»).

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
6. UI — ui/, character_flow: localization keys, menu flow regressions.
7. Docs sync — if behavior/API/data changed, docs/ (API, ARCHITECTURE, DATA_SCHEMA, CHANGELOG) should reflect it; flag drift.
8. Git hygiene — unrelated files, secrets, committed artifacts (.coverage, saves/).
9. Security — only if auth, file paths, or user input parsing changed; otherwise skip.

Output: compact findings table. Blocker = would fail in production or breaks tests/docs contract. Do not suggest browser verification.
Language: findings in Russian; file paths and identifiers in English.
```

## После review

| Исход | Действие |
|-------|----------|
| Blockers | `fix: …` commit(s) → verify → один повтор `dnd-mud-review` |
| Только Major/Minor/Nit | Сообщить пользователю; push/PR — по запросу |
| Subagent failed | См. retry в `review-bugbot`; затем `Diff: natural language` как last resort |
| Empty diff | Сообщить «нет diff для review»; проверить ветку и base |

## Связь с release

Release PR `dev` → `main`: review **до** `gh pr create --base main` с `Base Branch: main`, ветка `dev`. Затем skill [`dnd-mud-release`](../dnd-mud-release/SKILL.md) (trial merge, `make test`, PR).

Sync `main` → `dev`: review опционален; обязателен `make test` (skill `git-dev-main-sync`).
