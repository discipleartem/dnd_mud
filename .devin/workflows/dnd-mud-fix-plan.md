---
description: >-
  Readonly план исправлений по findings из dnd-mud-review: приоритет, файлы,
  границы коммитов. Запуск после Blocker/Major или по запросу. Не правит код
  и не коммитит.
---

# dnd_mud — fix plan (план исправлений после review)

Канон: [`AGENTS.md`](../../AGENTS.md) · [`dnd-mud-workflow.md`](../rules/dnd-mud-workflow.md) §Verify / review · после [`dnd-mud-review`](dnd-mud-review.md).

**Fix plan** — readonly: структурированный план **без** правок кода, commit и push.  
Реализация — в Agent mode по запросу пользователя («исправь по плану», «исправь blockers»).

## Когда выполнять

| Триггер | Действие |
|---------|----------|
| После `dnd-mud-review` с **Blocker** или **Major** | Оркестратор review **предлагает** `/dnd-mud-fix-plan` (не auto-fix) |
| После review только с **Minor** | Предложить workflow **одной строкой** (опционально) |
| Только **Nit** или **нет findings** | Workflow **не предлагать** |
| Явный запрос `/dnd-mud-fix-plan` | Выполнить всегда (если есть findings или пользователь приложил таблицу) |

**Не** запускать автоматически после каждого review. **Не** переключать Plan Mode программно — для крупного набора Major предложить пользователю Plan mode вручную.

## Предусловия

- [ ] Выполнен [`dnd-mud-review`](dnd-mud-review.md) — light, full или light re-check (или пользователь приложил таблицу findings)
- [ ] Известны ветка и base branch review (`dev` / `main`)
- [ ] Рабочее дерево чистое (или явно указано, что план включает незакоммиченные правки)

## Входные данные

1. Таблицы findings — [template-findings.md](dnd-mud-review/template-findings.md)
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
   - verify после пункта: pre-commit `verify-changed` only (policy — workflow §На task-ветке)
4. Границы коммитов: atomic; не смешивать unrelated (код vs docs vs `.devin/`).
5. Финальный блок **After fixes**:
   - **light re-check** — [`dnd-mud-review`](dnd-mud-review.md) §Light re-check
   - повторный full `verify-scope` / bugbot — только по запросу
   - push/PR — [`dnd-mud-git-pr`](dnd-mud-git-pr.md) по запросу
6. **Не** править код, **не** `git commit`, **не** push.

## Формат выхода

```markdown
## Remediation plan — `<branch>` (base: `<base>`)

### Must fix before push
1. [Blocker|Major] `<location>` — <краткое описание>
   - Files: …
   - Commit: `fix: …` / `docs: …`
   - Verify: `make verify-changed` [; smoke …]

### Optional
2. [Minor] …

### Out of scope (defer) — Nit

Отдельный подраздел; пункты из таблицы **Nit (опционально)** review (не дублировать в Must/Optional):

- [Nit] `<location>` — …

### After fixes
- [ ] light re-check ([`dnd-mud-review`](dnd-mud-review.md) §Light re-check) — при Blocker в must-fix
- [ ] push/PR — по запросу; полный pytest — CI на PR
```

Язык: русский; пути и идентификаторы — English.

## Plan Mode (опционально)

Если **≥3 Major** или затронуты несколько слоёв (core + database + ui + docs) — в конце плана добавить:

> Для согласования большого объёма правок можно переключиться в **Plan mode**, подтвердить план и затем «реализуй план» в Agent.

Для 1–2 Minor достаточно плана в Agent (readonly).
