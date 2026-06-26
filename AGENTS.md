# Agent rules — dnd_mud

**Канон:** [`.cursor/rules/00-project.mdc`](.cursor/rules/00-project.mdc) · global [`~/.cursor/rules/00-global.mdc`](~/.cursor/rules/00-global.mdc)

**Принцип:** простой код (`dnd-mud-python-simple.mdc`) · минимум тестов (`dnd-mud-tests.mdc`) · verify (`dnd-mud-verify.mdc`)

**Docs:** [`00-project.mdc`](.cursor/rules/00-project.mdc) §Docs · [`docs/API.md`](docs/API.md)

## Agent-loop

**Обычная сессия (Agent напрямую):**

```
анализ → git-старт → план → действие → verify → PR (по запросу)
```

> **Project override:** в dnd_mud git-старт обязателен всегда (строже глобального «Agent напрямую — git-flow не обязателен»). См. [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc) §Переопределения.

**Сессия Plan → Build → Agent** (план подтверждён, «Implement the plan» / прикреплён `.plan.md`):

```
Plan (readonly) → Build → git-старт → реализация → verify → commit → push → PR
```

Канон: [`00-global.mdc`](~/.cursor/rules/00-global.mdc) §Cursor modes · git: [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle.

| Этап | Что делать |
|------|------------|
| Plan | Исследование, `CreatePlan`. Без правок кода и git. |
| Build | Пользователь подтверждает план → переход в Agent. |
| **git-старт** | **Первое действие** — до правок кода: sync `main`/`dev`, task-ветка от `dev`. |
| Реализация | Подзадачи → atomic commits; verify в конце. |
| Завершение | push task-ветки → предложить PR task → `dev`; release — PR `dev` → `main`. |

> Слово «план» в обычном loop — этап проектирования в голове, **не** режим Cursor Plan.

### 1. Понять задачу

Запрос + история → режим (Ask / Plan / Agent) → ограничения (git, venv, verify, язык).

**Plan → Build?** `CreatePlan`, `.plan.md`, «реализуй план» → Task cycle; commit/push на task-ветке **обязательны**.

### 2. Собрать контекст (readonly)

Порядок: глобальные правила → `.cursor/rules/` → этот файл → skills → код/docs.

### 3. Git-старт (перед правками кода)

Для **любой** задачи с изменением кода/docs/git — **до** `Write` / `StrReplace` / `Delete`:

```bash
git fetch origin
git checkout main && git pull origin main
git checkout dev && git pull origin dev
git log dev..origin/main --oneline   # must be empty
```

Если **не пусто** (`main` впереди `dev`):

```bash
git merge origin/main
make test                            # если затронут код
git push origin dev
```

Task-ветка (kebab-case, от актуального `dev`):

```bash
git checkout -b feat/my-task
```

**Запрещено:** task-ветка от `dev`, который отстаёт от `main`.

Незакоммиченные изменения: `git stash` → git-старт → `git stash pop` на task-ветке.

IDE: расширения **GitHub Pull Requests** и **GitHub Actions**; squash merge — [`.vscode/settings.json`](.vscode/settings.json).

### 4. Подзадачи и коммиты

- Главная задача → **подзадачи**; **один atomic commit на подзадачу** (Conventional Commits).
- Plan → Build → Agent: auto-commit на task-ветке обязателен.
- Agent напрямую: commit/push — по запросу пользователя.

### 5. Завершение главной задачи (task-ветка)

1. `make test` (и `make check` при типах/импортах).
2. `git push -u origin HEAD`.
3. **Предложить PR** task → `dev` (squash merge):

```bash
gh pr create --base dev --title "feat: …"
```

Панель **GitHub Pull Requests** → фильтр «Task → dev».

### 6. Release (`dev` → `main`)

Перед PR **проверить** (дублирует CI [`pr-dev-to-main-check.yml`](.github/workflows/pr-dev-to-main-check.yml)):

```bash
git fetch origin
git checkout dev && git pull origin dev
git log dev..origin/main --oneline          # must be empty
git merge origin/main --no-commit --no-ff   # пробный merge; git merge --abort если ok
make test
gh pr create --base main --head dev --title "release: …"
```

Панель **GitHub Pull Requests** → фильтр «Release dev → main».

После squash merge в `main`:

- Action [**Sync dev with main**](.github/workflows/sync-dev-with-main.yml) подтягивает `main` → `dev`.
- При падении Action — вручную: `git checkout dev && git merge origin/main && git push origin dev` ([`git-dev-main-sync.md`](~/.cursor/docs/git-dev-main-sync.md)).

### 7. Verify

См. [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc).
