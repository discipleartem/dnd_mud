# Agent rules — dnd_mud

**Канон:** [`.cursor/rules/00-project.mdc`](.cursor/rules/00-project.mdc) · global [`~/.cursor/rules/00-global.mdc`](~/.cursor/rules/00-global.mdc)

**Принцип:** простой код (`dnd-mud-python-simple.mdc`) · минимум тестов (`dnd-mud-tests.mdc`) · verify (`dnd-mud-verify.mdc`)

**Docs:** [`00-project.mdc`](.cursor/rules/00-project.mdc) §Docs · [`docs/API.md`](docs/API.md)

## Agent-loop

**Обычная сессия (Agent напрямую):**

```
анализ → план → действие → verify → краткое объяснение
```

**Сессия Plan → Build → Agent** (план подтверждён, «Implement the plan» / прикреплён `.plan.md`):

```
Plan (readonly) → Build → git-старт → реализация → verify → commit → push
```

Канон: [`00-global.mdc`](~/.cursor/rules/00-global.mdc) §Cursor modes · git: [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle.

| Этап | Что делать |
|------|------------|
| Plan | Исследование, `CreatePlan`. Без правок кода и git. |
| Build | Пользователь подтверждает план → переход в Agent. |
| **git-старт** | **Первое действие в Agent** — до `Write` / `StrReplace` / `Delete`: `git fetch`, sync `main`/`dev`, task-ветка от `dev`. |
| Реализация | Код по плану; auto-commit на task-ветке; push в конце — обязателен. |

> Слово «план» в обычном loop — этап проектирования в голове, **не** режим Cursor Plan.

### 1. Понять задачу

Запрос + история диалога → режим (Ask / Plan / Agent) → ограничения (git, venv, verify, язык). Неясно — спросить.

**Plan → Build?** Признаки: `CreatePlan`, прикреплённый `.plan.md`, «реализуй план» после Build → включить Task cycle; commit/push на task-ветке **обязательны** (переопределяет «коммит только по запросу» для этой сессии).

### 2. Собрать контекст (readonly)

Порядок чтения правил (при конфликте **локальные переопределяют глобальные**):

| # | Источник | Что |
|---|----------|-----|
| 1 | **Глобальные правила** | User Rules (Cursor Settings) ≡ `~/.cursor/rules/` |
| 2 | **Локальные правила** | `<repo>/.cursor/rules/` (приоритетнее глобальных) |
| 3 | **AGENTS.md** | этот файл — индекс и loop проекта |
| 4 | **Skills** | `~/.cursor/skills-cursor/`, `~/.agents/skills/` — если релевантны задаче |

Затем: код (затронутые файлы, `grep`, search) · соглашения (стиль соседнего кода, слои `ui → core → database`) · git (ветка, diff).

- **Plan → Build → Agent:** git-старт **до** правок кода (см. таблицу выше); commit/push на task-ветке — по Task cycle.
- **Agent напрямую:** commit/push — только по запросу пользователя.

### 3. Plan → Build: git-старт (обязательно первым)

До любых правок кода выполнить [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаги 1–2:

```bash
git fetch origin
git checkout main && git pull origin main
git checkout dev && git pull origin dev
git log dev..origin/main --oneline   # пусто; иначе merge origin/main в dev и push
git checkout -b <task-branch>        # от dev, kebab-case
```

Незакоммиченные изменения: `git stash` → git-старт → `git stash pop` на task-ветке.

### 4–6. Реализация · verify · завершение

См. [`dnd-mud-python-simple.mdc`](.cursor/rules/dnd-mud-python-simple.mdc), [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc).
