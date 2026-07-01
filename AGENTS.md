# Agent rules — dnd_mud

**Канон:** [`00-project.mdc`](.cursor/rules/00-project.mdc) · [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) · global [`00-global.mdc`](~/.cursor/rules/00-global.mdc)

**Приоритет:** [`user-rules-minimal.md`](~/.cursor/docs/user-rules-minimal.md) §Иерархия

## Agent-loop

```
git-старт → подзадачи (промежуточные commits) → [слияние веток по плану]* → docs → commit → verify → review (light|full) → [fix-plan?] → push/PR task→dev (+ локальный rename) → merged/…
```

\* [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Несколько веток по плану · docs — skill [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) **перед** commit финализации

| Режим | Delta vs [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) |
|-------|---------------------------------------------------------------------|
| Agent напрямую | **git-старт обязателен**; push по запросу |
| Plan → Build → Agent | push обязателен |

Git/verify/review/rename — [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc). Global Task cycle — [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle.

## Skills

| Skill | Когда |
|-------|-------|
| [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) | После реализации, **перед** commit финализации |
| [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md) | После docs+commit, **перед** review |
| [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) | После verify, до push/PR — light или full |
| [`dnd-mud-fix-plan`](.cursor/skills/dnd-mud-fix-plan/SKILL.md) | Major/Blocker после review |
| [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md) | PR `dev` → `main` |

Personal: `git-dev-main-sync` (`~/.cursor/skills/git-dev-main-sync/`).

## Steps

| # | Шаг | Канон |
|---|-----|-------|
| 1 | Git-старт | [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Git · [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle ш.1 |
| 2 | Реализация | Промежуточные commits — [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Commits |
| 2b | Слияние веток по плану | [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Несколько веток по плану |
| 3–4 | Docs + commit финализации | skill [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) |
| 5 | Verify | skill [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md) |
| 6 | Review | skill [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) |
| 7 | Fix plan | skill [`dnd-mud-fix-plan`](.cursor/skills/dnd-mud-fix-plan/SKILL.md) |
| 8–9 | Push / PR / rename → `merged/*` (локально) | [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Ветки `merged/*` · §PR task → dev |
| 10 | Release | skill [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md) |
