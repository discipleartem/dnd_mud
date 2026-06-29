---
name: dnd-mud-docs-after-task
description: >-
  Updates dnd_mud project docs in docs/ after the main implementation commit.
  Use when finishing a feature task, before verify, or when the user asks to
  sync documentation with code changes.
---

# dnd_mud — документация после задачи

Канон-политика: [`00-global.mdc`](~/.cursor/rules/00-global.mdc) §Документация после задачи · шаг 3 [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle.

## Когда выполнять

После коммита **основной** реализации (не git-старт), **до** verify.

## Когда пропустить

- Задача была только про `docs/` или `.cursor/rules/`
- Косметика / рефакторинг без смены поведения, API или данных
- Документация уже обновлена в том же коммите, что и код

## Алгоритм

1. По `git diff` (или списку изменённых файлов) определить затронутые области.
2. Обновить **только** релевантные файлы из таблицы ниже — факты, не дублирование.
3. Если правки не вошли в коммит реализации — отдельный коммит: `docs: <краткое описание>`.
4. Перейти к skill `dnd-mud-verify` или verify по [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc).

## Какой файл обновлять

| Изменения | Документ |
|-----------|----------|
| Публичные функции, модули `core/`, контракты | `docs/API.md` |
| Слои, потоки данных, новые модули | `docs/ARCHITECTURE.md` |
| D&D-механика, правила игры | `docs/DND_RULES.md`, `docs/rules/*.md` |
| Продуктовые требования, scope | `docs/MUD_PRD.md` |
| Заметные фичи / фиксы для пользователей | `docs/CHANGELOG.md` |
| Workflow разработки, команды | `docs/DEVELOPMENT.md` |
| Python-версия, tooling | `docs/PYTHON_312.md` |

Индекс: [`00-project.mdc`](.cursor/rules/00-project.mdc) §Docs.

## Принципы

- Минимальный diff: только изменившиеся факты
- Не копировать код в docs — ссылка на модуль/функцию достаточно
- Доменные правила (`docs/rules/`) — если менялась механика или UX выбора
