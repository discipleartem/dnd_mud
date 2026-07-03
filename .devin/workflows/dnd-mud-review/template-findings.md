# Template findings — review

## Формат

```markdown
## Findings — `<branch>` (base: `<base>`)

| Severity | Location | Issue |
|----------|----------|-------|
| Blocker | `file:line` | … |
| Major | `file:line` | … |
| Minor | `file:line` | … |
| Nit | `file:line` | … |
```

## Действия после review

| Findings | Действие |
|----------|----------|
| Blocker или Major | Предложить [`dnd-mud-fix-plan`](dnd-mud-fix-plan.md) |
| Только Minor | Предложить fix-plan одной строкой (опционально) |
| Только Nit или нет findings | Skill **не предлагать** |

## Light re-check (после fix Blocker)

Без subagent, без повторного `make verify-scope` (если fix точечный):

1. `git diff` по исправленным файлам
2. Blocker устранены
3. Full bugbot — только по запросу

## Severity guide

- **Blocker** — ломает фичу, критический баг, нарушение политики (git, verify)
- **Major** — заметный дефект, риск регрессии, нарушение KISS/DRY
- **Minor** — стиль, документация, мелкие улучшения
- **Nit** — опциональные замечания, не блокирующие merge
