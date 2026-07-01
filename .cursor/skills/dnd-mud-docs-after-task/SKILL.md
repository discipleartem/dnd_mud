---
name: dnd-mud-docs-after-task
description: >-
  Updates dnd_mud project docs in docs/ after task implementation is complete,
  before the finalization commit, then commits (docs: … or together with code).
  Use when finishing a feature task, before verify, or when the user asks to sync
  documentation with code changes.
---

# dnd_mud — документация после задачи

Канон: [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle ш.3 · оркестрация [`AGENTS.md`](../../AGENTS.md) §Steps.

## Когда выполнять

После **завершения реализации** задачи (подзадачи, слияние веток по плану), **перед** commit финализации.

Промежуточные commits подзадач — pre-commit `verify-changed` only; **не** запускать `make verify-scope` / `make test` до [`dnd-mud-review`](../dnd-mud-review/SKILL.md).

## Когда пропустить

- Задача была **только** про `docs/` или `.cursor/rules/` (без предшествующего коммита реализации)
- Косметика / рефакторинг без смены поведения, API или данных
- Документация уже актуальна и diff после шага 2 пустой

## Алгоритм

1. По `git diff` (working tree, staged; при необходимости `origin/dev...HEAD`) определить затронутые области.
2. Обновить **только** релевантные файлы из таблицы ниже — факты, не дублирование.
3. **Commit финализации** — после шагов 1–2, по [`user-protocols.mdc`](~/.cursor/rules/user-protocols.mdc) §Commit procedure:
   - незакоммиченный код + docs: один коммит `feat:`/`fix:`/… (docs в том же коммите), если уместно; иначе сначала код, затем `docs:`
   - код уже в подзадачах, изменились только docs: `docs: <краткое описание>` (Conventional Commits, английский)
   - не коммитить `.coverage`, `saves/` ([`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Git)
   - если diff пустой — commit пропустить
4. Перейти к skill [`dnd-mud-review`](../dnd-mud-review/SKILL.md) (**один раз** на task-ветку).

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
