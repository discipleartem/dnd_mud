---
description: >-
  Справочник команд verify (changed / scope / full). Политика — dnd-mud-workflow
  §Verify/review. Агент на task-ветке не вызывает scope/full вручную. Читать
  reference.md при явном запросе пользователя, release или контексте команд.
---

# dnd_mud — verify (справочник)

Политика: [`dnd-mud-workflow.md`](../rules/dnd-mud-workflow.md) §Verify / review.

## Когда читать reference

| Ситуация | Действие |
|----------|----------|
| Подзадача / commit на task-ветке | **Не вызывать.** Pre-commit → `make verify-changed` |
| Конец task-ветки | Процедура в [`dnd-mud-review`](dnd-mud-review.md) |
| Пользователь явно просит `make test` / `make verify` | Команды — [reference.md](dnd-mud-verify/reference.md) |
| Release `dev`→`main` | [`dnd-mud-release`](dnd-mud-release.md) + [reference.md](dnd-mud-verify/reference.md) |

Команды и таблицы уровней: **[reference.md](dnd-mud-verify/reference.md)**.
