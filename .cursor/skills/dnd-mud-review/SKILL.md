---
name: dnd-mud-review
description: >-
  Локальный readonly review (Cursor bugbot subagent) diff vs dev/main с чеклистом
  dnd_mud. После verify, до push/PR/merge. При Major/Blocker — предложить
  dnd-mud-fix-plan. GitHub PR Bugbot не используется.
---

# dnd_mud — review (локальный subagent)

Канон-политика: [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Verify / review · [`AGENTS.md`](../../AGENTS.md).

**Verify** (`make test`) — runtime. **Review** — readonly diff + чеклист; не дублирует pytest.

## Когда выполнять

После skill [`dnd-mud-verify`](../dnd-mud-verify/SKILL.md), **до** push/PR/merge:

| Действие | Base Branch | Ветка для review |
|----------|-------------|------------------|
| `git push` task-ветки | `dev` | текущая task-ветка |
| `gh pr create --base dev` | `dev` | head PR / task-ветка |
| `gh pr create --base main` (release) | `main` | `dev` |

## Когда пропустить

- Только docs / `.cursor/rules` / `AGENTS.md` — без изменений кода и данных
- Пользователь явно просит push/PR/merge **без** review
- Повторный review: только после fix **blocker** findings (максимум один повтор)

## Предусловия

- [ ] Verify пройден
- [ ] Рабочее дерево чистое (для финального review — сначала commit)

## Алгоритм (оркестратор)

1. Определить **Base Branch** (`dev` по умолчанию).
2. Запустить **ровно один** subagent `bugbot` ([`review-bugbot`](~/.cursor/skills-cursor/review-bugbot/SKILL.md)):
   - `readonly: true`, `run_in_background: false`, `description: "Bugbot"`, `subagent_type: "bugbot"`
3. Prompt subagent:

```text
Full Repository Path: <absolute repository path>
Diff: branch changes
Base Branch: dev
Custom Instructions: <текст из §dnd_mud checklist ниже>
```

4. Сводка по §**Формат ответа**; при Blocker/Major — предложить [`dnd-mud-fix-plan`](../dnd-mud-fix-plan/SKILL.md).
5. Оркестратор **не** правит код, пока пользователь не попросил fix.

## dnd_mud checklist (Custom Instructions)

```text
Reviewer for dnd_mud console MUD (Python 3.12). Readonly code review of branch changes vs base branch.

Scope: only files in the diff; ignore .coverage, saves/.

Checklist (report findings with severity Blocker / Major / Minor / Nit):

1. Correctness & regressions — logic bugs, edge cases, broken loaders, grant/subrace/mod_loader consistency if YAML or core/ touched.
2. Project simplicity — dnd-mud-python KISS: no over-abstraction, match surrounding code style.
3. Tests — meaningful gaps only (do not re-run pytest); missing tests for new behavior in core/ or database/.
4. Types & imports — if core/ changed, flag missing type hints or obvious mypy/ruff issues.
5. Data & mods — database/**/*.yaml, mods/**: grants schema per docs/DATA_SCHEMA.md, legacy compatibility, localization {ru,en} where applicable.
6. UI — ui/, `_creation_steps`: localization keys, menu flow regressions.
7. Docs sync — if behavior/API/data changed, docs/ should reflect it; flag drift.
8. Git hygiene — unrelated files, secrets, committed artifacts (.coverage, saves/).
9. Security — only if auth, file paths, or user input parsing changed; otherwise skip.

Output: two blocks — (1) compact table Blocker/Major/Minor only, columns Severity | Location (file:line) | Finding; (2) if any Nit — separate subsection «Nit (опционально)» with table Location | Finding.
Blocker = would fail in production or breaks tests/docs contract. Do not suggest browser verification.
Language: findings in Russian; file paths and identifiers in English.
```

## Формат ответа (оркестратор)

**1. Findings** — Blocker, Major, Minor:

| Severity | Location | Finding |
|----------|----------|---------|
| … | `file:line` | … |

**2. Nit (опционально)** — отдельная таблица, если есть.

## После review

| Findings | Действие |
|----------|----------|
| Blocker | fix-plan → fix → verify → один повтор review |
| Major | fix-plan (предложить) → fix по запросу |
| Minor/Nit only | push/PR — по запросу |
| No issues | push/PR — по политике сессии |

Release: `Base Branch: main`, ветка `dev` → skill [`dnd-mud-release`](../dnd-mud-release/SKILL.md).
