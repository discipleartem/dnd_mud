# dnd_mud — verify commands (reference)

Политика: [`dnd-mud-workflow.md`](../../rules/dnd-mud-workflow.md) §Verify / review.

## Три уровня

| Уровень | Команда | Кто запускает |
|---------|---------|---------------|
| **changed** | `make verify-changed` | pre-commit при commit; агент — не дублировать |
| **scope** | `make verify-scope` | **один раз** в [`dnd-mud-review`](../dnd-mud-review.md) |
| **full** | `make verify` (= `make check` + `make test`) | CI на PR; release — [`dnd-mud-release`](../dnd-mud-release.md) |

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

Только `docs/`, `.devin/rules`, `AGENTS.md`, workflows — без изменений кода/данных: `verify-scope` в review можно пропустить (см. workflow §Пропуск verify-scope).
