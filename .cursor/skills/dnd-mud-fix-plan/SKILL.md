---
name: dnd-mud-fix-plan
description: >-
  Readonly план исправлений по findings из dnd-mud-review: приоритет, файлы,
  границы коммитов, verify. Запуск после review при Major/Blocker или по запросу
  (/dnd-mud-fix-plan). Не правит код и не коммитит.
disable-model-invocation: true
---

# dnd_mud — fix plan (план исправлений после review)

Канон-политика: [`AGENTS.md`](../../AGENTS.md) · [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) · после [`dnd-mud-review`](../dnd-mud-review/SKILL.md).

**Fix plan** — readonly: структурированный план **без** правок кода, commit и push.  
Реализация — в Agent mode по запросу пользователя («исправь по плану», «исправь blockers»).

## Когда выполнять

| Триггер | Действие |
|---------|----------|
| После `dnd-mud-review` с **Blocker** или **Major** | Оркестратор review **предлагает** `/dnd-mud-fix-plan` (не auto-fix) |
| После review только с **Minor** | Предложить skill **одной строкой** (опционально) |
| Только **Nit** или **нет findings** | Skill **не предлагать** |
| Явный запрос `/dnd-mud-fix-plan` | Выполнить всегда (если есть findings или пользователь приложил таблицу) |

**Не** запускать автоматически после каждого review. **Не** переключать Plan Mode программно — для крупного набора Major предложить пользователю Plan mode вручную.

## Предусловия

- [ ] Выполнен [`dnd-mud-review`](../dnd-mud-review/SKILL.md) (или пользователь приложил таблицу findings)
- [ ] Известны ветка и base branch review (`dev` / `main`)
- [ ] Рабочее дерево чистое (или явно указано, что план включает незакоммиченные правки)

## Входные данные

1. Таблицы findings из review: **основная** (Blocker/Major/Minor) и **Nit (опционально)** — см. [`dnd-mud-review`](../dnd-mud-review/SKILL.md) §Формат ответа
2. Имя ветки (`git branch --show-current`)
3. Base branch review (`dev` по умолчанию)

Если таблицы нет в контексте — перечитать diff `git diff origin/<base>...HEAD --stat` и ключевые файлы из Location; не выдумывать findings.

## Алгоритм (оркестратор, readonly)

1. Отсортировать findings: Blocker → Major → Minor → Nit.
2. Разделить на группы:
   - **Must fix before push** — Blocker + Major (если пользователь не пометил Major как defer)
   - **Optional** — Minor
   - **Out of scope (defer)** — Nit и явно отложенное
3. Для каждого пункта must/optional указать:
   - файл(ы) и суть правки (1–2 предложения)
   - предлагаемый commit message (Conventional Commits, **why**)
   - verify после пункта или блока: `make check`, `make test`; smoke — если UI
4. Границы коммитов: atomic; не смешивать unrelated (код vs docs vs `.cursor/`).
5. Финальный блок **After fixes**:
   - verify один раз в конце блока must-fix
   - повтор [`dnd-mud-review`](../dnd-mud-review/SKILL.md) — **только** если были Blocker
   - push/PR — по запросу пользователя
6. **Не** править код, **не** `git commit`, **не** push.

## Формат выхода

```markdown
## Remediation plan — `<branch>` (base: `<base>`)

### Must fix before push
1. [Blocker|Major] `<location>` — <краткое описание>
   - Files: …
   - Commit: `fix: …` / `docs: …`
   - Verify: `make check` && `make test` [; smoke …]

### Optional
2. [Minor] …

### Out of scope (defer) — Nit

Отдельный подраздел; пункты из таблицы **Nit (опционально)** review (не дублировать в Must/Optional):

- [Nit] `<location>` — …

### After fixes
- [ ] verify (…)
- [ ] повтор dnd-mud-review — только при Blocker в must-fix
- [ ] push/PR — по запросу
```

Язык: русский; пути и идентификаторы — English.

## Связь с Agent-loop

```
… → verify → review → [fix-plan?] → fix (Agent) → verify → review (если blockers) → push
                      ↑
              Major+ или /dnd-mud-fix-plan
```

После выдачи плана — ждать явного запроса на реализацию.

## Plan Mode (опционально)

Если **≥3 Major** или затронуты несколько слоёв (core + database + ui + docs) — в конце плана добавить:

> Для согласования большого объёма правок можно переключиться в **Plan mode**, подтвердить план и затем «реализуй план» в Agent.

Для 1–2 Minor достаточно плана в Agent (readonly).
