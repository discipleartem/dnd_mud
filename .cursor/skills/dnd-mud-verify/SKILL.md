---
name: dnd-mud-verify
description: >-
  Runs dnd_mud verification checklist (make test, make check, python main.py smoke)
  once at end of task. Use before push/PR or when the user asks to verify changes.
disable-model-invocation: true
---

# dnd_mud — verify

Канон: [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc). Браузер **запрещён** — только консоль.

## Когда выполнять

Один раз в конце task-ветки, **после** docs (skill `dnd-mud-docs-after-task`), **перед** review (skill `dnd-mud-review`).

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
| Изменён код | `make test` — **обязательно** |
| Типы / импорты | `make check` |
| Затронут UI (`ui/`, меню) | `python main.py` — smoke затронутого меню |

**Пропустить runtime**, если только docs, `.cursor/`, `AGENTS.md`, workflows — без изменений кода.

## Чеклист Before finishing

- [ ] `make test` прошёл (если был код)
- [ ] `make check` прошёл (если нужен)
- [ ] Smoke пройден (если UI)
- [ ] Перейти к skill [`dnd-mud-review`](../dnd-mud-review/SKILL.md)
