# Agent rules — dnd_mud

**Канон:** [`.cursor/rules/00-project.mdc`](.cursor/rules/00-project.mdc) · global [`00-global.mdc`](~/.cursor/rules/00-global.mdc) · git [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) · verify [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc)

**Приоритет при конфликте:** project local (этот файл, `.cursor/rules/`) → User Rules / global. User Rules: [`user-rules-minimal.md`](~/.cursor/docs/user-rules-minimal.md).

**Принцип:** простой код (`dnd-mud-python-simple.mdc`) · минимум тестов (`dnd-mud-tests.mdc`)

**Docs:** [`00-project.mdc`](.cursor/rules/00-project.mdc) §Docs · [`docs/API.md`](docs/API.md)

## Agent-loop

| Режим | Цикл |
|-------|------|
| Agent напрямую | анализ → git-старт → план → действие → commit → **docs** → verify → **review** → PR (по запросу) |
| Plan → Build → Agent | см. [`00-global.mdc`](~/.cursor/rules/00-global.mdc) §Cursor modes |

**Project overrides:** [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc) §Переопределения (git-старт всегда; verify без браузера).

> Слово «план» в обычном loop — этап проектирования в голове, **не** режим Cursor Plan.

### 1. Понять задачу

Запрос + история → режим (Ask / Plan / Agent) → ограничения (git, venv, verify, язык).

**venv:** любые bash-команды проекта (`make`, `python`, `pytest`, `pip`) — только из активированного `.venv` ([`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Virtual environment).

**Plan → Build?** `CreatePlan`, `.plan.md`, «реализуй план» → [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle; commit/push на task-ветке **обязательны**.

### 2. Собрать контекст (readonly)

Порядок: глобальные правила → `.cursor/rules/` → этот файл → [`.cursor/skills/`](.cursor/skills/) → код/docs.

### 3. Git-старт

Канон: [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаг 1.

**Дополнительно для dnd_mud:**

- при merge `origin/main` в `dev` — `make test`, если затронут код; процедура — skill `git-dev-main-sync`
- IDE: расширения **GitHub Pull Requests** и **GitHub Actions**; squash merge — [`.vscode/settings.json`](.vscode/settings.json)

### 4. Подзадачи и коммиты

Канон: [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаг 2, §Commits.

**Коммиты** — автоматически после каждой подзадачи и в конце реализации (если остались правки).  
**Agent напрямую:** push и PR — по запросу пользователя.

### 5. Документация

Канон: [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаг 3 · skill [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) (после правок — **автокоммит** `docs: …`).

После коммита основной задачи — обновить `docs/` по факту изменений; отдельный коммит `docs: …`, если docs не вошли в коммит реализации.

### 6. Verify

Канон: [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc) §Verify · skill [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md).

Один раз в конце (не после каждого файла): `make test` / `make check` / smoke `python main.py` по условиям.

### 6.5 Review

Канон: skill [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md). Readonly Bugbot vs **`dev`** (task-ветка) или **`main`** (release).

**Обязательно после verify, до** `git push`, `gh pr create`, `git merge`, интегрирующего код в `dev`/`main`.

Пропуск: только docs/rules без кода и данных; явный запрос пользователя без review.

Blockers → fix → verify → один повтор review. Push/PR — после чистого review или по запросу (non-blocker).

### 7. Завершение task-ветки

1. Verify (шаг 6) и review (шаг 6.5) выполнены
2. Push и PR — [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаги 5–6
3. **Plan → Build → Agent:** push обязателен; предложить PR → `dev`
4. **Agent напрямую:** push — по запросу; после push — предложить PR → `dev`

Панель **GitHub Pull Requests** → фильтр «Task → dev».

### 8. Release (`dev` → `main`)

Канон: [`dnd-mud-verify.mdc`](.cursor/rules/dnd-mud-verify.mdc) §Release · skill [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md).

Панель **GitHub Pull Requests** → фильтр «Release dev → main». Sync после merge — skill `git-dev-main-sync`.

## Skills (project)

| Skill | Когда |
|-------|-------|
| [`dnd-mud-docs-after-task`](.cursor/skills/dnd-mud-docs-after-task/SKILL.md) | После commit реализации, перед verify; **автокоммит** `docs: …` |
| [`dnd-mud-verify`](.cursor/skills/dnd-mud-verify/SKILL.md) | После docs, перед review |
| [`dnd-mud-review`](.cursor/skills/dnd-mud-review/SKILL.md) | После verify, **до** push / PR / merge |
| [`dnd-mud-release`](.cursor/skills/dnd-mud-release/SKILL.md) | Release PR `dev` → `main` (после review vs `main`) |

Personal: `git-dev-main-sync` (`~/.cursor/skills/git-dev-main-sync/`) — sync `dev` с `main`.
