# Agent rules — dnd_mud

**Канон:** [`.cursor/rules/00-project.mdc`](.cursor/rules/00-project.mdc) · global [`00-global.mdc`](~/.cursor/rules/00-global.mdc) · git [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) · verify [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc)

**Принцип:** простой код (`dnd-mud-python-simple.mdc`) · минимум тестов (`dnd-mud-tests.mdc`)

**Docs:** [`00-project.mdc`](.cursor/rules/00-project.mdc) §Docs · [`docs/API.md`](docs/API.md)

## Agent-loop

| Режим | Цикл |
|-------|------|
| Agent напрямую | анализ → git-старт → план → действие → verify → PR (по запросу) |
| Plan → Build → Agent | см. [`00-global.mdc`](~/.cursor/rules/00-global.mdc) §Cursor modes |

**Project overrides:** [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc) §Переопределения (git-старт всегда; verify без браузера).

> Слово «план» в обычном loop — этап проектирования в голове, **не** режим Cursor Plan.

### 1. Понять задачу

Запрос + история → режим (Ask / Plan / Agent) → ограничения (git, venv, verify, язык).

**venv:** любые bash-команды проекта (`make`, `python`, `pytest`, `pip`) — только из активированного `.venv` ([`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Virtual environment).

**Plan → Build?** `CreatePlan`, `.plan.md`, «реализуй план» → [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle; commit/push на task-ветке **обязательны**.

### 2. Собрать контекст (readonly)

Порядок: глобальные правила → `.cursor/rules/` → этот файл → skills → код/docs.

### 3. Git-старт

Канон: [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаг 1.

**Дополнительно для dnd_mud:**

- при merge `origin/main` в `dev` — `make test`, если затронут код
- IDE: расширения **GitHub Pull Requests** и **GitHub Actions**; squash merge — [`.vscode/settings.json`](.vscode/settings.json)

### 4. Подзадачи и коммиты

Канон: [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаг 2, §Commits.

**Коммиты** — автоматически после каждой подзадачи и в конце задачи (если остались правки).  
**Agent напрямую:** push и PR — по запросу пользователя.

### 5. Завершение task-ветки

1. Verify — [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc) §Verify, §Before finishing
2. Push и PR — [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаги 4–5

Панель **GitHub Pull Requests** → фильтр «Task → dev».

### 6. Release (`dev` → `main`)

Канон: [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc) §Release checklist, §GitHub Actions.

Панель **GitHub Pull Requests** → фильтр «Release dev → main».

### 7. Verify

Канон: [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc) §Verify.
