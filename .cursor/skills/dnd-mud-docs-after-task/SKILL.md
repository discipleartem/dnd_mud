---
name: dnd-mud-docs-after-task
description: >-
  Обновляет docs в docs/ после завершения реализации задачи, перед commit
  финализации. Auto-commit на task-ветке. Перед verify/review. Когда задача
  только docs/rules — пропустить.
---

# dnd_mud — документация после задачи

Канон: [`task-cycle.mdc`](~/.cursor/rules/task-cycle.mdc) ш.3 · [`AGENTS.md`](../../AGENTS.md) §Steps. Политика verify: [`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Verify / review.

## Когда выполнять

После **завершения реализации** (подзадачи, слияние веток по плану), **перед** commit финализации и [`dnd-mud-review`](../dnd-mud-review/SKILL.md).

## Когда пропустить

- Задача была **только** про `docs/` или `.cursor/rules/` (без предшествующего коммита реализации)
- Косметика / рефакторинг без смены поведения, API или данных
- Документация уже актуальна и diff после шага 2 пустой

## Алгоритм

1. По `git diff` (working tree, staged; при необходимости `origin/dev...HEAD`) определить затронутые области.
2. Обновить **только** релевантные файлы из таблицы ниже — факты, не дублирование.
3. **Commit финализации** — после шагов 1–2, по [`git.mdc`](~/.cursor/rules/git.mdc) §Commit procedure:
   - на task-ветке commit **auto** ([`git.mdc`](~/.cursor/rules/git.mdc) §Commits; project local overrides user «commit по запросу»)
   - незакоммиченный код + docs: один коммит `feat:`/`fix:`/… (docs в том же коммите), если уместно; иначе сначала код, затем `docs:`
   - код уже в подзадачах, изменились только docs: `docs: <краткое описание>` (Conventional Commits, английский)
   - не коммитить `.coverage`, `saves/` ([`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) Overrides / Git scope)
   - если diff пустой — commit пропустить
4. Перейти к [`dnd-mud-review`](../dnd-mud-review/SKILL.md) (**один раз** на task-ветку).

## Какой файл обновлять

| Изменения | Документ |
|-----------|----------|
| Публичные функции, модули `core/`, контракты | `docs/API.md` |
| Слои, потоки данных, новые модули | `docs/ARCHITECTURE.md` |
| D&D-механика, правила игры | `docs/DND_RULES.md`, `docs/rules/*.md` |
| Продуктовые требования, scope | `docs/MUD_PRD.md` |
| Заметные фичи / фиксы для пользователей | `docs/CHANGELOG.md` |
| Workflow разработки, команды | `docs/DEVELOPMENT.md`, `.cursor/rules/dnd-mud-workflow.mdc` |
| Python-версия, tooling | `.cursor/rules/dnd-mud-python.mdc` |

Индекс: [`00-project.mdc`](../../rules/00-project.mdc) §Docs.

## Принципы

- Минимальный diff: только изменившиеся факты
- Не копировать код в docs — ссылка на модуль/функцию достаточно
- **Не фиксировать** точное число тестов или файлов в docs/rules — при необходимости: `pytest --collect-only -q`, `git diff --shortstat`, или описание без цифр
