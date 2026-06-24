# Agent rules — dnd_mud

**Канон:** [`.cursor/rules/00-project.mdc`](.cursor/rules/00-project.mdc) · global [`~/.cursor/rules/00-global.mdc`](~/.cursor/rules/00-global.mdc)

**Принцип:** простой код (`dnd-mud-python-simple.mdc`) · минимум тестов (`dnd-mud-tests.mdc`) · verify (`dnd-mud-verify.mdc`)

**Docs:** [`00-project.mdc`](.cursor/rules/00-project.mdc) §Docs · [`docs/API.md`](docs/API.md)

## Agent-loop

```
анализ → план → действие → verify → краткое объяснение
```

### 1. Понять задачу

Запрос + история диалога → режим (Ask / Agent) → ограничения (git, venv, verify, язык). Неясно — спросить.

### 2. Собрать контекст (readonly)

Порядок чтения правил (при конфликте **локальные переопределяют глобальные**):

| # | Источник | Что |
|---|----------|-----|
| 1 | **Глобальные правила** | User Rules (Cursor Settings) ≡ `~/.cursor/rules/` |
| 2 | **Локальные правила** | `<repo>/.cursor/rules/` (приоритетнее глобальных) |
| 3 | **AGENTS.md** | этот файл — индекс и loop проекта |
| 4 | **Skills** | `~/.cursor/skills-cursor/`, `~/.agents/skills/` — если релевантны задаче |

Затем: код (затронутые файлы, `grep`, search) · соглашения (стиль соседнего кода, слои `ui → core → database`) · git (ветка, diff; commit/push — только по запросу).

### 3–5. План · реализация · verify

См. [`00-global.mdc`](~/.cursor/rules/00-global.mdc) §Cursor modes, [`dnd-mud-python-simple.mdc`](.cursor/rules/dnd-mud-python-simple.mdc), [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc).
