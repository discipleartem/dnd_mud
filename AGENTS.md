# Agent rules — dnd_mud

**Канон:** [`.cursor/rules/00-project.mdc`](.cursor/rules/00-project.mdc) · workflow [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) · global [`00-global.mdc`](~/.cursor/rules/00-global.mdc)

**Приоритет:** project local → User Rules / global ([`user-rules-minimal.md`](~/.cursor/docs/user-rules-minimal.md))

## Agent-loop

```
git-старт → подзадачи (commits) → docs → verify → review → [fix-plan?] → fix → verify → review* → push / PR
                                                                                    ↑ blockers only
                                                      ↑ Major+ или /dnd-mud-fix-plan
```

| Режим | Цикл |
|-------|------|
| Agent напрямую | git-старт → реализация → commit → docs → verify → review → push/PR (по запросу) |
| Plan → Build → Agent | [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Cursor modes; commit + push обязательны |

## Skills

| Skill | Когда |
|-------|-------|
| [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) | После commit реализации, перед verify |
| [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md) | После docs, перед review |
| [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) | После verify, до push / PR / merge |
| [`dnd-mud-fix-plan`](.cursor/skills/dnd-mud-fix-plan/SKILL.md) | После review при Major/Blocker или по запросу |
| [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md) | Release PR `dev` → `main` |

Personal: `git-dev-main-sync` (`~/.cursor/skills/git-dev-main-sync/`).

## Steps (one-liners)

1. **Git-старт** — [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Git · [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаг 1
2. **Commits** — [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Commits · [`user-protocols.mdc`](~/.cursor/rules/user-protocols.mdc) §Commit procedure
3. **Docs** — skill [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md)
4. **Verify** — skill [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md)
5. **Review** — skill [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) (до push/PR/merge)
6. **Fix plan** — skill [`dnd-mud-fix-plan`](.cursor/skills/dnd-mud-fix-plan/SKILL.md) при Major/Blocker
7. **Push / PR** — [`dnd-mud-workflow.mdc`](.cursor/rules/dnd-mud-workflow.mdc) §Git (delta)
8. **Release** — skill [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md)
