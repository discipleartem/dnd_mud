---
name: dnd-mud-docs-after-task
description: >-
  Updates dnd_mud project docs in docs/ after the main implementation commit,
  then commits docs automatically (docs: …). Use when finishing a feature task,
  before verify, or when the user asks to sync documentation with code changes.
---

# dnd_mud — документация после задачи

Канон: [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаг 3.

## Когда выполнять

После коммита **основной** реализации (не git-старт), **до** verify.

## Когда пропустить

- Задача была **только** про `docs/` или `.cursor/rules/` (без предшествующего коммита реализации)
- Косметика / рефакторинг без смены поведения, API или данных
- Документация уже обновлена в том же коммите, что и код

## Алгоритм

1. По `git diff` определить затронутые области.
2. Обновить **только** релевантные файлы из таблицы ниже — факты, не дублирование.
3. **Коммит** — если после шага 2 есть незакоммиченные правки в `docs/`, `.cursor/rules/`, `README.md`, `AGENTS.md`:
   - сообщение: `docs: <краткое описание>` (Conventional Commits, английский)
   - процедура: [`user-protocols.mdc`](~/.cursor/rules/user-protocols.mdc) §Commit procedure
   - не коммитить `.coverage`, `saves/` ([`dnd-mud-workflow.mdc`](../../rules/dnd-mud-workflow.mdc) §Git)
   - если diff пустой — коммит пропустить
4. Перейти к skill `dnd-mud-verify` → `dnd-mud-review`.

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
