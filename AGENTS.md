# Agent rules — dnd_mud

**Канон:** [`.cursor/rules/00-project.mdc`](.cursor/rules/00-project.mdc) · workflow [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) · global [`00-global.mdc`](~/.cursor/rules/00-global.mdc)

**Приоритет:** project local → User Rules / global ([`user-rules-minimal.md`](~/.cursor/docs/user-rules-minimal.md))

## Agent-loop

```
git-старт → подзадачи (commits) → docs → verify → review (light|full) → [fix-plan?] → fix → verify → light re-check* → push / PR
                                                                                              ↑ blockers only
                                                                    ↑ Major+ или /dnd-mud-fix-plan
```

| Режим | Цикл |
|-------|------|
| Agent напрямую | git-старт → реализация → commit → docs → verify → review (light\|full) → push/PR (по запросу) |
| Plan → Build → Agent | [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Cursor modes; commit + push обязательны |

## Skills

| Skill | Когда |
|-------|-------|
| [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) | После commit реализации, перед verify |
| [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md) | После docs, перед review |
| [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) | После verify, до push / PR / merge — light или full по критериям skill |
| [`dnd-mud-fix-plan`](.cursor/skills/dnd-mud-fix-plan/SKILL.md) | После review при Major/Blocker или по запросу |
| [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md) | Release PR `dev` → `main` |

Personal: `git-dev-main-sync` (`~/.cursor/skills/git-dev-main-sync/`).

## Steps (one-liners)

1. **Git-старт** — [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Git · [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаг 1
2. **Commits** — [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Commits · [`user-protocols.mdc`](~/.cursor/rules/user-protocols.mdc) §Commit procedure
3. **Docs** — skill [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md)
4. **Verify** — skill [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md) (см. таблицу ниже)
5. **Review** — skill [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) (light или full, до push/PR/merge)
6. **Fix plan** — skill [`dnd-mud-fix-plan`](.cursor/skills/dnd-mud-fix-plan/SKILL.md) при Major/Blocker
7. **Push / PR** — [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Git (delta)
8. **Release** — skill [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md)

## Verify (lint + pytest)

Канон: [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md) · маппинг: [`scripts/verify_targets.py`](scripts/verify_targets.py).

| Когда | Команда | Что гоняется |
|-------|---------|--------------|
| После подзадачи / перед commit | `make verify-changed` | ruff + black + mypy + pytest **только staged `.py`** |
| Конец task-ветки, после rebase/merge | `make verify-scope` | то же для diff `origin/dev...HEAD` |
| CI на PR; release локально | `make verify` | полный `make check` + `make test` (~205 тестов + coverage) |

**Не** запускать `make test` / `make check` после каждой правки — только уровень из таблицы.

| Ситуация | Действие |
|----------|----------|
| Только `docs/`, `.cursor/`, `AGENTS.md`, workflows | verify **пропустить** |
| Затронут `ui/` или меню | + smoke `python main.py` |
| Нет mapped-тестов / infra (`Makefile`, `conftest.py`, …) | incremental → **full suite** (fallback в `verify_targets.py`) |
| Pre-commit | хук уже вызывает `make verify-changed` |
