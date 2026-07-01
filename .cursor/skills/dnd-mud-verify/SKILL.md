---
name: dnd-mud-verify
description: >-
  Справочник команд verify (changed / scope / full). Агент на task-ветке НЕ
  вызывает scope/full вручную — только pre-commit verify-changed. Полный прогон
  один раз в dnd-mud-review в конце задачи. По явному запросу пользователя или CI.
disable-model-invocation: true
---

# dnd_mud — verify (справочник команд)

Канон-политика: [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Verify / review · [`AGENTS.md`](../../AGENTS.md).

## Когда агент вызывает этот skill

| Ситуация | Действие агента |
|----------|-----------------|
| Подзадача / commit на task-ветке | **Не вызывать.** Полагаться на pre-commit → `make verify-changed` (staged `.py` only) |
| Конец task-ветки | **Не вызывать отдельно.** Полный прогон — шаг внутри [`dnd-mud-review`](../dnd-mud-review/SKILL.md) |
| Пользователь явно просит `make test` / `make verify` | Выполнить запрошенную команду |
| CI / release `dev`→`main` | См. [`dnd-mud-release`](../dnd-mud-release/SKILL.md) |

**Запрещено агенту на task-ветке между подзадачами:** `make test`, `make test-fast`, `make check`, `make verify`, `make verify-scope`, полный `pytest` без фильтра по staged/diff.

## Три уровня (справочник)

| Уровень | Команда | Кто запускает |
|---------|---------|---------------|
| **changed** | `make verify-changed` | pre-commit при commit; агент — не дублировать |
| **scope** | `make verify-scope` | **один раз** в [`dnd-mud-review`](../dnd-mud-review/SKILL.md) |
| **full** | `make verify` (= `make check` + `make test`) | CI на PR; release — по skill |

Маппинг: [`scripts/verify_targets.py`](../../scripts/verify_targets.py).

## Команды (из `.venv`)

```bash
source .venv/bin/activate
which python   # must point to .venv/bin/python
```

| Команда | Diff / scope |
|---------|----------------|
| `make verify-changed` | staged `.py` |
| `make verify-scope` | `origin/dev...HEAD` (на `dev`: `VERIFY_BASE=origin/main`) |
| `make verify` | full check + full test |
| `python main.py` | smoke меню (если UI в diff — в review) |

Число тестов в отчётах — `pytest --collect-only -q`, не из docs.

## Пропуск runtime

Только `docs/`, `.cursor/rules`, `AGENTS.md`, workflows — без изменений кода/данных: `verify-scope` в review можно пропустить.
