# Agent skills — dnd_mud

Индекс project skills. **Policy** verify/review/git — [`dnd-mud-workflow.mdc`](../rules/dnd-mud-workflow.mdc). **Оркестрация** — [`AGENTS.md`](../../AGENTS.md).

| Слой | Где |
|------|-----|
| Policy | `dnd-mud-workflow.mdc` |
| Loop / steps | `AGENTS.md` |
| Процедуры | skills ниже |

## Skills

| Skill | Когда |
|-------|-------|
| [`dnd-mud-docs-after-task`](dnd-mud-docs-after-task/SKILL.md) | После реализации, перед commit финализации |
| [`dnd-mud-verify`](dnd-mud-verify/SKILL.md) | Справочник команд → [reference.md](dnd-mud-verify/reference.md) |
| [`dnd-mud-review`](dnd-mud-review/SKILL.md) | Один раз: verify-scope + light/full review |
| [`dnd-mud-fix-plan`](dnd-mud-fix-plan/SKILL.md) | План после Blocker/Major |
| [`dnd-mud-git-pr`](dnd-mud-git-pr/SKILL.md) | Push / PR / rename `merged/*` |
| [`dnd-mud-release`](dnd-mud-release/SKILL.md) | Release `dev` → `main` |

Personal: `git-dev-main-sync` (`~/.cursor/skills/git-dev-main-sync/`).

## Agent-loop

```
git-старт → подзадачи (commits; verify-changed) → docs-after-task → commit → review → [fix-plan?] → [git-pr?] → merged/…
```

Release `dev` → `main` — отдельно по запросу (`dnd-mud-release`).

## Reference files

| Файл | Назначение |
|------|------------|
| [`dnd-mud-verify/reference.md`](dnd-mud-verify/reference.md) | Команды verify |
| [`dnd-mud-review/checklist-full.md`](dnd-mud-review/checklist-full.md) | Bugbot checklist |
| [`dnd-mud-review/template-findings.md`](dnd-mud-review/template-findings.md) | Формат findings |
