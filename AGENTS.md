# Agent rules — dnd_mud

**Канон:** [`.cursor/rules/00-project.mdc`](.cursor/rules/00-project.mdc) · global [`00-global.mdc`](~/.cursor/rules/00-global.mdc) · verify [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc)

**Приоритет:** project local → User Rules / global ([`user-rules-minimal.md`](~/.cursor/docs/user-rules-minimal.md))

## Agent-loop

```
git-старт → подзадачи (commits) → docs → verify → review → push / PR
```

| Режим | Цикл |
|-------|------|
| Agent напрямую | анализ → git-старт → план → действие → commit → docs → verify → review → PR (по запросу) |
| Plan → Build → Agent | [`00-global.mdc`](~/.cursor/rules/00-global.mdc) §Cursor modes; commit + push обязательны |

**Overrides:** [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc) §Переопределения.

### 1. Понять задачу

Режим, venv ([`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Virtual environment), git/review constraints.

### 2. Контекст

Правила → этот файл → [`.cursor/skills/`](.cursor/skills/) → код/docs.

### 3. Git-старт

[`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаг 1.  
dnd_mud: при merge `origin/main` в `dev` — `make test` если затронут код (skill `git-dev-main-sync`).

### 4. Подзадачи и коммиты

[`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Commits · procedure [`user-protocols.mdc`](~/.cursor/rules/user-protocols.mdc) §Commit procedure.  
Auto-commit после подзадачи; push/PR — по запросу (Plan → Build → Agent: push обязателен).

### 5. Документация

Skill [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md).

### 6. Verify

Skill [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md). Один раз в конце, после docs.

### 6.5 Review

Skill [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md). После verify, **до** push / PR / merge.  
Blockers → fix → verify → один повтор review.

### 7. Завершение task-ветки

Verify + review выполнены → push/PR по [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаги 5–6.

### 8. Release (`dev` → `main`)

Skill [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md). Review vs `main` до release PR.

## Skills

| Skill | Когда |
|-------|-------|
| [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) | После commit реализации, перед verify |
| [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md) | После docs, перед review |
| [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) | После verify, до push / PR / merge |
| [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md) | Release PR `dev` → `main` |

Personal: `git-dev-main-sync` (`~/.cursor/skills/git-dev-main-sync/`).
