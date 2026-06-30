---
name: dnd-mud-docs-after-task
description: >-
  Updates dnd_mud project docs in docs/ after the main implementation commit,
  then commits docs automatically (docs: …). Use when finishing a feature task,
  before verify, or when the user asks to sync documentation with code changes.
---

# dnd_mud — документация после задачи

Канон-политика: [`00-global.mdc`](~/.cursor/rules/00-global.mdc) §Документация после задачи · шаг 3 [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle.

**Запуск skill (`/dnd-mud-docs-after-task`) = явное разрешение на коммит docs** (отдельный `docs: …`), даже если в сессии действует общее правило «коммит только по запросу».

## Когда выполнять

После коммита **основной** реализации (не git-старт), **до** verify.

## Когда пропустить

- Задача была **только** про `docs/` или `.cursor/rules/` (без предшествующего коммита реализации) — skill не запускают; docs-коммит по обычному запросу пользователя
- Косметика / рефакторинг без смены поведения, API или данных
- Документация уже обновлена в том же коммите, что и код — шаги 2–3 не нужны

## Алгоритм

1. По `git diff` (или списку изменённых файлов) определить затронутые области.
2. Обновить **только** релевантные файлы из таблицы ниже — факты, не дублирование.
3. **Обязательный коммит** — если после шага 2 есть незакоммиченные правки в `docs/`, `.cursor/rules/` (индекс docs), `README.md`, `AGENTS.md` (только если менялся вместе с docs):
   - сообщение: `docs: <краткое описание>` (Conventional Commits, английский)
   - процедура: [`user-protocols.mdc`](~/.cursor/rules/user-protocols.mdc) §Commit procedure
   - не коммитить `.coverage`, `saves/`
   - если diff пустой — коммит пропустить
4. Перейти к skill `dnd-mud-verify` → затем `dnd-mud-review` (см. [`AGENTS.md`](../../AGENTS.md) §6–6.5).

## Коммит (шаг 3 — детали)

Параллельно: `git status`, `git diff`, `git log -5` (стиль сообщений).

Stage только файлы документации из шага 2 (+ `CHANGELOG.md`, если затронут). HEREDOC для сообщения. После коммита — `git status`.

Не смешивать docs-коммит с кодом реализации.

## Какой файл обновлять

| Изменения | Документ |
|-----------|----------|
| Публичные функции, модули `core/`, контракты | `docs/API.md` |
| Слои, потоки данных, новые модули | `docs/ARCHITECTURE.md` |
| D&D-механика, правила игры | `docs/DND_RULES.md`, `docs/rules/*.md` |
| Продуктовые требования, scope | `docs/MUD_PRD.md` |
| Заметные фичи / фиксы для пользователей | `docs/CHANGELOG.md` |
| Workflow разработки, команды | `docs/DEVELOPMENT.md`, `.cursor/rules/dnd-mud-git.mdc` |
| Python-версия, tooling | `.cursor/rules/dnd-mud-python-312.mdc` |

Индекс: [`00-project.mdc`](.cursor/rules/00-project.mdc) §Docs.

## Принципы

- Минимальный diff: только изменившиеся факты
- Не копировать код в docs — ссылка на модуль/функцию достаточно
- Доменные правила (`docs/rules/`) — если менялась механика или UX выбора
