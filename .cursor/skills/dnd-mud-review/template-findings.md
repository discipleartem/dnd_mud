# dnd_mud — формат findings (review output)

Оркестратор review указывает: **Light** или **Full**, **base branch**, результат **verify-scope** (pass/skip).

## Findings

| Severity | Location | Finding |
|----------|----------|---------|
| … | `file:line` | … |

## Nit (опционально)

| Location | Finding |
|----------|---------|
| … | … |

## После review

| Findings | Действие |
|----------|----------|
| Blocker | [`dnd-mud-fix-plan`](../dnd-mud-fix-plan/SKILL.md) → fix (`verify-changed` на commits) → light re-check |
| Major | fix-plan по запросу |
| Minor/Nit only | push/PR — по запросу ([`dnd-mud-git-pr`](../dnd-mud-git-pr/SKILL.md)) |
| No issues | push/PR — по запросу |
