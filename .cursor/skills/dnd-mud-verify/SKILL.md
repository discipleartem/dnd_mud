---
name: dnd-mud-verify
description: >-
  Справочник команд verify (changed / scope / full). Политика — dnd-mud-workflow
  §Verify/review. Агент на task-ветке не вызывает scope/full вручную. Читать
  reference.md при явном запросе пользователя, release или контексте команд.
disable-model-invocation: true
---

# dnd_mud — verify (справочник)

Политика: [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Verify / review.

## Когда читать reference

| Ситуация | Действие |
|----------|----------|
| Подзадача / commit на task-ветке | **Не вызывать.** Pre-commit → `make verify-changed` |
| Конец task-ветки | Процедура в [`dnd-mud-review`](../dnd-mud-review/SKILL.md) |
| Пользователь явно просит `make test` / `make verify` | Команды — [reference.md](reference.md) |
| Release `dev`→`main` | [`dnd-mud-release`](../dnd-mud-release/SKILL.md) + [reference.md](reference.md) |

Команды и таблицы уровней: **[reference.md](reference.md)**.
