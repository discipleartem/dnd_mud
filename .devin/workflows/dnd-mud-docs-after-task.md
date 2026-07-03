---
description: >-
  Обновляет docs в docs/ после завершения реализации задачи, перед commit
  финализации. Auto-commit на task-ветке. Перед verify/review. Когда задача
  только docs — пропустить.
---

# dnd_mud — документация после задачи

Канон: global Task cycle · [`AGENTS.md`](../../AGENTS.md) §Steps. Политика verify: [`dnd-mud-workflow.md`](../rules/dnd-mud-workflow.md) §Verify / review.

## Когда выполнять

После **завершения реализации** (подзадачи, слияние веток по плану), **перед** commit финализации и [`dnd-mud-review`](dnd-mud-review.md).

## Когда пропустить

- Задача была **только** про `docs/` или `.devin/rules/` (без предшествующего коммита реализации)
- Косметика / рефакторинг без смены поведения, API или данных
- Документация уже актуальна и diff после шага 2 пустой

## Алгоритм

1. По `git diff` (working tree, staged; при необходимости `origin/dev...HEAD`) определить затронутые области.
2. Обновить **только** релевантные файлы из таблицы ниже — факты, не дублирование.
3. **Commit финализации** — после шагов 1–2, по global Commit procedure:
   - на task-ветке commit **auto** (global Commits; project local overrides user «commit по запросу»)
   - незакоммиченный код + docs: один коммит `feat:`/`fix:`/… (docs в том же коммите), если уместно; иначе сначала код, затем `docs:`
   - код уже в подзадачах, изменились только docs: `docs: <краткое описание>` (Conventional Commits, английский)
   - не коммитить `.coverage`, `saves/` ([`dnd-mud-workflow.md`](../rules/dnd-mud-workflow.md) §Git)
   - если diff пустой — commit пропустить
4. Перейти к [`dnd-mud-review`](dnd-mud-review.md) (**один раз** на task-ветку).

## Какой файл обновлять

| Изменения | Документ |
|-----------|----------|
| Публичные функции, модули `core/`, контракты | `docs/API.md` |
| Слои, потоки данных, новые модули | `docs/ARCHITECTURE.md` |
| D&D-механика, правила игры | `docs/DND_RULES.md`, `docs/rules/*.md` |
| Продуктовые требования, scope | `docs/MUD_PRD.md` |
| Заметные фичи / фиксы для пользователей | `docs/CHANGELOG.md` |
| Workflow разработки, команды | `docs/DEVELOPMENT.md`, `.devin/rules/dnd-mud-workflow.md` |
| Python-версия, tooling | `.devin/rules/dnd-mud-python.md` |

Индекс: [`00-project.md`](../rules/00-project.md) §Docs.

## Принципы

- Минимальный diff: только изменившиеся факты
- Не копировать код в docs — ссылка на модуль/функцию достаточно
- **Не фиксировать** точное число тестов или файлов в docs/rules — при необходимости: `pytest --collect-only -q`, `git diff --shortstat`, или описание без цифр
