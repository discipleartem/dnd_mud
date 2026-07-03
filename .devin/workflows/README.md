# Agent workflows — dnd_mud

Индекс project workflows. **Policy** verify/review/git — [`dnd-mud-workflow.md`](../rules/dnd-mud-workflow.md). **Оркестрация** — [`AGENTS.md`](../../AGENTS.md).

| Слой | Где |
|------|-----|
| Policy | `dnd-mud-workflow.md` |
| Loop / steps | `AGENTS.md` |
| Процедуры | workflows ниже |

## Workflows

| Workflow | Когда |
|----------|-------|
| [`dnd-mud-docs-after-task`](dnd-mud-docs-after-task.md) | После реализации, перед commit финализации |
| [`dnd-mud-verify`](dnd-mud-verify.md) | Справочник команд → [reference.md](dnd-mud-verify/reference.md) |
| [`dnd-mud-review`](dnd-mud-review.md) | Один раз: verify-scope + light/full review |
| [`dnd-mud-fix-plan`](dnd-mud-fix-plan.md) | План после Blocker/Major |
| [`dnd-mud-git-pr`](dnd-mud-git-pr.md) | Push / PR / rename `merged/*` |
| [`dnd-mud-release`](dnd-mud-release.md) | Release `dev` → `main` |

Personal: `git-dev-main-sync` (global skill).

## Agent-loop

```
git-старт → [инвентария N PR] → [part × N: branch + commit] → merge → feat/<slug> → docs → review → [git-pr?] → merged/…
```

**1 PR плана = 1 ветка.** План на 17 PR — 17 part-веток, не одна. Канон: [`dnd-mud-workflow.md`](../rules/dnd-mud-workflow.md) §Несколько веток.

Release `dev` → `main` — отдельно по запросу (`dnd-mud-release`).

## Reference files

| Файл | Назначение |
|------|------------|
| [`dnd-mud-verify/reference.md`](dnd-mud-verify/reference.md) | Команды verify |
| [`dnd-mud-review/checklist-full.md`](dnd-mud-review/checklist-full.md) | Bugbot checklist |
| [`dnd-mud-review/template-findings.md`](dnd-mud-review/template-findings.md) | Формат findings |
