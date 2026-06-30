---
name: dnd-mud-verify
description: >-
  Runs dnd_mud verification (verify-changed / verify-scope / full via CI).
  Use after subtasks, at end of task branch, before push/PR, or when asked.
disable-model-invocation: true
---

# dnd_mud — verify

Канон: [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc). Браузер **запрещён** — только консоль.

## Три уровня verify

| Уровень | Когда | Команда |
|---------|-------|---------|
| **changed** | После подзадачи, pre-commit | `make verify-changed` |
| **scope** | Конец task-ветки, после rebase/merge | `make verify-scope` |
| **full** | CI на PR; опционально локально | `make verify` (= `make check` + `make test`) |

Маппинг changed/scope → pytest/lint: [`scripts/verify_targets.py`](../../scripts/verify_targets.py).

## Когда выполнять

- **Подзадача:** `make verify-changed` после правок (или полагается на pre-commit).
- **Конец task-ветки:** один раз **после** docs (skill `dnd-mud-docs-after-task`), **перед** review — `make verify-scope`.
- **Full локально** — по желанию перед push; **обязателен** в CI ([`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)) на PR в `dev` / `main`.

## Предусловия

- [ ] git-старт был в начале сессии ([`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Git)
- [ ] Коммиты подзадач сделаны
- [ ] Документация обновлена (или пропущена по правилам)

## Команды (из `.venv`)

```bash
source .venv/bin/activate
which python   # must point to .venv/bin/python
```

| Условие | Команда |
|---------|---------|
| Подзадача (staged .py) | `make verify-changed` |
| Конец задачи (diff `origin/dev...HEAD`) | `make verify-scope` |
| Затронут UI (`ui/`, меню) | `python main.py` — smoke затронутого меню |
| Полный прогон (CI / вручную) | `make verify` |

**Пропустить runtime**, если только docs, `.cursor/`, `AGENTS.md`, workflows — без изменений кода.

## Чеклист Before finishing

- [ ] `make verify-scope` прошёл (если был код)
- [ ] Smoke пройден (если UI)
- [ ] Перейти к skill [`dnd-mud-review`](../dnd-mud-review/SKILL.md) — review **не** заменяет CI full test
